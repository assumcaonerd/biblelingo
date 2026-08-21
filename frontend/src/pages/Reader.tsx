import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type Chapter, type SeedResult } from "../api";
import { useAuth } from "../auth";
import { SpeakButton } from "../components/SpeakButton";

const LESSONS = [
  { book: "genesis", chapter: 1, label: "Gênesis 1" },
  { book: "psalms", chapter: 23, label: "Salmos 23" },
] as const;

type Lesson = (typeof LESSONS)[number];

export function Reader() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<Lesson>(LESSONS[0]);
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [seedInfo, setSeedInfo] = useState<SeedResult | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setChapter(null);
    setSeedInfo(null);

    api
      .chapter(lesson.book, lesson.chapter)
      .then((value) => {
        if (active) setChapter(value);
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : "Erro");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [lesson]);

  async function practiceChapter() {
    if (!token) return;
    setSeeding(true);
    setError("");
    try {
      const result = await api.seedChapter(token, lesson.book, lesson.chapter);
      setSeedInfo(result);
      navigate("/review");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao preparar prática");
    } finally {
      setSeeding(false);
    }
  }

  const fullChapterText = chapter?.verses.map((v) => v.text).join(" ") ?? "";
  const lessonValue = `${lesson.book}:${lesson.chapter}`;

  return (
    <div>
      <div className="actions" style={{ marginTop: 0 }}>
        <label htmlFor="lesson-select">Lição</label>
        <select
          id="lesson-select"
          value={lessonValue}
          disabled={loading || seeding}
          onChange={(event) => {
            const selected = LESSONS.find(
              (item) => `${item.book}:${item.chapter}` === event.target.value,
            );
            if (selected) setLesson(selected);
          }}
        >
          {LESSONS.map((item) => (
            <option key={`${item.book}:${item.chapter}`} value={`${item.book}:${item.chapter}`}>
              {item.label}
            </option>
          ))}
        </select>
      </div>

      <h1>{lesson.label}</h1>
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
          {seedInfo.words_new} novas · {seedInfo.words_existing} já conhecidas · {seedInfo.due_count} para revisar
        </p>
      )}

      <div className="actions">
        <button type="button" disabled={seeding || !token || loading} onClick={practiceChapter}>
          {seeding ? "Preparando palavras…" : "Praticar palavras deste capítulo"}
        </button>
        <Link to="/" className="muted">
          Voltar
        </Link>
      </div>
    </div>
  );
}
