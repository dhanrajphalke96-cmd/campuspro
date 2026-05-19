import { useState, useEffect } from 'react';
import useChatbot from './useChatbot';
import ChatPanel from './ChatPanel';

export default function ChatWidget({ role, username }) {
  const [open, setOpen] = useState(false);
  const {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
    rolePrompts,
    unread,
  } = useChatbot(role, username);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  return (
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end">
      <button
        type="button"
        className="group flex h-14 w-14 items-center justify-center rounded-full bg-accent text-surface shadow-xl shadow-black/30 transition hover:scale-105"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Toggle ERP Assistant"
      >
        <span className="text-2xl">🤖</span>
        {unread > 0 && !open && (
          <span className="absolute right-0 top-0 flex h-6 min-w-[1.5rem] items-center justify-center rounded-full bg-red-500 px-1.5 text-[0.65rem] font-semibold text-white">
            {unread}
          </span>
        )}
      </button>

      {open && (
        <ChatPanel
          role={role}
          username={username}
          messages={messages}
          loading={loading}
          error={error}
          onSend={sendMessage}
          onClear={clearChat}
          prompts={rolePrompts}
          onClose={() => setOpen(false)}
        />
      )}
    </div>
  );
}
