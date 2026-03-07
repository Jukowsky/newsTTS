import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { Article } from "../api/client";
import { fetchArticles } from "../api/client";
import ArticleCard from "../components/ArticleCard";
import AudioPlayer from "../components/AudioPlayer";
import SolLogo from "../components/SolLogo";
import RiktpunktLogo from "../components/RiktpunktLogo";

export default function ArticleList() {
  const { portalId } = useParams<{ portalId: string }>();
  const navigate = useNavigate();

  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState<number | null>(null);

  const load = useCallback(() => {
    if (!portalId) return;
    setLoading(true);
    fetchArticles(portalId)
      .then(setArticles)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [portalId]);

  useEffect(() => {
    load();
  }, [load]);

  const playableArticles = articles.filter((a) => a.audio_url);

  const handlePlayAll = () => {
    if (playableArticles.length > 0) setCurrentIdx(0);
  };

  const handleEnded = () => {
    if (currentIdx !== null && currentIdx < playableArticles.length - 1) {
      setCurrentIdx(currentIdx + 1);
    } else {
      setCurrentIdx(null);
    }
  };

  const currentArticle =
    currentIdx !== null ? playableArticles[currentIdx] : null;

  return (
    <div className="max-w-2xl mx-auto px-4 pb-36 pt-6">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate("/")}
          className="text-neutral-400 hover:text-white transition-colors"
        >
          &larr; Back
        </button>
        <div className="flex items-center">
          {portalId === "sol" && <SolLogo className="h-6 w-auto" />}
          {portalId === "riktpunkt" && <RiktpunktLogo className="h-5 w-auto text-white" />}
        </div>
        <div className="w-16" />
      </div>

      {playableArticles.length > 0 && (
        <button
          onClick={handlePlayAll}
          className="w-full mb-6 bg-red-700 hover:bg-red-600 py-3 rounded-xl
            font-semibold transition-colors"
        >
          Play All ({playableArticles.length} articles)
        </button>
      )}

      {loading ? (
        <p className="text-center text-neutral-500 mt-20">Loading articles...</p>
      ) : articles.length === 0 ? (
        <p className="text-center text-neutral-400 mt-20">
          No articles yet for today.
        </p>
      ) : (
        <div className="space-y-3">
          {articles.map((a) => (
            <ArticleCard
              key={a.id}
              article={a}
              isPlaying={currentArticle?.id === a.id}
              onPlay={() => {
                const idx = playableArticles.findIndex((p) => p.id === a.id);
                if (idx >= 0) setCurrentIdx(idx);
              }}
            />
          ))}
        </div>
      )}

      {currentArticle?.audio_url && (
        <AudioPlayer
          src={currentArticle.audio_url}
          title={currentArticle.title}
          author={currentArticle.author}
          onEnded={handleEnded}
          onNext={
            currentIdx !== null && currentIdx < playableArticles.length - 1
              ? () => setCurrentIdx(currentIdx + 1)
              : undefined
          }
          onPrev={
            currentIdx !== null && currentIdx > 0
              ? () => setCurrentIdx(currentIdx - 1)
              : undefined
          }
        />
      )}
    </div>
  );
}
