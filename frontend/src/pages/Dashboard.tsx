import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Dashboard } from "../api";
import { useAuth } from "../auth";

export function DashboardPage() {
  const { token, user } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    api
      .dashboard(token)
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro"))
      .finally(() => setLoading(false));
  }, [token]);

  const progress = data?.progress;
  const vocab = data?.vocabulary;

  return (
    <div>
      <h1>Olá{user ? `, ${user.email.split("@")[0]}` : ""}</h1>
      <p className="muted">Seu resumo de aprendizagem.</p>

      {loading && <p className="muted">Carregando dashboard…</p>}
      {error && <p className="error">{error}</p>}

      {progress && vocab && data && (
        <>
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

          <div className="card">
            <h2>Meta diária</h2>
            <p style={{ margin: "0 0 0.5rem" }}>
              {data.reviews_today} / {data.daily_goal} revisões hoje{" "}
              {data.goal_met ? (
                <span className="success">· meta cumprida</span>
              ) : (
                <span className="muted">· continue praticando</span>
              )}
            </p>
            <div className="progress-bar">
              <div
                style={{
                  width: `${Math.min(
                    100,
                    Math.round((data.reviews_today / data.daily_goal) * 100)
                  )}%`,
                }}
              />
            </div>
          </div>

          <div className="card">
            <h2>Vocabulário</h2>
            <div className="stats">
              <div className="stat">
                <strong>{vocab.total_words}</strong>
                <span>Palavras</span>
              </div>
              <div className="stat">
                <strong>{vocab.due_words}</strong>
                <span>Pendentes</span>
              </div>
              <div className="stat">
                <strong>{vocab.accuracy_rate}%</strong>
                <span>Acerto</span>
              </div>
              <div className="stat">
                <strong>{vocab.reviewed_words}</strong>
                <span>Já revisadas</span>
              </div>
            </div>
            <p className="muted" style={{ marginBottom: 0, marginTop: "0.75rem" }}>
              {vocab.correct_reviews} acertos · {vocab.incorrect_reviews} erros ·{" "}
              {vocab.never_reviewed} ainda sem revisão
            </p>
          </div>

          {data.recent_activity.length > 0 && (
            <div className="card">
              <h2>Atividade recente</h2>
              <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
                {data.recent_activity.map((item, idx) => (
                  <li key={`${item.word}-${item.created_at}-${idx}`}>
                    <strong>{item.word}</strong>{" "}
                    <span className={item.is_correct ? "success" : "error"}>
                      {item.is_correct ? "acerto" : "erro"}
                    </span>
                    {item.xp_awarded > 0 ? ` · +${item.xp_awarded} XP` : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      <div className="actions">
        <Link
          className="btn"
          to="/read"
          style={{
            background: "var(--accent)",
            color: "white",
            padding: "0.7rem 1rem",
            borderRadius: 8,
            fontWeight: 600,
          }}
        >
          Ler Gênesis 1
        </Link>
        <Link
          to="/review"
          style={{
            background: "var(--surface-2)",
            color: "var(--text)",
            padding: "0.7rem 1rem",
            borderRadius: 8,
            fontWeight: 600,
          }}
        >
          Praticar palavras
        </Link>
      </div>
    </div>
  );
}

// Compatível com o import antigo
export { DashboardPage as Dashboard };
