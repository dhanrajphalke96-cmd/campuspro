import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const staffColumns = [
  { key: 'employee_id', label: 'Employee ID' },
  { key: 'user', label: 'Name', render: (_, row) => `${row.user?.first_name || '-'} ${row.user?.last_name || ''}` },
  { key: 'designation', label: 'Designation' },
  { key: 'department', label: 'Department', render: (_, row) => row.department?.name || '-' },
  { key: 'is_active', label: 'Active', render: (value) => (value ? 'Yes' : 'No') },
];

const leaveColumns = [
  { key: 'staff', label: 'Staff', render: (_, row) => row.staff?.employee_id || '-' },
  { key: 'leave_type', label: 'Type', render: (_, row) => row.leave_type?.name || '-' },
  { key: 'from_date', label: 'From' },
  { key: 'to_date', label: 'To' },
  { key: 'status', label: 'Status' },
];

export default function HRMSPage() {
  const [staff, setStaff] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const { showToast } = useToast();

  const loadData = async () => {
    setLoading(true);
    try {
      const [staffRes, leavesRes] = await Promise.all([
        api.get('staff/', { params: { search, page_size: 50 } }),
        api.get('leaves/', { params: { search, page_size: 50 } }),
      ]);
      setStaff(staffRes.data.results || staffRes.data);
      setLeaves(leavesRes.data.results || leavesRes.data);
    } catch (error) {
      showToast('Unable to load HR data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search]);

  return (
    <div className="space-y-8">
      <div className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">HRMS</h1>
            <p className="text-sm text-muted">Staff directory, leave approvals, and directory metrics.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search staff or leave requests"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>
      </div>

      <div className="space-y-6">
        <section className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
          <h2 className="text-xl font-semibold">Staff Directory</h2>
          <div className="mt-5">
            <DataTable columns={staffColumns} data={staff} sortKey="employee_id" sortOrder="asc" />
          </div>
        </section>

        <section className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
          <h2 className="text-xl font-semibold">Leave Applications</h2>
          <div className="mt-5">
            <DataTable columns={leaveColumns} data={leaves} sortKey="from_date" sortOrder="desc" />
          </div>
        </section>
      </div>
      {loading && <p className="text-sm text-muted">Loading HRMS records…</p>}
    </div>
  );
}
