import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type DueQuestion, type ReviewResult } from "../api";
import { useAuth } from "../auth";

export function Review() {
  const { token, user } = useAuth();
  const native = user?.native_language || "pt";

  const [questions, setQuestions] = useState<DueQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [index, setIndex] = useState(0);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    api
      .dueReviews(token, 5, native)
      .then((data) => {
        setQuestions(data.questions);
        if (data.count === 0) {
          setLoadError("Nenhuma palavra para revisar agora.");
        }
      })
      .catch((err) =>
        setLoadError(err instanceof Error ? err.message : "Erro ao carregar")
      )
      .finally(() => setLoading(false));
  }, [token, native]);

  const current = questions[index];

  async function answer(selected: string) {
    if (!token || !current || busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await api.answerReview(token, {
        word: current.word,
        selected,
        native_lang: native,
        idempotency_key: `web-${current.word}-${Date.now()}-${Math.random()
          .toString(36)
          .slice(2, 8)}`,
      });
      setResult(res);
      setScore((s) => ({
        correct: s.correct + (res.is_correct ? 1 : 0),
        total: s.total + 1,
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar resposta");
    } finally {
      setBusy(false);
    }
  }

  function next() {
    setResult(null);
    setError("");
    if (index + 1 >= questions.length) {
      setDone(true);
    } else {
      setIndex((i) => i + 1);
    }
  }

  if (loading) {
    return <p className="muted">Carregando palavras vencidas…</p>;
  }

  if (loadError && questions.length === 0) {
    return (
      <div className="card">
        <h1>Prática</h1>
        <p className="muted">{loadError}</p>
        <Link to="/">Voltar</Link>
      </div>
    );
  }

  if (done) {
    return (
      <div className="card">
        <h1>Sessão concluída</h1>
        <p>
          Você acertou <strong>{score.correct}</strong> de{" "}
          <strong>{score.total}</strong>.
        </p>
        <div className="actions">
          <Link
            to="/"
            className="btn"
            style={{
              background: "var(--accent)",
              color: "white",
              padding: "0.7rem 1rem",
              borderRadius: 8,
              fontWeight: 600,
            }}
          >
            Ver progresso
          </Link>
          <button type="button" className="secondary" onClick={() => window.location.reload()}>
            Praticar de novo
          </button>
        </div>
      </div>
    );
  }

  if (!current) {
    return (
      <div className="card">
        <p className="muted">Nada para revisar.</p>
        <Link to="/">Voltar</Link>
      </div>
    );
  }

  return (
    <div>
      <h1>Prática</h1>
      <p className="muted">
        Pergunta {index + 1} de {questions.length}
        {current.origin ? ` · ${current.origin}` : ""}
      </p>

      <div className="card">
        {current.context && (
          <p className="muted" style={{ fontStyle: "italic", marginTop: 0 }}>
            “{current.context}”
          </p>
        )}
        <h2>
          Qual o significado de <em>{current.word}</em>?
        </h2>

        {!result && (
          <div className="quiz-options">
            {current.options.map((opt) => (
              <button key={opt} type="button" disabled={busy} onClick={() => answer(opt)}>
                {opt}
              </button>
            ))}
          </div>
        )}

        {result && (
          <div>
            <p className={result.is_correct ? "success" : "error"}>
              {result.is_correct
                ? `Correto! +${result.xp_awarded} XP`
                : `Errado. Resposta: ${result.correct_answer}`}
            </p>
            {error && (
              <p className="muted" style={{ fontSize: "0.85rem" }}>
                {error}
              </p>
            )}
            <button type="button" onClick={next}>
              {index + 1 >= questions.length ? "Finalizar" : "Próxima"}
            </button>
          </div>
        )}
      </div>

      <Link to="/" className="muted">
        Sair da prática
      </Link>
    </div>
  );
}
