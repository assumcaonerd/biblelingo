/**
 * Cliente HTTP da API BibleLingo.
 * Tipos: ver src/types/api.ts
 */

import type {
  Chapter,
  Dashboard,
  DueReviews,
  NativeLanguage,
  Progress,
  ReviewAnswerRequest,
  ReviewAnswerResponse,
  SeedChapterResponse,
  StudySessionResponse,
  TokenResponse,
  User,
} from "./types/api";

export type {
  Chapter,
  Dashboard,
  DueQuestion,
  DueReviews,
  DueWordItem,
  LevelProgress,
  NativeLanguage,
  Progress,
  RecentActivityItem,
  RegisterRequest,
  ReviewAnswer,
  ReviewAnswerRequest,
  ReviewAnswerResponse,
  ReviewResult,
  SeedChapterRequest,
  SeedChapterResponse,
  SeedResult,
  StudySessionResponse,
  TokenResponse,
  User,
  VocabularyStats,
  Verse,
} from "./types/api";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function authHeaders(token: string | null): HeadersInit {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      const body: unknown = await res.json();
      if (
        body &&
        typeof body === "object" &&
        "detail" in body &&
        (body as { detail: unknown }).detail !== undefined
      ) {
        detail = (body as { detail: unknown }).detail;
      } else {
        detail = body;
      }
    } catch {
      /* ignore */
    }
    const message =
      typeof detail === "string" ? detail : JSON.stringify(detail);
    throw new ApiError(res.status, message);
  }
  return res.json() as Promise<T>;
}

export const api = {
  register(
    email: string,
    password: string,
    native_language: NativeLanguage = "pt"
  ) {
    return fetch(`${API_BASE}/v1/auth/register`, {
      method: "POST",
      headers: authHeaders(null),
      body: JSON.stringify({ email, password, native_language }),
    }).then((r) => handle<TokenResponse>(r));
  },

  login(email: string, password: string) {
    return fetch(`${API_BASE}/v1/auth/login`, {
      method: "POST",
      headers: authHeaders(null),
      body: JSON.stringify({ email, password }),
    }).then((r) => handle<TokenResponse>(r));
  },

  me(token: string) {
    return fetch(`${API_BASE}/v1/me`, {
      headers: authHeaders(token),
    }).then((r) => handle<User>(r));
  },

  progress(token: string) {
    return fetch(`${API_BASE}/v1/progress`, {
      headers: authHeaders(token),
    }).then((r) => handle<Progress>(r));
  },

  dashboard(token: string, dailyGoal = 5) {
    return fetch(`${API_BASE}/v1/dashboard?daily_goal=${dailyGoal}`, {
      headers: authHeaders(token),
    }).then((r) => handle<Dashboard>(r));
  },

  chapter(book: string, chapter: number) {
    return fetch(`${API_BASE}/v1/chapters/${book}/${chapter}`).then((r) =>
      handle<Chapter>(r)
    );
  },

  seedChapter(token: string, book: string, chapter: number) {
    return fetch(`${API_BASE}/v1/vocabulary/seed`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ book, chapter }),
    }).then((r) => handle<SeedChapterResponse>(r));
  },

  /** GET puro: palavras vencidas (sem emitir question_id). */
  dueReviews(token: string, limit = 20, native_lang?: string) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (native_lang) params.set("native_lang", native_lang);
    return fetch(`${API_BASE}/v1/reviews/due?${params}`, {
      headers: authHeaders(token),
    }).then((r) => handle<DueReviews>(r));
  },

  /** POST: emite perguntas com question_id. */
  createStudySession(token: string, limit = 5, native_lang?: string) {
    return fetch(`${API_BASE}/v1/study-sessions`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ limit, native_lang }),
    }).then((r) => handle<StudySessionResponse>(r));
  },

  answerReview(token: string, payload: ReviewAnswerRequest) {
    return fetch(`${API_BASE}/v1/reviews/answer`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    }).then((r) => handle<ReviewAnswerResponse>(r));
  },
};
