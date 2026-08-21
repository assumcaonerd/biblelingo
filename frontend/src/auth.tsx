import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { ApiError, api, type User } from "./api";

const TOKEN_KEY = "biblelingo_token";
const USER_KEY = "biblelingo_user";

type AuthState = {
  token: string | null;
  user: User | null;
  ready: boolean;
  sessionError: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, native?: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

function loadStored(): { token: string | null; user: User | null } {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const raw = localStorage.getItem(USER_KEY);
    const user = raw ? (JSON.parse(raw) as User) : null;
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const stored = loadStored();
  const [token, setToken] = useState<string | null>(stored.token);
  const [user, setUser] = useState<User | null>(stored.user);
  const [ready, setReady] = useState(!stored.token);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const validating = useRef(false);

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const persist = useCallback((nextToken: string, nextUser: User) => {
    localStorage.setItem(TOKEN_KEY, nextToken);
    localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    setToken(nextToken);
    setUser(nextUser);
    setSessionError(null);
  }, []);

  // Revalida token salvo com GET /v1/me ao iniciar.
  useEffect(() => {
    if (!token) {
      setReady(true);
      return;
    }
    if (validating.current) return;
    validating.current = true;

    api
      .me(token)
      .then((profile) => {
        setUser(profile);
        localStorage.setItem(USER_KEY, JSON.stringify(profile));
        setSessionError(null);
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          clearSession();
          setSessionError("Sessão expirada. Entre novamente.");
        } else {
          // API indisponível: mantém sessão local, só avisa.
          setSessionError(
            "Não foi possível validar a sessão. Verifique se a API está no ar."
          );
        }
      })
      .finally(() => {
        validating.current = false;
        setReady(true);
      });
  }, [token, clearSession]);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await api.login(email, password);
      persist(res.access_token, res.user);
      setReady(true);
    },
    [persist]
  );

  const register = useCallback(
    async (email: string, password: string, native = "pt") => {
      const res = await api.register(email, password, native);
      persist(res.access_token, res.user);
      setReady(true);
    },
    [persist]
  );

  const logout = useCallback(() => {
    clearSession();
    setSessionError(null);
    setReady(true);
  }, [clearSession]);

  const value = useMemo(
    () => ({
      token,
      user,
      ready,
      sessionError,
      login,
      register,
      logout,
    }),
    [token, user, ready, sessionError, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
