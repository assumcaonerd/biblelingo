import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type Chapter, type SeedResult } from "../api";
import { useAuth } from "../auth";
import { SpeakButton } from "../components/SpeakButton";

export function Reader() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [seedInfo, setSeedInfo] = useState<SeedResult | null>(null);

  useEffect(() => {
    api
      .chapter("genesis", 1)
      .then(setChapter)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro"))
      .finally(() => setLoading(false));
  }, []);

  async function practiceChapter() {
    if (!token) return;
    setSeeding(true);
    setError("");
    try {
      const result = await api.seedChapter(token, "genesis", 1);
      setSeedInfo(result);
      navigate("/review");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao preparar prática");
    } finally {
      setSeeding(false);
    }
  }

  const fullChapterText =
    chapter?.verses.map((v) => v.text).join(" ") ?? "";

  return (
    <div>
      <h1>Genesis 1</h1>
      <p className="muted">
        World English Bible — leia e ouça, depois pratique as palavras deste capítulo.
      </p>

      {loading && <p className="muted">Carregando…</p>}
      {error && <p className="error">{error}</p>}

      {chapter && (
        <div className="card">
          <div className="actions" style={{ marginTop: 0, marginBottom: "1rem" }}>
            <SpeakButton text={fullChapterText} label="Ouvir capítulo" rate={0.95} />
          </div>
          <div className="verse-list">
            {chapter.verses.map((v) => (
              <div
                key={v.verse_number}
                className="verse"
                style={{
                  display: "flex",
                  gap: "0.5rem",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                }}
              >
                <p style={{ margin: 0, flex: 1 }}>
                  <span className="verse-num">{v.verse_number}</span>
                  {v.text}
                </p>
                <SpeakButton text={v.text} label="▶" rate={0.9} className="ghost" />
              </div>
            ))}
          </div>
        </div>
      )}

      {seedInfo && (
        <p className="muted">
          {seedInfo.words_new} novas · {seedInfo.words_existing} já conhecidas ·{" "}
          {seedInfo.due_count} para revisar
        </p>
      )}

      <div className="actions">
        <button type="button" disabled={seeding || !token} onClick={practiceChapter}>
          {seeding ? "Preparando palavras…" : "Praticar palavras deste capítulo"}
        </button>
        <Link to="/" className="muted">
          Voltar
        </Link>
      </div>
    </div>
  );
}
