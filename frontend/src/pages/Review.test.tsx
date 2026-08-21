import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { render } from "@testing-library/react";
import { Review } from "./Review";
import {
  mockDueReviews,
  mockReviewCorrect,
  mockUser,
} from "../test/fixtures";

const dueMock = vi.fn();
const answerMock = vi.fn();

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      dueReviews: (...args: unknown[]) => dueMock(...args),
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

// SpeakButton usa speechSynthesis; evita ruído nos testes.
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
    dueMock.mockReset();
    answerMock.mockReset();
  });

  it("carrega pergunta due e opções", async () => {
    dueMock.mockResolvedValueOnce(mockDueReviews);

    renderReview();

    expect(screen.getByText(/Carregando palavras vencidas/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/light/i)).toBeInTheDocument();
    });

    expect(screen.getByRole("button", { name: "luz" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "escuridão" })).toBeInTheDocument();
    expect(dueMock).toHaveBeenCalledWith("test-jwt-token", 5, "pt");
  });

  it("ao acertar mostra feedback de XP", async () => {
    const user = userEvent.setup();
    dueMock.mockResolvedValueOnce(mockDueReviews);
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
        word: "light",
        selected: "luz",
        native_lang: "pt",
      })
    );
  });

  it("mostra mensagem quando não há palavras", async () => {
    dueMock.mockResolvedValueOnce({ count: 0, native_lang: "pt", questions: [] });

    renderReview();

    await waitFor(() => {
      expect(
        screen.getByText(/Nenhuma palavra para revisar agora/i)
      ).toBeInTheDocument();
    });
  });
});
