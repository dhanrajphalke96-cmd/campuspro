import { useEffect, useState } from 'react';
import api from '../api/axios';
import DataTable from '../components/DataTable';
import { useToast } from '../contexts/ToastContext';

const columns = [
  { key: 'application_id', label: 'Application ID' },
  { key: 'full_name', label: 'Name', render: (_, row) => `${row.first_name} ${row.last_name}` },
  { key: 'course', label: 'Course', render: (_, row) => row.course?.name || '-' },
  { key: 'academic_year', label: 'Academic Year', render: (_, row) => row.academic_year?.label || '-' },
  { key: 'status', label: 'Status' },
  { key: 'applied_at', label: 'Applied On' },
];

const defaultForm = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  date_of_birth: '',
  gender: 'male',
  category: 'general',
  address: '',
  city: '',
  state: 'Maharashtra',
  pincode: '',
  course: '',
  academic_year: '',
  previous_qualification: '',
  previous_percentage: '',
};

export default function AdmissionPage() {
  const [applications, setApplications] = useState([]);
  const [courses, setCourses] = useState([]);
  const [years, setYears] = useState([]);
  const [formData, setFormData] = useState(defaultForm);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('applied_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const { showToast } = useToast();

  const loadData = async () => {
    setLoading(true);
    try {
      const [applicationsRes, coursesRes, yearsRes] = await Promise.all([
        api.get('admissions/', {
          params: {
            search,
            ordering: sortOrder === 'asc' ? sortKey : `-${sortKey}`,
            page_size: 50,
          },
        }),
        api.get('courses/'),
        api.get('academic-years/'),
      ]);
      setApplications(applicationsRes.data.results || applicationsRes.data);
      setCourses(coursesRes.data.results || coursesRes.data);
      setYears(yearsRes.data.results || yearsRes.data);
    } catch (error) {
      showToast('Unable to load admissions data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search, sortKey, sortOrder]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await api.post('admissions/', formData);
      showToast('Application submitted successfully', 'success');
      setFormData(defaultForm);
      loadData();
    } catch (error) {
      showToast('Submission failed. Please verify required fields.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Admission Management</h1>
            <p className="text-sm text-muted">Submit new student applications and monitor merit-driven intake.</p>
          </div>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or application ID"
            className="w-full max-w-md rounded-2xl border border-border px-4 py-3"
          />
        </div>

        <form onSubmit={handleSubmit} className="grid gap-4 rounded-3xl border border-border bg-surface p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="text-sm text-muted">First name</span>
              <input
                required
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
            <label className="block">
              <span className="text-sm text-muted">Last name</span>
              <input
                required
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <label className="block">
              <span className="text-sm text-muted">Email</span>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
            <label className="block">
              <span className="text-sm text-muted">Phone</span>
              <input
                required
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
            <label className="block">
              <span className="text-sm text-muted">Date of birth</span>
              <input
                type="date"
                required
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <label className="block">
              <span className="text-sm text-muted">Course</span>
              <select
                required
                value={formData.course}
                onChange={(e) => setFormData({ ...formData, course: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              >
                <option value="">Select course</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>{course.name}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="text-sm text-muted">Academic year</span>
              <select
                required
                value={formData.academic_year}
                onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              >
                <option value="">Select year</option>
                {years.map((year) => (
                  <option key={year.id} value={year.id}>{year.label}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="text-sm text-muted">Category</span>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              >
                <option value="general">General</option>
                <option value="obc">OBC</option>
                <option value="sc">SC</option>
                <option value="st">ST</option>
                <option value="ews">EWS</option>
                <option value="nt">NT</option>
              </select>
            </label>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="text-sm text-muted">City</span>
              <input
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
            <label className="block">
              <span className="text-sm text-muted">Pincode</span>
              <input
                value={formData.pincode}
                onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
          </div>

          <div>
            <label className="block">
              <span className="text-sm text-muted">Address</span>
              <textarea
                rows="3"
                required
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="mt-2 w-full rounded-2xl border border-border px-4 py-3"
              />
            </label>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={() => setFormData(defaultForm)}
              className="rounded-2xl border border-border px-5 py-3 text-sm text-white/80 hover:bg-surface"
            >
              Reset
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-surface transition hover:bg-accent/90 disabled:opacity-70"
            >
              {submitting ? 'Submitting...' : 'Submit Application'}
            </button>
          </div>
        </form>
      </section>

      <section className="rounded-3xl border border-border bg-panel p-6 shadow-lg shadow-black/10">
        <h2 className="mb-4 text-xl font-semibold">Application List</h2>
        <DataTable
          columns={columns}
          data={applications}
          sortKey={sortKey}
          sortOrder={sortOrder}
          onSort={(key, order) => {
            setSortKey(key);
            setSortOrder(order);
          }}
        />
        {loading && <p className="mt-4 text-sm text-muted">Loading application list…</p>}
      </section>
    </div>
  );
}
