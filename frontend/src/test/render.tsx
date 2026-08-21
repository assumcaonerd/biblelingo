import { type ReactElement, type ReactNode } from "react";
import { render, type RenderOptions } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { createContext, useContext, useMemo } from "react";
import type { User } from "../types/api";
import { mockUser } from "./fixtures";

type AuthState = {
  token: string | null;
  user: User | null;
  ready: boolean;
  sessionError: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, native?: string) => Promise<void>;
  logout: () => void;
};

const TestAuthContext = createContext<AuthState | null>(null);

/** Provider de auth para testes; não chama GET /v1/me. */
export function TestAuthProvider({
  children,
  token = "test-jwt-token",
  user = mockUser,
}: {
  children: ReactNode;
  token?: string | null;
  user?: User | null;
}) {
  const value = useMemo<AuthState>(
    () => ({
      token,
      user,
      ready: true,
      sessionError: null,
      login: async () => undefined,
      register: async () => undefined,
      logout: () => undefined,
    }),
    [token, user]
  );

  return (
    <TestAuthContext.Provider value={value}>{children}</TestAuthContext.Provider>
  );
}

// Utilitário de teste, não participa de Fast Refresh em produção.
// eslint-disable-next-line react-refresh/only-export-components
export function useTestAuth() {
  const ctx = useContext(TestAuthContext);
  if (!ctx) throw new Error("useTestAuth outside provider");
  return ctx;
}

type Options = Omit<RenderOptions, "wrapper"> & {
  route?: string;
  token?: string | null;
  user?: User | null;
};

/**
 * Render com MemoryRouter + auth de teste.
 * Os testes devem mockar `../auth` useAuth para usar useTestAuth,
 * ou mockar o módulo api diretamente.
 */
// Utilitário de teste, não participa de Fast Refresh em produção.
// eslint-disable-next-line react-refresh/only-export-components
export function renderWithProviders(ui: ReactElement, options: Options = {}) {
  const { route = "/", token, user, ...rest } = options;

  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <MemoryRouter initialEntries={[route]}>
        <TestAuthProvider token={token} user={user}>
          {children}
        </TestAuthProvider>
      </MemoryRouter>
    );
  }

  return render(ui, { wrapper: Wrapper, ...rest });
}
