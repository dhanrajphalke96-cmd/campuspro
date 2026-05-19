import { useToast } from '../contexts/ToastContext';

export default function Toast() {
  const { toast } = useToast();

  if (!toast.visible) {
    return null;
  }

  const color = toast.type === 'error' ? 'bg-red-500' : toast.type === 'success' ? 'bg-emerald-500' : 'bg-sky-500';

  return (
    <div className={`fixed right-6 top-6 z-50 rounded-2xl px-5 py-4 shadow-2xl shadow-black/40 ${color} text-white`}>
      {toast.message}
    </div>
  );
}
