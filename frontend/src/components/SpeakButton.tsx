import { useState } from "react";

type SpeakButtonProps = {
  text: string;
  lang?: string;
  label?: string;
  rate?: number;
  className?: string;
};

/**
 * Pronúncia via Web Speech API.
 * Não bloqueia a sessão se o navegador não suportar ou falhar.
 */
export function SpeakButton({
  text,
  lang = "en-US",
  label = "Ouvir",
  rate = 0.9,
  className = "secondary",
}: SpeakButtonProps) {
  const [speaking, setSpeaking] = useState(false);
  const [error, setError] = useState("");

  function speak() {
    setError("");
    const value = text.trim();
    if (!value) return;

    if (typeof window === "undefined" || !window.speechSynthesis) {
      setError("Áudio indisponível neste navegador");
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(value);
    utterance.lang = lang;
    utterance.rate = rate;

    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => {
      setSpeaking(false);
      setError("Não foi possível reproduzir");
    };

    try {
      window.speechSynthesis.speak(utterance);
    } catch {
      setSpeaking(false);
      setError("Não foi possível reproduzir");
    }
  }

  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem" }}>
      <button
        type="button"
        className={className}
        onClick={speak}
        disabled={speaking || !text.trim()}
        title={error || label}
      >
        {speaking ? "…" : label}
      </button>
      {error && (
        <span className="muted" style={{ fontSize: "0.8rem" }}>
          {error}
        </span>
      )}
    </span>
  );
}
