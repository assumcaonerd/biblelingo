/** Cliente HTTP da API BibleLingo. */

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

export type User = {
  id: string;
  email: string;
  native_language: string;
  created_at?: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type Progress = {
  xp: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string | null;
  streak_bonus: number;
  level_progress: {
    current: number;
    level_start: number;
    next_level: number;
    percent: number;
  };
};

export type Verse = {
  verse_number: number;
  text: string;
};

export type Chapter = {
  book: string;
  chapter: number;
  verses: Verse[];
};

export type ReviewAnswer = {
  word: string;
  selected: string;
  native_lang: string;
  idempotency_key: string;
};

export type ReviewResult = {
  is_correct: boolean;
  correct_answer: string;
  xp_awarded: number;
  already_processed: boolean;
  next_review?: string;
  review_streak?: number;
};

export type DueQuestion = {
  word: string;
  options: string[];
  correct: string;
  context: string;
  origin: string;
  next_review?: string | null;
};

export type DueReviews = {
  count: number;
  native_lang: string;
  questions: DueQuestion[];
};

function authHeaders(token: string | null): HeadersInit {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return res.json() as Promise<T>;
}

export const api = {
  register(email: string, password: string, native_language = "pt") {
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

  chapter(book: string, chapter: number) {
    return fetch(`${API_BASE}/v1/chapters/${book}/${chapter}`).then((r) =>
      handle<Chapter>(r)
    );
  },

  dueReviews(token: string, limit = 5, native_lang?: string) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (native_lang) params.set("native_lang", native_lang);
    return fetch(`${API_BASE}/v1/reviews/due?${params}`, {
      headers: authHeaders(token),
    }).then((r) => handle<DueReviews>(r));
  },

  answerReview(token: string, payload: ReviewAnswer) {
    return fetch(`${API_BASE}/v1/reviews/answer`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(payload),
    }).then((r) => handle<ReviewResult>(r));
  },
};
