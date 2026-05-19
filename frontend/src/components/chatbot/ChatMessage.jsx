export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const bubbleClass = isUser
    ? 'ml-auto rounded-tl-3xl rounded-tr-3xl rounded-bl-3xl bg-accent text-surface'
    : 'mr-auto rounded-tr-3xl rounded-br-3xl rounded-tl-3xl bg-white/10 text-white';

  return (
    <div className="mb-3 flex flex-col gap-2">
      <div className={`max-w-[85%] break-words px-4 py-3 text-sm ${bubbleClass}`}>
        {message.content}
      </div>
      <div className="text-[0.68rem] text-white/40">
        {isUser ? 'You' : 'Assistant'} · {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  );
}
