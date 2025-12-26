import { useState } from "react";
import { Chat } from "./components/Chat";
import { Upload } from "./components/Upload";
import "./index.css";

function App() {
  const [ready, setReady] = useState(false);
  const [lastInfo, setLastInfo] = useState<string>("");

  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-sand via-white to-brand-mist">
      <div className="mx-auto max-w-5xl px-4 py-8 lg:py-12 space-y-6">
        <header className="flex flex-col gap-2">
          <p className="text-xs font-semibold uppercase text-brand-sky tracking-wide">
            RootMind Tutor
          </p>
          <h1 className="text-3xl font-bold text-brand-ink">Sube, procesa y estudia</h1>
          <p className="text-sm text-slate-600 max-w-2xl">
            Carga tu PDF, deja que lo fragmentemos y consulta al tutor cognitivo para
            guiar tu estudio.
          </p>
        </header>

        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <Upload
              onUploaded={({ chunks, persistDir }) => {
                setReady(true);
                setLastInfo(`Chunks: ${chunks} · Store: ${persistDir}`);
              }}
            />
            {lastInfo && (
              <p className="mt-2 text-xs text-slate-500">{lastInfo}</p>
            )}
          </div>
          <div className="lg:col-span-2 min-h-[420px]">
            <Chat disabled={!ready} />
            {!ready && (
              <p className="mt-2 text-xs text-slate-500">
                Sube un PDF para habilitar el chat.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
