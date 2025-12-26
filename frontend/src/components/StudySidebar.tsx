import { useState } from "react";

type StudyPlan = {
  section: string;
  objective: string;
};

type Props = {
  plan: StudyPlan[];
};

export function StudySidebar({ plan }: Props) {
  const [expanded, setExpanded] = useState(true);

  if (!plan || plan.length === 0) {
    return null;
  }

  return (
    <aside className="glass p-4 rounded-xl shadow-sm border border-brand-mist h-fit sticky top-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between mb-3 hover:opacity-75 transition"
      >
        <h3 className="text-sm font-semibold text-brand-ink">📚 Plan de Estudios</h3>
        <span className="text-xs text-brand-sky">{expanded ? "▼" : "▶"}</span>
      </button>

      {expanded && (
        <nav className="space-y-2">
          {plan.map((item, idx) => (
            <div key={idx} className="text-xs">
              <p className="font-semibold text-brand-ink hover:text-brand-sky cursor-pointer transition">
                {idx + 1}. {item.section}
              </p>
              <p className="text-slate-500 ml-2 text-[11px] italic">{item.objective}</p>
            </div>
          ))}
        </nav>
      )}
    </aside>
  );
}
