import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, type ReviewResult } from "../api";
import { useAuth } from "../auth";

/** Palavras de Gênesis 1 com traduções pt (MVP local até existir GET /reviews/due). */
const WORDS: { word: string; options: string[]; correct: string }[] = [
  { word: "beginning", options: ["começo / princípio", "fim", "meio", "luz"], correct: "começo / princípio" },
  { word: "created", options: ["criou", "destruiu", "viu", "disse"], correct: "criou" },
  { word: "light", options: ["luz", "escuridão", "água", "terra"], correct: "luz" },
  { word: "darkness", options: ["escuridão", "luz", "céu", "dia"], correct: "escuridão" },
  { word: "waters", options: ["águas", "montanhas", "estrelas", "vento"], correct: "águas" },
];

function shuffle<T>(items: T[]): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

export function Review() {
  const { token, user } = useAuth();
  const native = user?.native_language || "pt";
  const questions = useMemo(
    () =>
      WORDS.map((q) => ({
        ...q,
        options: shuffle(q.options),
      })),
    []
  );

  const [index, setIndex] = useState(0);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [done, setDone] = useState(false);

  const current = questions[index];

  async function answer(selected: string) {
    if (!token || !current || busy) return;
    setBusy(true);
    setError("");
    try {
      const res = await api.answerReview(token, {
        word: current.word,
        selected,
        native_lang: native === "en" ? "pt" : native,
        idempotency_key: `web-${current.word}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      });
      setResult(res);
      setScore((s) => ({
        correct: s.correct + (res.is_correct ? 1 : 0),
        total: s.total + 1,
      }));
    } catch (err) {
      // Se a API rejeitar (ex: idioma), ainda mostra feedback local
      const isCorrect = selected === current.correct;
      setResult({
        is_correct: isCorrect,
        correct_answer: current.correct,
        xp_awarded: isCorrect ? 10 : 0,
        already_processed: false,
      });
      setScore((s) => ({
        correct: s.correct + (isCorrect ? 1 : 0),
        total: s.total + 1,
      }));
      if (err instanceof Error) setError(err.message);
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

  if (done) {
    return (
      <div className="card">
        <h1>Sessão concluída</h1>
        <p>
          Você acertou <strong>{score.correct}</strong> de <strong>{score.total}</strong>.
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

  return (
    <div>
      <h1>Prática</h1>
      <p className="muted">
        Pergunta {index + 1} de {questions.length}
      </p>

      <div className="card">
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
            {error && <p className="muted" style={{ fontSize: "0.85rem" }}>{error}</p>}
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
