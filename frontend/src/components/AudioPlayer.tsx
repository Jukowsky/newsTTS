import { useRef, useEffect, useState } from "react";

interface Props {
  src: string;
  title: string;
  author: string;
  onEnded: () => void;
  onNext?: () => void;
  onPrev?: () => void;
}

const SPEEDS = [0.75, 1, 1.25, 1.5, 1.75, 2];

function fmt(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function AudioPlayer({
  src,
  title,
  author,
  onEnded,
  onNext,
  onPrev,
}: Props) {
  const ref = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeed] = useState(1);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.src = src;
    el.playbackRate = speed;
    el.play().then(() => setPlaying(true)).catch(() => {});
  }, [src]);

  const toggle = () => {
    const el = ref.current;
    if (!el) return;
    if (playing) {
      el.pause();
      setPlaying(false);
    } else {
      el.play().then(() => setPlaying(true)).catch(() => {});
    }
  };

  const seek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const el = ref.current;
    if (!el) return;
    el.currentTime = Number(e.target.value);
  };

  const cycleSpeed = () => {
    const idx = SPEEDS.indexOf(speed);
    const next = SPEEDS[(idx + 1) % SPEEDS.length];
    setSpeed(next);
    if (ref.current) ref.current.playbackRate = next;
  };

  return (
    <div className="fixed bottom-0 inset-x-0 bg-neutral-900 border-t border-neutral-800 px-4 py-3 z-50">
      <audio
        ref={ref}
        onTimeUpdate={() => setCurrent(ref.current?.currentTime ?? 0)}
        onLoadedMetadata={() => setDuration(ref.current?.duration ?? 0)}
        onEnded={onEnded}
      />

      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-2">
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium truncate text-white">{title}</p>
            {author && (
              <p className="text-xs text-neutral-400 truncate">{author}</p>
            )}
          </div>

          <button
            onClick={cycleSpeed}
            className="shrink-0 text-xs font-bold bg-neutral-800 border border-neutral-700
              text-red-500 px-2.5 py-1 rounded-lg hover:bg-neutral-700 transition-colors
              tabular-nums min-w-[3.2rem] text-center"
          >
            {speed}x
          </button>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onPrev}
            disabled={!onPrev}
            className="text-neutral-400 hover:text-white disabled:opacity-30 transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <polygon points="19,20 9,12 19,4" />
              <rect x="5" y="4" width="2" height="16" />
            </svg>
          </button>

          <button
            onClick={toggle}
            className="w-10 h-10 rounded-full bg-red-700 hover:bg-red-600
              flex items-center justify-center transition-colors shrink-0"
          >
            {playing ? (
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="4" width="4" height="16" />
                <rect x="14" y="4" width="4" height="16" />
              </svg>
            ) : (
              <svg className="w-5 h-5 ml-0.5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <polygon points="5,3 19,12 5,21" />
              </svg>
            )}
          </button>

          <button
            onClick={onNext}
            disabled={!onNext}
            className="text-neutral-400 hover:text-white disabled:opacity-30 transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <polygon points="5,4 15,12 5,20" />
              <rect x="17" y="4" width="2" height="16" />
            </svg>
          </button>

          <span className="text-xs text-neutral-500 tabular-nums w-10 text-right shrink-0">
            {fmt(current)}
          </span>

          <input
            type="range"
            min={0}
            max={duration || 0}
            value={current}
            onChange={seek}
            className="flex-1 h-1 accent-red-600 cursor-pointer"
          />

          <span className="text-xs text-neutral-500 tabular-nums w-10 shrink-0">
            {fmt(duration)}
          </span>
        </div>
      </div>
    </div>
  );
}
