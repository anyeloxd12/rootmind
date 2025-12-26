import { FormEvent, useState } from "react";
import { askQuestion } from "../lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Props = {
  disabled?: boolean;
};

export function Chat({ disabled }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = async (evt: FormEvent) => {
    evt.preventDefault();
    if (!question.trim() || loading || disabled) return;
    const q = question.trim();
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setQuestion("");
    setLoading(true);
    setError(null);
    try {
      const res = await askQuestion(q);
      const answer = res.answer || "Sin respuesta";
      setMessages((prev) => [...prev, { role: "assistant", content: answer }]);
    } catch (err) {
      const e = err as Error;
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass p-4 rounded-xl shadow-sm border border-brand-mist h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-sm font-semibold">Chat de estudio</p>
          <p className="text-xs text-slate-500">Haz preguntas sobre tu PDF.</p>
        </div>
        {loading && <span className="text-xs text-brand-ink">Pensando…</span>}
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-slate-500">Sube un PDF y pregunta algo.</p>
        )}
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
              m.role === "user"
                ? "bg-brand-mist text-brand-ink self-end"
                : "bg-white text-slate-800 border border-slate-100"
            }`}
          >
            <span className="block text-[11px] uppercase tracking-wide text-slate-500 mb-1">
              {m.role === "user" ? "Tú" : "RootMind"}
            </span>
            {m.content}
          </div>
        ))}
      </div>

      <form onSubmit={send} className="mt-3 flex gap-2">
        <input
          className="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-sky"
          placeholder="Escribe tu pregunta..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={disabled || loading}
        />
        <button
          type="submit"
          disabled={disabled || loading}
          className="rounded-lg bg-brand-sky px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-500 disabled:opacity-60"
        >
          Enviar
        </button>
      </form>
      {error && <p className="mt-2 text-xs text-rose-600">{error}</p>}
    </div>
  );
}
