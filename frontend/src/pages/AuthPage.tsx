import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";
import type { NativeLanguage } from "../types/api";

export function AuthPage() {
  const { token, login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [native, setNative] = useState<NativeLanguage>("pt");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (token) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password, native);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha na autenticação");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="card">
        <h1>BibleLingo</h1>
        <p className="muted">Aprenda inglês lendo e ouvindo a Bíblia.</p>

        <div className="tabs">
          <button
            type="button"
            className={mode === "login" ? "active" : ""}
            onClick={() => setMode("login")}
          >
            Entrar
          </button>
          <button
            type="button"
            className={mode === "register" ? "active" : ""}
            onClick={() => setMode("register")}
          >
            Criar conta
          </button>
        </div>

        <form onSubmit={onSubmit}>
          <label>
            Email
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>
          <label>
            Senha
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />
          </label>
          {mode === "register" && (
            <label>
              Idioma nativo
              <select
                value={native}
                onChange={(e) => setNative(e.target.value as NativeLanguage)}
              >
                <option value="pt">Português</option>
                <option value="es">Español</option>
                <option value="en">English</option>
                <option value="ar">العربية</option>
                <option value="he">עברית</option>
              </select>
            </label>
          )}
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? "Aguarde…" : mode === "login" ? "Entrar" : "Criar conta"}
          </button>
        </form>
      </div>
    </div>
  );
}
