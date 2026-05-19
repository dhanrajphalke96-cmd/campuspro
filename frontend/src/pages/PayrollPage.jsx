import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const columns = [
  { key: 'staff', label: 'Staff', render: (_, row) => row.staff?.employee_id || '-' },
  { key: 'month', label: 'Month' },
  { key: 'year', label: 'Year' },
  { key: 'net_salary', label: 'Net Salary' },
  { key: 'status', label: 'Status' },
  { key: 'paid_at', label: 'Paid On' },
];

export default function PayrollPage() {
  const [payslips, setPayslips] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const loadPayslips = async () => {
    setLoading(true);
    try {
      const response = await api.get('payslips/', { params: { search, page_size: 50 } });
      setPayslips(response.data.results || response.data);
    } catch (error) {
      showToast('Unable to load payslips', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPayslips();
  }, [search]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Payroll Management</h1>
            <p className="text-sm text-muted">Salary slips, payment status, and payroll oversight.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by employee or month"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>
      </div>
      <DataTable columns={columns} data={payslips} sortKey="year" sortOrder="desc" />
      {loading && <p className="text-sm text-muted">Loading payroll records…</p>}
    </div>
  );
}
