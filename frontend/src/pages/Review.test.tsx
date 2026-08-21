import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { render } from "@testing-library/react";
import { Review } from "./Review";
import {
  mockReviewCorrect,
  mockStudySession,
  mockUser,
} from "../test/fixtures";

const sessionMock = vi.fn();
const answerMock = vi.fn();

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      createStudySession: (...args: unknown[]) => sessionMock(...args),
      answerReview: (...args: unknown[]) => answerMock(...args),
    },
  };
});

vi.mock("../auth", () => ({
  useAuth: () => ({
    token: "test-jwt-token",
    user: mockUser,
    ready: true,
    sessionError: null,
    login: async () => undefined,
    register: async () => undefined,
    logout: () => undefined,
  }),
}));

vi.mock("../components/SpeakButton", () => ({
  SpeakButton: ({ label }: { label?: string }) => (
    <button type="button">{label ?? "Ouvir"}</button>
  ),
}));

function renderReview() {
  return render(
    <MemoryRouter>
      <Review />
    </MemoryRouter>
  );
}

describe("Review", () => {
  beforeEach(() => {
    sessionMock.mockReset();
    answerMock.mockReset();
  });

  it("abre sessão via POST e mostra opções", async () => {
    sessionMock.mockResolvedValueOnce(mockStudySession);

    renderReview();

    await waitFor(() => {
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });

    expect(sessionMock).toHaveBeenCalledWith("test-jwt-token", 5, "pt");
    expect(screen.getByRole("button", { name: "luz" })).toBeInTheDocument();
  });

  it("ao acertar envia question_id", async () => {
    const user = userEvent.setup();
    sessionMock.mockResolvedValueOnce(mockStudySession);
    answerMock.mockResolvedValueOnce(mockReviewCorrect);

    renderReview();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "luz" })).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "luz" }));

    await waitFor(() => {
      expect(screen.getByText(/Correto! \+10 XP/i)).toBeInTheDocument();
    });

    expect(answerMock).toHaveBeenCalledWith(
      "test-jwt-token",
      expect.objectContaining({
        question_id: "q_test_light_001",
        selected: "luz",
      })
    );
  });

  it("mostra mensagem quando sessão vazia", async () => {
    sessionMock.mockResolvedValueOnce({
      count: 0,
      native_lang: "pt",
      questions: [],
      mode: "session",
    });

    renderReview();

    await waitFor(() => {
      expect(screen.getByText(/Nenhuma palavra vencida/i)).toBeInTheDocument();
    });
  });
});
