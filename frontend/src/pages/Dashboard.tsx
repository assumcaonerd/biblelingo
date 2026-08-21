import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Progress } from "../api";
import { useAuth } from "../auth";

export function Dashboard() {
  const { token, user } = useAuth();
  const [progress, setProgress] = useState<Progress | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    api
      .progress(token)
      .then(setProgress)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro"));
  }, [token]);

  return (
    <div>
      <h1>Olá{user ? `, ${user.email.split("@")[0]}` : ""}</h1>
      <p className="muted">Continue de onde parou.</p>

      {error && <p className="error">{error}</p>}

      {progress && (
        <div className="card">
          <div className="stats">
            <div className="stat">
              <strong>{progress.level}</strong>
              <span>Nível</span>
            </div>
            <div className="stat">
              <strong>{progress.xp}</strong>
              <span>XP</span>
            </div>
            <div className="stat">
              <strong>{progress.current_streak}</strong>
              <span>Streak</span>
            </div>
            <div className="stat">
              <strong>{progress.longest_streak}</strong>
              <span>Recorde</span>
            </div>
          </div>
          <p className="muted" style={{ marginTop: "1rem", marginBottom: 0 }}>
            Progresso até o nível {progress.level + 1}:{" "}
            {progress.level_progress.percent}%
          </p>
          <div className="progress-bar">
            <div style={{ width: `${progress.level_progress.percent}%` }} />
          </div>
        </div>
      )}

      <div className="actions">
        <Link className="btn" to="/read">
          Ler Gênesis 1
        </Link>
        <Link className="btn secondary" to="/review" style={{ background: "var(--surface-2)", color: "var(--text)", padding: "0.7rem 1rem", borderRadius: 8, fontWeight: 600 }}>
          Praticar palavras
        </Link>
      </div>
    </div>
  );
}
