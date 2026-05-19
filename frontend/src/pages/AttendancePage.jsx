import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const columns = [
  { key: 'student', label: 'Student', render: (_, row) => row.student?.enrollment_no || '-' },
  { key: 'session', label: 'Session', render: (_, row) => `${row.session?.subject?.name || '-'} (${row.session?.date || '-'})` },
  { key: 'status', label: 'Status' },
  { key: 'marked_at', label: 'Marked At' },
];

export default function AttendancePage() {
  const [records, setRecords] = useState([]);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('marked_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const loadRecords = async () => {
    setLoading(true);
    try {
      const response = await api.get('attendance/', {
        params: {
          search,
          ordering: sortOrder === 'asc' ? sortKey : `-${sortKey}`,
          page_size: 50,
        },
      });
      setRecords(response.data.results || response.data);
    } catch (error) {
      showToast('Unable to load attendance', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecords();
  }, [search, sortKey, sortOrder]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Attendance Management</h1>
            <p className="text-sm text-muted">Track and analyze attendance records across subjects.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by student or subject"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>
      </div>
      <DataTable
        columns={columns}
        data={records}
        sortKey={sortKey}
        sortOrder={sortOrder}
        onSort={(key, order) => {
          setSortKey(key);
          setSortOrder(order);
        }}
      />
      {loading && <p className="text-sm text-muted">Loading attendance records…</p>}
    </div>
  );
}
