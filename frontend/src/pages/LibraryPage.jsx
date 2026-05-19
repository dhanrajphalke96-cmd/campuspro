import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const columns = [
  { key: 'title', label: 'Title' },
  { key: 'author', label: 'Author' },
  { key: 'isbn', label: 'ISBN' },
  { key: 'category', label: 'Category' },
  { key: 'available_copies', label: 'Available Copies' },
  { key: 'shelf_number', label: 'Shelf' },
];

export default function LibraryPage() {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const loadBooks = async () => {
    setLoading(true);
    try {
      const response = await api.get('books/', { params: { search, page_size: 50 } });
      setBooks(response.data.results || response.data);
    } catch (error) {
      showToast('Unable to load library catalog', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, [search]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Library Management</h1>
            <p className="text-sm text-muted">Search books, check availability, and manage catalog records.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title, author, or ISBN"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>
      </div>
      <DataTable columns={columns} data={books} sortKey="title" sortOrder="asc" />
      {loading && <p className="text-sm text-muted">Loading library records…</p>}
    </div>
  );
}
