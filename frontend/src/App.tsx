import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import { AuthPage } from "./pages/AuthPage";
import { Dashboard } from "./pages/Dashboard";
import { Reader } from "./pages/Reader";
import { Review } from "./pages/Review";

function Protected({ children }: { children: React.ReactNode }) {
  const { token, ready } = useAuth();
  if (!ready) {
    return <p className="muted">Validando sessão…</p>;
  }
  if (!token) return <Navigate to="/auth" replace />;
  return <>{children}</>;
}

function Shell() {
  const { token, user, ready, sessionError, logout } = useAuth();

  if (!ready) {
    return (
      <div className="app-shell">
        <p className="muted">Carregando…</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <nav className="nav">
        <div className="nav-brand">BibleLingo</div>
        <div className="nav-links">
          {token ? (
            <>
              <NavLink to="/" end>
                Início
              </NavLink>
              <NavLink to="/read">Ler</NavLink>
              <NavLink to="/review">Praticar</NavLink>
              <span className="muted" style={{ fontSize: "0.85rem" }}>
                {user?.email}
              </span>
              <button type="button" onClick={logout}>
                Sair
              </button>
            </>
          ) : (
            <NavLink to="/auth">Entrar</NavLink>
          )}
        </div>
      </nav>

      {sessionError && (
        <p className={token ? "muted" : "error"} style={{ marginTop: 0 }}>
          {sessionError}
        </p>
      )}

      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route
          path="/"
          element={
            <Protected>
              <Dashboard />
            </Protected>
          }
        />
        <Route
          path="/read"
          element={
            <Protected>
              <Reader />
            </Protected>
          }
        />
        <Route
          path="/review"
          element={
            <Protected>
              <Review />
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  );
}
