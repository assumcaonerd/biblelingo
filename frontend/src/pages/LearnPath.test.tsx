import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LearnPath } from "./LearnPath";
import { mockDashboard, mockUser } from "../test/fixtures";

const dashboardMock = vi.fn();

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      dashboard: (...args: unknown[]) => dashboardMock(...args),
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

function renderPath() {
  return render(
    <MemoryRouter>
      <LearnPath />
    </MemoryRouter>
  );
}

describe("LearnPath", () => {
  beforeEach(() => {
    dashboardMock.mockReset();
  });

  it("monta a trilha com dados reais do dashboard", async () => {
    dashboardMock.mockResolvedValueOnce(mockDashboard);

    renderPath();

    expect(screen.getByText(/Preparando sua trilha/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Unidade 2/i })).toBeInTheDocument();
    });

    expect(screen.getByText("40")).toBeInTheDocument();
    expect(screen.getByText("Palavras de vida")).toBeInTheDocument();
    expect(screen.getByText("Ouça as Escrituras")).toBeInTheDocument();
    expect(screen.getByText("Foco no contexto")).toBeInTheDocument();
    expect(screen.getByText(/8 palavras já revisadas/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Palavras de vida/i })).toHaveAttribute("href", "/read");
    expect(screen.getByRole("navigation", { name: /Navegação principal/i })).toBeInTheDocument();
    expect(dashboardMock).toHaveBeenCalledWith("test-jwt-token");
  });

  it("exibe erro amigável quando a trilha não carrega", async () => {
    dashboardMock.mockRejectedValueOnce(new Error("API offline"));

    renderPath();

    await waitFor(() => {
      expect(screen.getByText("API offline")).toBeInTheDocument();
    });
  });
});
