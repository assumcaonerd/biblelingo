import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { render } from "@testing-library/react";
import { DashboardPage } from "./Dashboard";
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

function renderDashboard() {
  return render(
    <MemoryRouter>
      <DashboardPage />
    </MemoryRouter>
  );
}

describe("DashboardPage", () => {
  beforeEach(() => {
    dashboardMock.mockReset();
  });

  it("mostra loading e depois XP, streak e taxa de acerto", async () => {
    dashboardMock.mockResolvedValueOnce(mockDashboard);

    renderDashboard();

    expect(screen.getByText(/Carregando dashboard/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("40")).toBeInTheDocument(); // XP
    });

    expect(screen.getByText("Nível")).toBeInTheDocument();
    expect(screen.getByText("Streak")).toBeInTheDocument();
    expect(screen.getByText("83.3%")).toBeInTheDocument();
    expect(screen.getByText(/2 \/ 5 revisões hoje/i)).toBeInTheDocument();
    expect(screen.getByText(/continue praticando/i)).toBeInTheDocument();
    expect(screen.getByText("light")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Ler Gênesis 1/i })).toHaveAttribute(
      "href",
      "/read"
    );
    expect(dashboardMock).toHaveBeenCalledWith("test-jwt-token");
  });

  it("exibe erro quando a API falha", async () => {
    dashboardMock.mockRejectedValueOnce(new Error("API offline"));

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText("API offline")).toBeInTheDocument();
    });
  });

  it("cumprimenta pelo prefixo do email", async () => {
    dashboardMock.mockResolvedValueOnce(mockDashboard);

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Olá, learner/i })).toBeInTheDocument();
    });
  });
});
