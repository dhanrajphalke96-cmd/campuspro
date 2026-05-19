import { useEffect, useMemo, useRef, useState } from 'react';
import ChatMessage from './ChatMessage';
import QuickPrompts from './QuickPrompts';

export default function ChatPanel({
  role,
  username,
  messages,
  loading,
  error,
  onSend,
  onClear,
  prompts,
  onClose,
}) {
  const [draft, setDraft] = useState('');
  const listRef = useRef(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const roleLabel = useMemo(() => {
    if (!role) return 'Guest';
    return role.charAt(0).toUpperCase() + role.slice(1);
  }, [role]);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!draft.trim()) return;
    onSend(draft.trim());
    setDraft('');
  };

  return (
    <div className="mt-3 w-[380px] rounded-3xl border border-white/10 bg-surface p-3 text-white shadow-2xl shadow-black/40">
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div>
          <div className="text-lg font-semibold">ERP Assistant 🤖</div>
          <div className="text-sm text-white/70">{roleLabel} chat</div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="rounded-full bg-white/10 px-3 py-1 text-xs uppercase tracking-[0.12em] text-white/80 transition hover:bg-white/20"
            onClick={onClear}
          >
            Clear
          </button>
          <button
            type="button"
            className="rounded-full bg-white/10 px-3 py-1 text-white/90 transition hover:bg-white/20"
            onClick={onClose}
          >
            ✕
          </button>
        </div>
      </div>

      <div className="mt-3 h-[320px] overflow-y-auto rounded-3xl bg-[#111827] p-4" ref={listRef}>
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center text-sm text-white/60">
            Ask me anything about CampusPro ERP.
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={`${message.role}-${message.timestamp}-${message.id ?? Math.random()}`} message={message} />
          ))
        )}
        {loading && (
          <div className="mt-2 flex items-center gap-2 rounded-2xl bg-white/5 p-3 text-sm text-white/80">
            <div className="flex h-3 items-center gap-1">
              <span className="inline-block h-2.5 w-2.5 animate-pulse rounded-full bg-white"></span>
              <span className="inline-block h-2.5 w-2.5 animate-pulse rounded-full bg-white animation-delay-150"></span>
              <span className="inline-block h-2.5 w-2.5 animate-pulse rounded-full bg-white animation-delay-300"></span>
            </div>
            Assistant is typing...
          </div>
        )}
      </div>

      {error && (
        <div className="mt-3 rounded-2xl bg-red-500/15 p-3 text-sm text-red-200">
          {error}
        </div>
      )}

      <div className="mt-3 rounded-3xl bg-[#0f172a] p-3">
        <QuickPrompts prompts={prompts} onSelect={(value) => { onSend(value); }} />

        <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
          <input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            className="flex-1 rounded-2xl border border-white/10 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-accent"
            placeholder="Type your question..."
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                handleSubmit(event);
              }
            }}
          />
          <button
            type="submit"
            disabled={loading || !draft.trim()}
            className="rounded-2xl bg-accent px-4 py-2 text-sm font-semibold text-surface transition disabled:cursor-not-allowed disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
