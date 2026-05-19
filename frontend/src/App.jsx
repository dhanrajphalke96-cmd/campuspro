import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';
import Toast from './components/Toast';
import ChatWidget from './components/chatbot/ChatWidget';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import StudentsPage from './pages/StudentsPage';
import AdmissionPage from './pages/AdmissionPage';
import AttendancePage from './pages/AttendancePage';
import FeesPage from './pages/FeesPage';
import ExamsPage from './pages/ExamsPage';
import HRMSPage from './pages/HRMSPage';
import PayrollPage from './pages/PayrollPage';
import LibraryPage from './pages/LibraryPage';
import NotFoundPage from './pages/NotFoundPage';

function AppLayout() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-surface text-white">
      <div className="flex min-h-screen">
        <Sidebar user={user} />
        <main className="flex-1 p-6 relative">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/students" element={<StudentsPage />} />
            <Route path="/admission" element={<AdmissionPage />} />
            <Route path="/attendance" element={<AttendancePage />} />
            <Route path="/fees" element={<FeesPage />} />
            <Route path="/exams" element={<ExamsPage />} />
            <Route path="/hrms" element={<HRMSPage />} />
            <Route path="/payroll" element={<PayrollPage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
          <ChatWidget role={user?.role} username={user?.username} />
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<ProtectedRoute><AppLayout /></ProtectedRoute>} />
        </Routes>
        <Toast />
      </ToastProvider>
    </AuthProvider>
  );
}
