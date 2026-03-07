import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { AdminSettings, Portal, PortalTTSSettings } from "../api/client";
import {
  adminLogin,
  fetchAdminSettings,
  updatePortalSettings,
  fetchPortals,
  triggerScrape,
} from "../api/client";

export default function Admin() {
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [authed, setAuthed] = useState(false);
  const [loginError, setLoginError] = useState(false);

  const [portals, setPortals] = useState<Portal[]>([]);
  const [, setAllSettings] = useState<AdminSettings>({});
  const [drafts, setDrafts] = useState<Record<string, PortalTTSSettings>>({});
  const [saving, setSaving] = useState<string | null>(null);
  const [scraping, setScraping] = useState<string | null>(null);
  const [scrapeError, setScrapeError] = useState<Record<string, string>>({});
  const [toast, setToast] = useState("");

  const flash = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3000);
  };

  const handleLogin = async () => {
    const ok = await adminLogin(password);
    if (ok) {
      setAuthed(true);
      setLoginError(false);
      const [p, s] = await Promise.all([
        fetchPortals(),
        fetchAdminSettings(password),
      ]);
      setPortals(p);
      setAllSettings(s);
      setDrafts(JSON.parse(JSON.stringify(s)));
    } else {
      setLoginError(true);
    }
  };

  const updateDraft = (
    portalId: string,
    field: keyof PortalTTSSettings,
    value: string
  ) => {
    setDrafts((prev) => ({
      ...prev,
      [portalId]: { ...prev[portalId], [field]: value },
    }));
  };

  const handleSave = async (portalId: string) => {
    setSaving(portalId);
    try {
      const updated = await updatePortalSettings(
        portalId,
        password,
        drafts[portalId]
      );
      setAllSettings(updated);
      setDrafts(JSON.parse(JSON.stringify(updated)));
      flash(`${portalId} settings saved`);
    } catch {
      flash("Failed to save");
    } finally {
      setSaving(null);
    }
  };

  const handleScrape = async (portalId: string) => {
    setScraping(portalId);
    setScrapeError((prev) => ({ ...prev, [portalId]: "" }));
    try {
      const res = await triggerScrape(portalId, password);
      if (res.error) {
        setScrapeError((prev) => ({ ...prev, [portalId]: res.error! }));
        flash(`Scraped ${res.articles_processed} articles (stopped early)`);
      } else {
        flash(`Scraped ${res.articles_processed} articles from ${portalId}`);
      }
    } catch {
      setScrapeError((prev) => ({ ...prev, [portalId]: "Request failed — check backend logs" }));
    } finally {
      setScraping(null);
    }
  };

  // ---------- Login screen ----------
  if (!authed) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen px-4">
        <h1 className="text-2xl font-bold mb-6 text-white">Admin Login</h1>
        <div className="w-full max-w-xs space-y-4">
          <input
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setLoginError(false);
            }}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            placeholder="Password"
            className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-4 py-3
              text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-red-600"
          />
          {loginError && (
            <p className="text-red-500 text-sm text-center">Wrong password</p>
          )}
          <button
            onClick={handleLogin}
            className="w-full bg-red-700 hover:bg-red-600 py-3 rounded-xl
              font-semibold transition-colors"
          >
            Log In
          </button>
          <button
            onClick={() => navigate("/")}
            className="w-full text-neutral-500 hover:text-neutral-300 text-sm
              transition-colors text-center"
          >
            &larr; Back
          </button>
        </div>
      </div>
    );
  }

  // ---------- Admin dashboard ----------
  return (
    <div className="max-w-xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={() => navigate("/")}
          className="text-neutral-400 hover:text-white transition-colors"
        >
          &larr; Back
        </button>
        <h1 className="text-xl font-bold text-white">Admin</h1>
        <div className="w-12" />
      </div>

      {toast && (
        <div className="mb-6 bg-neutral-800 border border-neutral-700 text-white
          text-sm px-4 py-3 rounded-xl text-center">
          {toast}
        </div>
      )}

      {/* ---- Manual scrape ---- */}
      <section className="mb-10">
        <h2 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-4">
          Manual Scrape
        </h2>
        <div className="flex gap-3">
          {portals.map((p) => (
            <button
              key={p.id}
              onClick={() => handleScrape(p.id)}
              disabled={scraping !== null}
              className="flex-1 bg-neutral-900 border border-neutral-700 hover:bg-neutral-800
                disabled:opacity-50 py-3 rounded-xl font-semibold text-sm transition-colors"
            >
              {scraping === p.id ? "Scraping..." : `Scrape ${p.name}`}
            </button>
          ))}
        </div>
        {Object.entries(scrapeError).map(([id, msg]) =>
          msg ? (
            <p key={id} className="mt-3 text-sm text-red-400 break-all">
              {id}: {msg}
            </p>
          ) : null
        )}
      </section>

      {/* ---- Per-portal TTS settings ---- */}
      {portals.map((p) => {
        const draft = drafts[p.id];
        if (!draft) return null;

        return (
          <section key={p.id} className="mb-8">
            <h2 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-4">
              TTS &mdash; {p.name}
            </h2>

            <div className="space-y-4">
              {/* Engine toggle */}
              <div className="flex gap-3">
                {(["gtts", "elevenlabs", "gemini"] as const).map((val) => (
                  <button
                    key={val}
                    onClick={() => updateDraft(p.id, "tts_engine", val)}
                    className={`flex-1 py-3 rounded-xl text-sm font-semibold border transition-colors
                      ${draft.tts_engine === val
                        ? "bg-red-700 border-red-600 text-white"
                        : "bg-neutral-900 border-neutral-700 text-neutral-300 hover:bg-neutral-800"
                      }`}
                  >
                    {val === "gtts" ? "gTTS (Free)" : val === "elevenlabs" ? "ElevenLabs" : "Gemini"}
                  </button>
                ))}
              </div>

              {/* ElevenLabs fields */}
              {draft.tts_engine === "elevenlabs" && (
                <div className="space-y-3 bg-neutral-900 border border-neutral-800 rounded-xl p-5">
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1.5">
                      API Key
                    </label>
                    <input
                      type="password"
                      value={draft.elevenlabs_api_key}
                      onChange={(e) =>
                        updateDraft(p.id, "elevenlabs_api_key", e.target.value)
                      }
                      placeholder="xi-..."
                      className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2.5
                        text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-red-600"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1.5">
                      Voice ID (optional)
                    </label>
                    <input
                      type="text"
                      value={draft.elevenlabs_voice_id}
                      onChange={(e) =>
                        updateDraft(p.id, "elevenlabs_voice_id", e.target.value)
                      }
                      placeholder="Leave blank for default"
                      className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2.5
                        text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-red-600"
                    />
                  </div>
                </div>
              )}

              {/* Gemini fields */}
              {draft.tts_engine === "gemini" && (
                <div className="space-y-3 bg-neutral-900 border border-neutral-800 rounded-xl p-5">
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1.5">
                      API Key
                    </label>
                    <input
                      type="password"
                      value={draft.gemini_api_key}
                      onChange={(e) =>
                        updateDraft(p.id, "gemini_api_key", e.target.value)
                      }
                      placeholder="AIza..."
                      className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2.5
                        text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-red-600"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-neutral-400 mb-1.5">
                      Voice Name (optional)
                    </label>
                    <input
                      type="text"
                      value={draft.gemini_voice_name}
                      onChange={(e) =>
                        updateDraft(p.id, "gemini_voice_name", e.target.value)
                      }
                      placeholder="Kore, Aoede, Charon, Fenrir, Puck..."
                      className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2.5
                        text-sm text-white placeholder-neutral-600 focus:outline-none focus:border-red-600"
                    />
                  </div>
                </div>
              )}

              <button
                onClick={() => handleSave(p.id)}
                disabled={saving !== null}
                className="w-full bg-red-700 hover:bg-red-600 disabled:opacity-50 py-3
                  rounded-xl font-semibold transition-colors"
              >
                {saving === p.id ? "Saving..." : `Save ${p.name} Settings`}
              </button>
            </div>
          </section>
        );
      })}
    </div>
  );
}
