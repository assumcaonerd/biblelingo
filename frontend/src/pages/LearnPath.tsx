import { useEffect, useMemo, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { api, type Dashboard } from "../api";
import { useAuth } from "../auth";

type PathStatus = "completed" | "current" | "locked" | "reward";

type PathNode = {
  id: number;
  title: string;
  subtitle: string;
  icon: string;
  to: string;
  status: PathStatus;
  badge?: string;
};

const languageBadges: Record<string, { flag: string; label: string }> = {
  pt: { flag: "🇧🇷", label: "PT" },
  es: { flag: "🇪🇸", label: "ES" },
  en: { flag: "🇺🇸", label: "EN" },
  ar: { flag: "🌙", label: "AR" },
  he: { flag: "✡", label: "HE" },
};

function PathItem({ node }: { node: PathNode }) {
  const content = (
    <>
      <div className={`path-step path-step--${node.status}`} aria-hidden="true">
        <span className="path-step-number">{node.id}</span>
        <span className="path-step-icon">{node.status === "locked" ? "🔒" : node.icon}</span>
      </div>
      <div className="path-copy">
        <strong>{node.title}</strong>
        <span>{node.subtitle}</span>
      </div>
      {node.badge && <span className="path-badge">{node.badge}</span>}
      {node.status === "current" && <span className="path-arrow" aria-hidden="true">›</span>}
    </>
  );

  if (node.status === "locked") {
    return (
      <div className="path-item path-item--locked" aria-label={`${node.title}, bloqueada`}>
        {content}
      </div>
    );
  }

  return (
    <Link className={`path-item path-item--${node.status}`} to={node.to}>
      {content}
    </Link>
  );
}

export function LearnPath() {
  const { token, user } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    api
      .dashboard(token)
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Erro ao carregar progresso"))
      .finally(() => setLoading(false));
  }, [token]);

  const nodes = useMemo<PathNode[]>(() => {
    const percent = data?.progress.level_progress.percent ?? 0;
    const currentStep = Math.min(6, Math.max(1, Math.floor(percent / 20) + 1));

    const base = [
      { id: 1, title: "Palavras de vida", subtitle: "Aprenda palavras no contexto bíblico", icon: "📖", to: "/read" },
      { id: 2, title: "Ouça as Escrituras", subtitle: "Escute, leia e repita", icon: "🔊", to: "/read" },
      { id: 3, title: "Foco no contexto", subtitle: "Entenda a frase completa", icon: "✎", to: "/read" },
      { id: 4, title: "Quiz rápido", subtitle: "Teste o que você aprendeu", icon: "✓", to: "/review" },
      { id: 5, title: "Recompensa", subtitle: "Consolide sua sequência", icon: "🏆", to: "/profile" },
      { id: 6, title: "Desafio de versículo", subtitle: "Pratique sem pistas", icon: "📖", to: "/review" },
    ];

    return base.map((node) => {
      let status: PathStatus = "locked";
      if (node.id < currentStep) status = node.id === 5 ? "reward" : "completed";
      if (node.id === currentStep) status = node.id === 5 ? "reward" : "current";
      return {
        ...node,
        status,
        badge: node.id === 1 && node.id <= currentStep ? "+10 XP" : node.id === 5 && node.id <= currentStep ? "+20" : undefined,
      };
    });
  }, [data]);

  if (loading) {
    return <div className="learn-loading">Preparando sua trilha…</div>;
  }

  if (error || !data) {
    return (
      <div className="learn-loading">
        <p className="error">{error || "Não foi possível carregar sua trilha."}</p>
      </div>
    );
  }

  const { progress, vocabulary } = data;
  const unit = progress.level + 1;
  const unitProgress = progress.level_progress.percent;
  const dailyPercent = Math.min(100, Math.round((data.reviews_today / Math.max(1, data.daily_goal)) * 100));
  const firstName = user?.email.split("@")[0] ?? "aluno";
  const language = languageBadges[user?.native_language ?? "pt"] ?? languageBadges.pt;

  return (
    <main className="learn-path-page">
      <header className="learn-topbar">
        <div className="learn-brand-row">
          <div className="learn-brand-mark" aria-hidden="true">✝</div>
          <div className="learn-brand">Bible<span>Lingo</span></div>
          <Link className="learn-avatar" to="/profile" aria-label={`Abrir perfil de ${firstName}`}>
            {firstName.slice(0, 1).toUpperCase()}
          </Link>
        </div>

        <div className="learn-status-strip" aria-label="Seu progresso">
          <div className="status-chip"><span>{language.flag}</span><strong>{language.label}</strong></div>
          <div className="status-chip"><span>⭐</span><strong>{progress.xp}</strong><small>XP</small></div>
          <div className="status-chip"><span>🔥</span><strong>{progress.current_streak}</strong><small>dias</small></div>
          <div className="status-chip"><span>❤️</span><strong>{data.reviews_today}/{data.daily_goal}</strong><small>meta</small></div>
        </div>
      </header>

      <section className="unit-hero" aria-labelledby="unit-title">
        <div className="unit-main">
          <div className="unit-shield" aria-hidden="true"><span>{unit}</span><small>UNIDADE</small></div>
          <div>
            <p className="unit-kicker">Sua próxima etapa</p>
            <h1 id="unit-title">Unidade {unit}</h1>
            <p>Aprenda inglês lendo, ouvindo e praticando a Bíblia.</p>
          </div>
          <div className="unit-book" aria-hidden="true">📖</div>
        </div>
        <div className="unit-progress-label"><span>Progresso nesta unidade</span><strong>{unitProgress}%</strong></div>
        <div className="unit-progress-track"><div style={{ width: `${unitProgress}%` }} /></div>
      </section>

      <section className="learning-path" aria-label="Trilha de aprendizagem">
        <div className="path-line" aria-hidden="true" />
        {nodes.map((node) => <PathItem key={node.id} node={node} />)}
      </section>

      <section className="milestone-card" aria-label="Meta diária e vocabulário">
        <div className="milestone-streak"><span>🔥</span><strong>{progress.current_streak}</strong><small>dias de sequência</small></div>
        <div className="milestone-progress">
          <div className="milestone-label"><span>Próximo marco</span><strong>{data.reviews_today}/{data.daily_goal}</strong></div>
          <div className="milestone-track"><div style={{ width: `${dailyPercent}%` }} /></div>
          <small>{vocabulary.reviewed_words} palavras já revisadas</small>
        </div>
        <div className="milestone-chest" aria-hidden="true">🎁</div>
      </section>

      <nav className="learn-bottom-nav" aria-label="Navegação principal">
        <NavLink to="/" end><span>⌂</span><small>Início</small></NavLink>
        <NavLink to="/read"><span>📖</span><small>Aprender</small></NavLink>
        <NavLink to="/review"><span>✦</span><small>Praticar</small></NavLink>
        <span className="learn-nav-disabled" title="Recompensas em breve"><span>🎁</span><small>Recompensas</small></span>
        <NavLink to="/profile"><span>●</span><small>Perfil</small></NavLink>
      </nav>
    </main>
  );
}
