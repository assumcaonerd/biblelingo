import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api, ApiError } from "./api";
import {
  jsonResponse,
  mockChapter,
  mockDashboard,
  mockDueReviews,
  mockReviewCorrect,
  mockSeedResult,
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
    expect(result.user.email).toBe("learner@example.com");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/v1/auth/login"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("me envia Bearer token", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockUser));

    const user = await api.me("test-jwt-token");

    expect(user.id).toBe("user-test-1");
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer test-jwt-token");
  });

  it("dashboard devolve VocabularyStats e meta diária", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockDashboard));

    const dash = await api.dashboard("test-jwt-token", 5);

    expect(dash.vocabulary.accuracy_rate).toBe(83.3);
    expect(dash.goal_met).toBe(false);
    expect(dash.recent_activity[0]?.word).toBe("light");
  });

  it("chapter carrega versículos de Gênesis", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockChapter));

    const chapter = await api.chapter("genesis", 1);

    expect(chapter.verses).toHaveLength(2);
    expect(chapter.verses[0].verse_number).toBe(1);
  });

  it("seedChapter devolve contagens idempotentes", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockSeedResult));

    const seed = await api.seedChapter("test-jwt-token", "genesis", 1);

    expect(seed.words_new).toBe(12);
    expect(seed.due_count).toBe(12);
  });

  it("dueReviews inclui opções e resposta correta", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockDueReviews));

    const due = await api.dueReviews("test-jwt-token", 5, "pt");

    expect(due.count).toBe(2);
    const q = due.questions[0];
    expect(q.options).toContain(q.correct);
  });

  it("answerReview retorna progresso embutido", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(mockReviewCorrect));

    const result = await api.answerReview("test-jwt-token", {
      word: "light",
      selected: "luz",
      native_lang: "pt",
      idempotency_key: "test-key-1",
    });

    expect(result.is_correct).toBe(true);
    expect(result.xp_awarded).toBe(10);
    expect(result.progress.xp).toBe(50);
  });

  it("lança ApiError com status em falha HTTP", async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ detail: "Not authenticated" }, 401)
    );

    await expect(api.me("bad-token")).rejects.toMatchObject({
      name: "ApiError",
      status: 401,
    } satisfies Partial<ApiError>);
  });
});
