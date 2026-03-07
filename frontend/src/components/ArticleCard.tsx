import type { Article } from "../api/client";

interface Props {
  article: Article;
  isPlaying: boolean;
  onPlay: () => void;
}

export default function ArticleCard({ article, isPlaying, onPlay }: Props) {
  return (
    <div
      className={`rounded-xl p-4 transition-colors cursor-pointer
        ${isPlaying ? "bg-red-900/30 ring-1 ring-red-600" : "bg-neutral-900 hover:bg-neutral-800"}`}
      onClick={article.audio_url ? onPlay : undefined}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-base leading-snug truncate text-white">
            {article.title}
          </h3>
          {article.author && (
            <p className="text-sm text-neutral-400 mt-1">{article.author}</p>
          )}
          <div className="flex items-center gap-3 mt-2 text-xs text-neutral-500">
            <span>{article.date}</span>
            <span>{article.word_count} words</span>
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-red-500 hover:text-red-400 transition-colors"
            >
              Source ↗
            </a>
          </div>
        </div>

        {article.audio_url ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onPlay();
            }}
            className={`shrink-0 w-10 h-10 rounded-full flex items-center justify-center
              transition-colors ${isPlaying ? "bg-red-600" : "bg-neutral-800 hover:bg-neutral-700 border border-neutral-700"}`}
          >
            {isPlaying ? (
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="4" width="4" height="16" />
                <rect x="14" y="4" width="4" height="16" />
              </svg>
            ) : (
              <svg className="w-4 h-4 ml-0.5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <polygon points="5,3 19,12 5,21" />
              </svg>
            )}
          </button>
        ) : (
          <span className="text-xs text-neutral-600 shrink-0 mt-1">No audio</span>
        )}
      </div>
    </div>
  );
}
