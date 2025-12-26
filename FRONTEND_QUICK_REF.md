# RootMind Frontend Quick Reference

## Component Structure

### App.tsx (Main)
- **State**: `ready`, `documentTitle`, `studyPlan`, `lastInfo`
- **Props**: None
- **Children**: Header, Upload, StudySidebar, Chat
- **Layout**: 4-col grid (sidebar: 1 col, main: 3 col)

### Upload.tsx
- **Props**: `onUploaded?: (info) => void`
- **State**: `status` ("idle" | "uploading" | "done" | "error"), `message`
- **Methods**: `handleFile`, `onChange`
- **API**: POST /upload, POST /study/metadata
- **Callback Data**: `{ chunks, persistDir, title, studyPlan }`

### Chat.tsx
- **Props**: `disabled?: boolean`, `documentTitle?: string`
- **State**: `messages`, `question`, `loading`, `error`
- **Message Type**: `{ role, content, sources? }`
- **Methods**: `send`
- **API**: POST /ask

### StudySidebar.tsx
- **Props**: `plan: StudyPlan[]`
- **State**: `expanded: boolean`
- **Display**: Collapsible sections with objectives

---

## Type Definitions

```typescript
// StudyPlan (shared across components)
type StudyPlan = {
  section: string;
  objective: string;
};

// Message in Chat
type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{ file: string; page: string | number }>;
};

// Upload Callback
type UploadedInfo = {
  chunks: number;
  persistDir: string;
  title: string;
  studyPlan?: StudyPlan[];
};
```

---

## API Functions (lib/api.ts)

```typescript
uploadPdf(file: File)              // POST /upload
askQuestion(question: string)      // POST /ask
generateStudyMetadata()            // POST /study/metadata
getStudyMetadata()                 // GET /study/metadata
getApiBase(): string               // Auto-detect API URL
```

---

## Backend Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | /upload | FormData(file) | `{chunks_added, persist_dir}` |
| POST | /ask | `{question}` | `{answer, sources}` |
| POST | /study/metadata | (empty) | `{title, study_plan}` |
| GET | /study/metadata | (empty) | `{title, study_plan}` |
| GET | /health | (empty) | `{status, model_info}` |

---

## State Flow

```
User uploads PDF
    ↓
Upload component:
  - Calls uploadPdf() → Updates Chroma
  - Calls generateStudyMetadata() → GPT-4o mini generates title + plan
  - Calls onUploaded() callback with metadata
    ↓
App.tsx receives callback:
  - setReady(true)
  - setDocumentTitle(title)
  - setStudyPlan(plan)
    ↓
UI Updates:
  - Header shows title
  - Sidebar shows Study Plan
  - Chat becomes enabled
```

---

## Styling Guide

### CSS Classes Used
- **Glass Effect**: `.glass` (backdrop blur, transparency)
- **Brand Colors**: `.text-brand-ink`, `.bg-brand-sky`, `.border-brand-mist`, `.bg-brand-sand`
- **Responsive**: `lg:grid-cols-4`, `lg:col-span-1`, `lg:col-span-3`
- **Hover States**: `.hover:opacity-75`, `.hover:bg-opacity-80`
- **Focus States**: `.focus:ring-2`, `.focus:ring-brand-sky`
- **Disabled States**: `.disabled:opacity-60`

### Layout Classes
- **Card**: `.glass .p-4 .rounded-xl .shadow-sm .border`
- **Button**: `.rounded-lg .px-4 .py-2 .text-sm .font-semibold .transition`
- **Input**: `.rounded-lg .border .px-3 .py-2 .focus:outline-none`
- **Text**: `.text-xs / .text-sm / .text-lg / .text-3xl`

---

## Common Tasks

### Add a new Study Plan section
1. Backend: Modify `generate_study_context()` prompt in `app/deps.py`
2. Frontend: No changes needed (renders dynamically)
3. Test: Upload PDF and verify new sections appear

### Change header title format
Edit `App.tsx` line ~28:
```typescript
<h1 className="text-3xl font-bold text-brand-ink">
  {documentTitle || "Sube, procesa y estudia"}
</h1>
```

### Modify chat appearance
Edit `Chat.tsx` message rendering section (~55-90)

### Adjust grid layout
Edit `App.tsx` line ~35:
```typescript
<div className="grid gap-4 lg:grid-cols-4">
```
Change `lg:grid-cols-4` for different layouts

### Add error logging
Edit `api.ts` or component catch blocks

---

## Common Issues & Solutions

**Problem**: Study plan not showing
- **Check**: Is `studyPlan` state set? Console log in App.tsx Upload callback
- **Fix**: Verify `generateStudyMetadata()` returns valid `study_plan` array

**Problem**: Source badges not showing
- **Check**: Is `/ask` response including `sources` field?
- **Fix**: Check backend `ask.py` returns `AskResponse` with sources

**Problem**: API URL wrong
- **Check**: Console shows "🔗 API Base URL: ..." on load
- **Fix**: Check `getApiBase()` in `api.ts` for hostname detection logic

**Problem**: Chat disabled
- **Check**: Has PDF been uploaded? Is `ready === true`?
- **Fix**: Upload a PDF first via the Upload component

---

## Environment Setup

### Frontend Environment
- Node.js 18+ (comes with Codespaces)
- Dependencies: `npm install` in `/frontend`
- Dev Server: `npm run dev` (port 5173)
- Build: `npm run build`

### Codespaces Port Forwarding
- 5173 → Frontend (public)
- 8000 → Backend (public)
- API URL auto-detected from hostname

### Local Testing
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- No need for .env.local (runtime detection)

---

## Component Communication Pattern

```
Upload.tsx
├─ Calls API: uploadPdf(), generateStudyMetadata()
├─ Fires callback: onUploaded(data)
│
App.tsx (Parent)
├─ Receives callback data
├─ Updates state: setDocumentTitle(), setStudyPlan()
├─ Passes to children:
│  ├─ documentTitle → Chat component
│  ├─ studyPlan → StudySidebar component
│  ├─ ready → Chat disabled state
│
Chat.tsx, StudySidebar.tsx
└─ Display data from props
```

---

## Testing Checklist

- [ ] Upload PDF works
- [ ] Document title updates in header
- [ ] Study plan sidebar appears
- [ ] Chat becomes enabled
- [ ] Questions get answered
- [ ] Source citations show with page numbers
- [ ] Study plan is collapsible
- [ ] Responsive on mobile (stacks properly)
- [ ] Error handling works (try uploading 2 PDFs)
- [ ] API Base URL logged correctly in console

---

## Performance Notes

- Metadata generation happens AFTER upload (2 API calls)
- Study plan rendering is lazy (conditional rendering)
- Chat uses auto-scroll (flex + overflow)
- Message list not paginated (consider for large chats)
- No memoization currently (fine for typical use)

---

## Browser Console Debugging

```javascript
// Check API URL
console.log("API URL:", window.location.hostname);

// Check stored state (if Redux used in future)
// Currently uses React state only

// Network tab:
// - Check /upload response: { chunks_added, persist_dir }
// - Check /study/metadata response: { title, study_plan[] }
// - Check /ask response: { answer, sources[] }
```

---

## Next Development Steps

1. Add localStorage persistence for study plans
2. Implement study plan navigation (click → search)
3. Add dark mode toggle
4. Mobile-responsive sidebar drawer
5. Export chat history
6. Bookmark/highlight important passages
7. Progress tracking within study plan
8. Integration with spaced repetition

---

**Last Updated**: 2024
**Maintainers**: RootMind Development Team
**License**: MIT (or as specified)
