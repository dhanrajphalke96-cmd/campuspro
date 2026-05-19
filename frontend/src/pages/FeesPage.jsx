import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const columns = [
  { key: 'receipt_number', label: 'Receipt No' },
  { key: 'student', label: 'Student', render: (_, row) => row.student?.enrollment_no || '-' },
  { key: 'fee_structure', label: 'Fee Structure', render: (_, row) => row.fee_structure?.course?.name || '-' },
  { key: 'amount_paid', label: 'Amount Paid' },
  { key: 'status', label: 'Status' },
  { key: 'paid_at', label: 'Paid On' },
];

export default function FeesPage() {
  const [payments, setPayments] = useState([]);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('paid_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const loadPayments = async () => {
    setLoading(true);
    try {
      const response = await api.get('fees/', {
        params: {
          search,
          ordering: sortOrder === 'asc' ? sortKey : `-${sortKey}`,
          page_size: 50,
        },
      });
      setPayments(response.data.results || response.data);
    } catch (error) {
      showToast('Unable to fetch fee records', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPayments();
  }, [search, sortKey, sortOrder]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Fees Management</h1>
            <p className="text-sm text-muted">Monitor payments, receipts, and overdue activity.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by receipt number or student"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>
      </div>
      <DataTable
        columns={columns}
        data={payments}
        sortKey={sortKey}
        sortOrder={sortOrder}
        onSort={(key, order) => {
          setSortKey(key);
          setSortOrder(order);
        }}
      />
      {loading && <p className="text-sm text-muted">Loading fee payments…</p>}
    </div>
  );
}
