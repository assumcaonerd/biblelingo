/**
 * Contratos HTTP alinhados aos schemas Pydantic em api/schemas/.
 *
 * Datas chegam como string ISO (JSON); no backend são date/datetime.
 * Nomes de campos seguem o JSON serializado pelo FastAPI (snake_case).
 *
 * Fonte de verdade no servidor:
 *   api/schemas/auth.py
 *   api/schemas/progress.py
 *   api/schemas/dashboard.py
 *   api/schemas/review.py
 *   api/schemas/vocabulary.py
 *   api/schemas/content.py
 */

/** Literal["pt", "es", "en", "ar", "he"] */
export type NativeLanguage = "pt" | "es" | "en" | "ar" | "he";

// ---------------------------------------------------------------------------
// Auth — api/schemas/auth.py
// ---------------------------------------------------------------------------

/** RegisterRequest */
export type RegisterRequest = {
  email: string;
  password: string;
  native_language?: NativeLanguage;
};

/** LoginRequest */
export type LoginRequest = {
  email: string;
  password: string;
};

/** UserOut */
export type User = {
  id: string;
  email: string;
  native_language: string;
  created_at?: string | null;
};

/** TokenResponse */
export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

// ---------------------------------------------------------------------------
// Progress — api/schemas/progress.py
// ---------------------------------------------------------------------------

/** LevelProgress */
export type LevelProgress = {
  current: number;
  level_start: number;
  next_level: number;
  percent: number;
};

/** ProgressResponse */
export type Progress = {
  xp: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string | null;
  streak_bonus: number;
  level_progress: LevelProgress;
};

// ---------------------------------------------------------------------------
// Dashboard — api/schemas/dashboard.py
// ---------------------------------------------------------------------------

/** VocabularyStats */
export type VocabularyStats = {
  total_words: number;
  due_words: number;
  reviewed_words: number;
  never_reviewed: number;
  total_reviews: number;
  correct_reviews: number;
  incorrect_reviews: number;
  accuracy_rate: number;
};

/** RecentActivityItem */
export type RecentActivityItem = {
  word: string;
  is_correct: boolean;
  xp_awarded: number;
  created_at: string;
};

/** DashboardResponse */
export type Dashboard = {
  progress: Progress;
  vocabulary: VocabularyStats;
  recent_activity: RecentActivityItem[];
  daily_goal: number;
  reviews_today: number;
  goal_met: boolean;
  last_activity_date: string | null;
};

// ---------------------------------------------------------------------------
// Content — api/schemas/content.py
// ---------------------------------------------------------------------------

/** VerseOut */
export type Verse = {
  verse_number: number;
  text: string;
};

/** ChapterOut */
export type Chapter = {
  book: string;
  chapter: number;
  verses: Verse[];
};

// ---------------------------------------------------------------------------
// Review — api/schemas/review.py
// ---------------------------------------------------------------------------

/** ReviewAnswerRequest */
export type ReviewAnswerRequest = {
  word: string;
  selected: string;
  native_lang: string;
  idempotency_key: string;
};

/** ReviewAnswerResponse — resposta completa do POST /v1/reviews/answer */
export type ReviewAnswerResponse = {
  idempotency_key: string;
  word: string;
  selected: string;
  correct_answer: string;
  is_correct: boolean;
  already_processed: boolean;
  xp_awarded: number;
  next_review: string;
  review_streak: number;
  progress: Progress;
};

/**
 * Subconjunto usado pela UI de quiz (campos opcionais para compat).
 * Preferir ReviewAnswerResponse quando o progresso embutido for necessário.
 */
export type ReviewResult = {
  is_correct: boolean;
  correct_answer: string;
  xp_awarded: number;
  already_processed: boolean;
  next_review?: string;
  review_streak?: number;
  progress?: Progress;
};

/** DueQuestion */
export type DueQuestion = {
  word: string;
  options: string[];
  correct: string;
  context: string;
  origin: string;
  next_review?: string | null;
};

/** DueReviewsResponse */
export type DueReviews = {
  count: number;
  native_lang: string;
  questions: DueQuestion[];
};

// ---------------------------------------------------------------------------
// Vocabulary seed — api/schemas/vocabulary.py
// ---------------------------------------------------------------------------

/** SeedChapterRequest */
export type SeedChapterRequest = {
  book: string;
  chapter: number;
  words?: string[] | null;
};

/** SeedChapterResponse */
export type SeedChapterResponse = {
  book: string;
  chapter: number;
  words_seen: number;
  words_new: number;
  words_existing: number;
  words_with_translation: number;
  due_count: number;
  sample_new: string[];
};

/** Alias legado usado nas páginas */
export type SeedResult = SeedChapterResponse;
export type ReviewAnswer = ReviewAnswerRequest;
