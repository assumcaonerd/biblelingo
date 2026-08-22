/** Contratos HTTP alinhados a api/schemas/. */

export type NativeLanguage = "pt" | "es" | "en" | "ar" | "he";

export type RegisterRequest = {
  email: string;
  password: string;
  native_language?: NativeLanguage;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type User = {
  id: string;
  email: string;
  native_language: string;
  created_at?: string | null;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type LevelProgress = {
  current: number;
  level_start: number;
  next_level: number;
  percent: number;
};

export type Progress = {
  xp: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string | null;
  streak_bonus: number;
  level_progress: LevelProgress;
};

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

export type RecentActivityItem = {
  word: string;
  is_correct: boolean;
  xp_awarded: number;
  created_at: string;
};

export type Dashboard = {
  progress: Progress;
  vocabulary: VocabularyStats;
  recent_activity: RecentActivityItem[];
  daily_goal: number;
  reviews_today: number;
  goal_met: boolean;
  last_activity_date: string | null;
};

export type Verse = {
  verse_number: number;
  text: string;
};

export type Chapter = {
  book: string;
  chapter: number;
  verses: Verse[];
  label?: string | null;
  complete?: boolean;
  verse_range?: string | null;
};

export type ReviewAnswerRequest = {
  question_id: string;
  selected: string;
  idempotency_key: string;
};

export type ReviewAnswerResponse = {
  question_id: string;
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

export type ReviewResult = {
  is_correct: boolean;
  correct_answer: string;
  xp_awarded: number;
  already_processed: boolean;
  next_review?: string;
  review_streak?: number;
  progress?: Progress;
  question_id?: string;
};

export type DueWordItem = {
  word: string;
  origin: string;
  context: string;
  next_review?: string | null;
};

/** GET /reviews/due — somente leitura */
export type DueReviews = {
  count: number;
  native_lang: string;
  words: DueWordItem[];
  mode?: string;
};

export type DueQuestion = {
  question_id: string;
  word: string;
  options: string[];
  context: string;
  origin: string;
  next_review?: string | null;
};

/** POST /study-sessions */
export type StudySessionResponse = {
  count: number;
  native_lang: string;
  questions: DueQuestion[];
  mode?: string;
};

export type SeedChapterRequest = {
  book: string;
  chapter: number;
  words?: string[] | null;
};

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

export type SeedResult = SeedChapterResponse;
export type ReviewAnswer = ReviewAnswerRequest;
