import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const navSections = [
  { key: 'dashboard', label: 'Dashboard', path: '/dashboard', roles: ['admin','principal','hod','faculty','student','accountant','hr','librarian'] },
  { key: 'students', label: 'Students', path: '/students', roles: ['admin','principal','hod','faculty','accountant','hr'] },
  { key: 'admission', label: 'Admission', path: '/admission', roles: ['admin','principal','hod','accountant'] },
  { key: 'attendance', label: 'Attendance', path: '/attendance', roles: ['admin','faculty','student'] },
  { key: 'fees', label: 'Fees', path: '/fees', roles: ['admin','accountant','student'] },
  { key: 'exams', label: 'Exams', path: '/exams', roles: ['admin','hod','faculty','student'] },
  { key: 'hrms', label: 'HRMS', path: '/hrms', roles: ['admin','principal','hod','hr'] },
  { key: 'payroll', label: 'Payroll', path: '/payroll', roles: ['admin','hr'] },
  { key: 'library', label: 'Library', path: '/library', roles: ['admin','librarian','student'] },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const menu = navSections.filter((item) => item.roles.includes(user?.role));

  return (
    <aside className="w-72 border-r border-border bg-panel p-6 text-sm text-white">
      <div className="mb-10">
        <div className="mb-4 text-xl font-semibold text-white">CampusPro ERP</div>
        <div className="rounded-2xl bg-surface p-4">
          <div className="text-sm text-muted">Signed in as</div>
          <div className="mt-1 font-semibold">{user?.first_name} {user?.last_name}</div>
          <div className="mt-1 text-xs uppercase tracking-[0.2em] text-accent">{user?.role}</div>
        </div>
      </div>

      <nav className="space-y-2">
        {menu.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={({ isActive }) =>
              `block rounded-2xl px-4 py-3 transition ${isActive ? 'bg-accent text-surface' : 'text-muted hover:bg-surface/60 hover:text-white'}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-10 border-t border-border pt-5">
        <button
          onClick={logout}
          className="w-full rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-500"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
