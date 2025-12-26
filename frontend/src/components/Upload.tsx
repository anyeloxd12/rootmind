import { useState } from "react";
import { uploadPdf, generateStudyMetadata } from "../lib/api";

type StudyPlan = {
  section: string;
  objective: string;
};

type Props = {
  onUploaded?: (info: {
    chunks: number;
    persistDir: string;
    title: string;
    studyPlan?: StudyPlan[];
  }) => void;
};

export function Upload({ onUploaded }: Props) {
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">(
    "idle"
  );
  const [message, setMessage] = useState<string>("");

  const handleFile = async (file: File) => {
    setStatus("uploading");
    setMessage("");
    try {
      const result = await uploadPdf(file);
      
      // Generar metadatos del estudio
      const metadata = await generateStudyMetadata();
      
      setStatus("done");
      setMessage(`Chunks indexados: ${result.chunks_added}`);
      onUploaded?.({
        chunks: result.chunks_added,
        persistDir: result.persist_dir,
        title: metadata.title,
        studyPlan: metadata.study_plan,
      });
    } catch (err) {
      const error = err as Error;
      setStatus("error");
      setMessage(error.message);
    }
  };

  const onChange = (evt: React.ChangeEvent<HTMLInputElement>) => {
    const file = evt.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="glass p-4 rounded-xl shadow-sm border border-brand-mist">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-brand-ink">Sube tu PDF</p>
          <p className="text-xs text-slate-500">
            Se dividirá en fragmentos y quedará listo para preguntas.
          </p>
        </div>
        <label className="inline-flex cursor-pointer items-center justify-center rounded-lg bg-brand-ink px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800">
          Elegir PDF
          <input
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={onChange}
          />
        </label>
      </div>
      <div className="mt-3 text-sm">
        {status === "uploading" && <span className="text-brand-ink">Procesando…</span>}
        {status === "done" && <span className="text-emerald-600">{message}</span>}
        {status === "error" && <span className="text-rose-600">{message}</span>}
      </div>
    </div>
  );
}
