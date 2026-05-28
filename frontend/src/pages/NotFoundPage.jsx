import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="grid min-h-screen place-items-center bg-surface px-6">
      <div className="max-w-xl rounded-3xl border border-border bg-panel p-10 text-center shadow-2xl shadow-black/30">
        <h1 className="text-6xl font-bold">404</h1>
        <p className="mt-4 text-xl font-semibold">Page not found</p>
        <p className="mt-3 text-muted">The page you are looking for does not exist or you do not have permission to view it.</p>
        <Link to="/dashboard" className="mt-6 inline-block rounded-2xl bg-accent px-6 py-3 text-sm font-semibold text-surface transition hover:bg-accent/90">
          Return to dashboard
        </Link>
      </div>
    </div>
  );
}
