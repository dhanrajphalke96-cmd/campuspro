import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const columns = [
  { key: 'enrollment_no', label: 'Enrollment No' },
  { key: 'user', label: 'Student Name', render: (_, row) => `${row.user.first_name} ${row.user.last_name}` },
  { key: 'department', label: 'Department', render: (_, row) => row.department?.name || '-' },
  { key: 'course', label: 'Course', render: (_, row) => row.course?.name || '-' },
  { key: 'current_semester', label: 'Semester' },
  { key: 'is_active', label: 'Status', render: (value) => (value ? 'Active' : 'Inactive') },
];

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('enrollment_no');
  const [sortOrder, setSortOrder] = useState('asc');
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const loadStudents = async () => {
    setLoading(true);
    try {
      const response = await api.get('students/', {
        params: {
          search,
          ordering: sortOrder === 'asc' ? sortKey : `-${sortKey}`,
          page_size: 50,
        },
      });
      setStudents(response.data.results || response.data);
    } catch (error) {
      showToast('Could not load students', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, [search, sortKey, sortOrder]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Student Records</h1>
            <p className="text-sm text-muted">Search, filter, and review student profiles.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, enrollment or course"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>
      </div>
      <DataTable
        columns={columns}
        data={students}
        sortKey={sortKey}
        sortOrder={sortOrder}
        onSort={(key, order) => {
          setSortKey(key);
          setSortOrder(order);
        }}
      />
      {loading && <p className="text-sm text-muted">Loading student data…</p>}
    </div>
  );
}
