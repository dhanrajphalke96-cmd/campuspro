import { useEffect, useState } from 'react';
import { BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, PieChart, Pie, Cell } from 'recharts';
import api from '../api/axios';
import { useToast } from '../contexts/ToastContext';

const chartColors = ['#8b5cf6', '#0ea5e9', '#22c55e', '#f97316', '#f43f5e'];

export default function DashboardPage() {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [students, admissions, fees, exams] = await Promise.all([
          api.get('students/?page_size=1'),
          api.get('admissions/?page_size=1'),
          api.get('fees/?page_size=1'),
          api.get('exams/?page_size=1'),
        ]);
        setStats({
          students: students.data.count,
          admissions: admissions.data.count,
          fees: fees.data.count,
          exams: exams.data.count,
        });
      } catch (error) {
        showToast('Unable to load dashboard metrics', 'error');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [showToast]);

  const keyFigures = [
    { label: 'Students', value: stats.students || 0 },
    { label: 'Admissions', value: stats.admissions || 0 },
    { label: 'Fees Records', value: stats.fees || 0 },
    { label: 'Exams', value: stats.exams || 0 },
  ];

  const chartData = [
    { name: 'Students', value: stats.students || 0 },
    { name: 'Admissions', value: stats.admissions || 0 },
    { name: 'Fees', value: stats.fees || 0 },
    { name: 'Exams', value: stats.exams || 0 },
  ];

  return (
    <div className="space-y-8">
      <div className="rounded-3xl border border-border bg-panel p-8 shadow-lg shadow-black/10">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Dashboard</h2>
            <p className="text-sm text-muted">Role-based analytics and system KPIs.</p>
          </div>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {keyFigures.map((item) => (
            <div key={item.label} className="rounded-3xl bg-surface p-6 shadow-inner shadow-black/5">
              <div className="text-sm uppercase tracking-[0.25em] text-muted">{item.label}</div>
              <div className="mt-4 text-4xl font-semibold">{loading ? '...' : item.value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-3xl border border-border bg-panel p-6">
          <div className="mb-5 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Activity Overview</h3>
            <span className="rounded-full bg-surface px-3 py-1 text-xs uppercase tracking-[0.2em] text-muted">Live</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fill: '#cbd5e1' }} />
                <YAxis tick={{ fill: '#cbd5e1' }} />
                <Tooltip />
                <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="rounded-3xl border border-border bg-panel p-6">
          <div className="mb-5">
            <h3 className="text-lg font-semibold">Role Distribution</h3>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={100} innerRadius={50}>
                  {chartData.map((entry, index) => (
                    <Cell key={entry.name} fill={chartColors[index % chartColors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </div>
  );
}
