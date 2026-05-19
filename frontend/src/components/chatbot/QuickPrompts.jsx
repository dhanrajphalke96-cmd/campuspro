export default function QuickPrompts({ prompts, onSelect }) {
  if (!prompts || prompts.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <div className="text-xs uppercase tracking-[0.2em] text-white/50">Suggested prompts</div>
      <div className="flex flex-wrap gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onSelect(prompt)}
            className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white transition hover:bg-white/10"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
