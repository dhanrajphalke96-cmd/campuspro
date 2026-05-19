import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const columns = [
  { key: 'name', label: 'Exam Name' },
  { key: 'subject', label: 'Subject', render: (_, row) => row.subject?.name || '-' },
  { key: 'exam_type', label: 'Type' },
  { key: 'date', label: 'Date' },
  { key: 'semester', label: 'Semester' },
  { key: 'is_published', label: 'Published', render: (value) => (value ? 'Yes' : 'No') },
];

export default function ExamsPage() {
  const [exams, setExams] = useState([]);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const loadExams = async () => {
    setLoading(true);
    try {
      const response = await api.get('exams/', {
        params: {
          search,
          ordering: sortOrder === 'asc' ? sortKey : `-${sortKey}`,
          page_size: 50,
        },
      });
      setExams(response.data.results || response.data);
    } catch (error) {
      showToast('Unable to load exams', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExams();
  }, [search, sortKey, sortOrder]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Examination Management</h1>
            <p className="text-sm text-muted">Review exam schedules and publication status.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search exam name or subject"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>
      </div>
      <DataTable
        columns={columns}
        data={exams}
        sortKey={sortKey}
        sortOrder={sortOrder}
        onSort={(key, order) => {
          setSortKey(key);
          setSortOrder(order);
        }}
      />
      {loading && <p className="text-sm text-muted">Loading exam schedules…</p>}
    </div>
  );
}
