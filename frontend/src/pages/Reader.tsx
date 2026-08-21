import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Chapter } from "../api";

export function Reader() {
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .chapter("genesis", 1)
      .then(setChapter)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1>Genesis 1</h1>
      <p className="muted">World English Bible — leia com atenção e depois pratique as palavras.</p>

      {loading && <p className="muted">Carregando…</p>}
      {error && <p className="error">{error}</p>}

      {chapter && (
        <div className="card">
          <div className="verse-list">
            {chapter.verses.map((v) => (
              <p key={v.verse_number} className="verse">
                <span className="verse-num">{v.verse_number}</span>
                {v.text}
              </p>
            ))}
          </div>
        </div>
      )}

      <div className="actions">
        <Link
          to="/review"
          className="btn"
          style={{
            background: "var(--accent)",
            color: "white",
            padding: "0.7rem 1rem",
            borderRadius: 8,
            fontWeight: 600,
          }}
        >
          Praticar palavras deste capítulo
        </Link>
        <Link to="/" className="muted">
          Voltar
        </Link>
      </div>
    </div>
  );
}
