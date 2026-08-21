import type {
  Chapter,
  Dashboard,
  DueReviews,
  Progress,
  ReviewAnswerResponse,
  SeedChapterResponse,
  StudySessionResponse,
  TokenResponse,
  User,
} from "../types/api";

export const mockUser: User = {
  id: "user-test-1",
  email: "learner@example.com",
  native_language: "pt",
  created_at: "2026-08-21T12:00:00Z",
};

export const mockTokenResponse: TokenResponse = {
  access_token: "test-jwt-token",
  token_type: "bearer",
  user: mockUser,
};

export const mockProgress: Progress = {
  xp: 40,
  level: 1,
  current_streak: 2,
  longest_streak: 5,
  last_activity_date: "2026-08-21",
  streak_bonus: 1.1,
  level_progress: {
    current: 40,
    level_start: 0,
    next_level: 100,
    percent: 40,
  },
};

export const mockDashboard: Dashboard = {
  progress: mockProgress,
  vocabulary: {
    total_words: 24,
    due_words: 5,
    reviewed_words: 8,
    never_reviewed: 16,
    total_reviews: 12,
    correct_reviews: 10,
    incorrect_reviews: 2,
    accuracy_rate: 83.3,
  },
  recent_activity: [
    {
      word: "light",
      is_correct: true,
      xp_awarded: 10,
      created_at: "2026-08-21T14:00:00Z",
    },
  ],
  daily_goal: 5,
  reviews_today: 2,
  goal_met: false,
  last_activity_date: "2026-08-21",
};

export const mockChapter: Chapter = {
  book: "genesis",
  chapter: 1,
  label: "Gênesis 1:1-10 (amostra)",
  complete: false,
  verse_range: "1-10",
  verses: [
    {
      verse_number: 1,
      text: "In the beginning, God created the heavens and the earth.",
    },
    {
      verse_number: 3,
      text: 'God said, "Let there be light," and there was light.',
    },
  ],
};

export const mockDueReviews: DueReviews = {
  count: 2,
  native_lang: "pt",
  mode: "due",
  words: [
    {
      word: "light",
      origin: "Genesis 1:3",
      context: 'God said, "Let there be light," and there was light.',
      next_review: "2026-08-21",
    },
    {
      word: "created",
      origin: "Genesis 1:1",
      context: "In the beginning, God created the heavens and the earth.",
      next_review: "2026-08-21",
    },
  ],
};

export const mockStudySession: StudySessionResponse = {
  count: 2,
  native_lang: "pt",
  mode: "session",
  questions: [
    {
      question_id: "q_test_light_001",
      word: "light",
      options: ["luz", "escuridão", "água", "terra"],
      context: 'God said, "Let there be light," and there was light.',
      origin: "Genesis 1:3",
      next_review: "2026-08-21",
    },
    {
      question_id: "q_test_created_002",
      word: "created",
      options: ["criou", "destruiu", "viu", "disse"],
      context: "In the beginning, God created the heavens and the earth.",
      origin: "Genesis 1:1",
      next_review: "2026-08-21",
    },
  ],
};

export const mockSeedResult: SeedChapterResponse = {
  book: "genesis",
  chapter: 1,
  words_seen: 40,
  words_new: 12,
  words_existing: 28,
  words_with_translation: 30,
  due_count: 12,
  sample_new: ["beginning", "created", "heavens"],
};

export const mockReviewCorrect: ReviewAnswerResponse = {
  question_id: "q_test_light_001",
  idempotency_key: "test-key-1",
  word: "light",
  selected: "luz",
  correct_answer: "luz",
  is_correct: true,
  already_processed: false,
  xp_awarded: 10,
  next_review: "2026-08-22",
  review_streak: 1,
  progress: {
    ...mockProgress,
    xp: 50,
  },
};

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
