import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Portal } from "../api/client";
import { fetchPortals } from "../api/client";
import SolLogo from "../components/SolLogo";
import RiktpunktLogo from "../components/RiktpunktLogo";

const PORTAL_META: Record<string, { lang: string }> = {
  sol: { lang: "Turkce" },
  riktpunkt: { lang: "Svenska" },
};

function PortalLogo({ id }: { id: string }) {
  if (id === "sol") return <SolLogo className="h-8 w-auto" />;
  if (id === "riktpunkt") return <RiktpunktLogo className="h-6 w-auto text-white" />;
  return null;
}

export default function PortalSelect() {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPortals()
      .then(setPortals)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      <h1 className="text-5xl font-black mb-1 tracking-tight text-red-600">
        Redcast
      </h1>
      <p className="text-neutral-400 mb-12 text-center">
        Daily column articles, read aloud
      </p>

      {loading ? (
        <div className="text-neutral-500">Loading portals...</div>
      ) : (
        <div className="grid gap-5 w-full max-w-md">
          {portals.map((p) => {
            const meta = PORTAL_META[p.id];
            return (
              <button
                key={p.id}
                onClick={() => navigate(`/portal/${p.id}`)}
                className="bg-neutral-900 hover:bg-neutral-800 border-l-4 border-red-600
                  rounded-xl p-7 text-left shadow-lg
                  hover:scale-[1.02] active:scale-[0.98] transition-transform"
              >
                <PortalLogo id={p.id} />
                <p className="text-sm text-neutral-400 mt-3">
                  {meta?.lang ?? p.language}
                </p>
              </button>
            );
          })}
        </div>
      )}

      <button
        onClick={() => navigate("/admin")}
        className="mt-12 text-xs text-neutral-600 hover:text-neutral-400 transition-colors"
      >
        Admin
      </button>
    </div>
  );
}
