import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api, ApiError } from "./api";
import {
  jsonResponse,
  mockChapter,
  mockDashboard,
  mockDueReviews,
  mockReviewCorrect,
  mockSeedResult,
  mockStudySession,
  mockTokenResponse,
  mockUser,
} from "./test/fixtures";

describe("api client", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("login retorna TokenResponse tipado", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockTokenResponse));
    const result = await api.login("learner@example.com", "secret123");
    expect(result.access_token).toBe("test-jwt-token");
  });

  it("me envia Bearer token", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockUser));
    const user = await api.me("test-jwt-token");
    expect(user.id).toBe("user-test-1");
  });

  it("dashboard devolve métricas", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockDashboard));
    const dash = await api.dashboard("test-jwt-token", 5);
    expect(dash.vocabulary.accuracy_rate).toBe(83.3);
  });

  it("chapter carrega amostra de Gênesis", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockChapter));
    const chapter = await api.chapter("genesis", 1);
    expect(chapter.complete).toBe(false);
  });

  it("dueReviews retorna words sem questions", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockDueReviews));
    const due = await api.dueReviews("test-jwt-token", 20, "pt");
    expect(due.words.length).toBe(2);
    expect(due).not.toHaveProperty("questions");
  });

  it("createStudySession emite question_id sem correct", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockStudySession));
    const session = await api.createStudySession("test-jwt-token", 5, "pt");
    expect(session.questions[0].question_id).toMatch(/^q_/);
    expect(session.questions[0]).not.toHaveProperty("correct");
  });

  it("answerReview usa question_id", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockReviewCorrect));
    const result = await api.answerReview("test-jwt-token", {
      question_id: "q_test_light_001",
      selected: "luz",
      idempotency_key: "test-key-1",
    });
    expect(result.progress.xp).toBe(50);
  });

  it("seedChapter devolve contagens", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockSeedResult));
    const seed = await api.seedChapter("test-jwt-token", "genesis", 1);
    expect(seed.words_new).toBe(12);
  });

  it("lança ApiError em 401", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ detail: "Not authenticated" }, 401)
    );
    await expect(api.me("bad-token")).rejects.toMatchObject({
      name: "ApiError",
      status: 401,
    } satisfies Partial<ApiError>);
  });
});
