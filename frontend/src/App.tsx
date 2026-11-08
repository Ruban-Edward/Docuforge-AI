import { createContext, useContext, useEffect, useMemo, useState, type FormEvent } from 'react';
import { Navigate, NavLink, Outlet, Route, Routes, useLocation } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminApi, authApi, departmentsApi, templatesApi, usersApi } from './api';
import type { Department, Stats, Template, User } from './types';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('docuforge_token'));

  useEffect(() => {
    if (token) localStorage.setItem('docuforge_token', token);
    else localStorage.removeItem('docuforge_token');
  }, [token]);

  const value = useMemo<AuthContextValue>(
    () => ({ user, token, setUser, setToken, logout: () => { setUser(null); setToken(null); } }),
    [user, token],
  );

  return (
    <AuthContext.Provider value={value}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="departments" element={<DepartmentsPage />} />
            <Route path="templates" element={<TemplatesPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthContext.Provider>
  );
}

function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('AuthContext not found');
  return context;
}

function ProtectedRoute() {
  const { token } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

function LoginPage() {
  const { setToken, setUser } = useAuth();
  const [email, setEmail] = useState('admin@docuforge.ai');
  const [password, setPassword] = useState('DocuForgeAdmin2026!');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      const payload = await authApi.login(email, password);
      setToken(payload.access_token);
      setUser({
        id: 'seed-admin',
        email,
        username: 'admin',
        full_name: 'System Administrator',
        role_name: 'super_admin',
        is_active: true,
        is_verified: true,
      });
      toast.success('Login successful');
      window.location.href = '/';
    } catch {
      toast.error('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-lg">
        <h1 className="mb-2 text-2xl font-bold text-slate-900">DocuForge AI</h1>
        <p className="mb-6 text-sm text-slate-600">Sign in to continue</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500" />
          </div>
          <button type="submit" disabled={loading} className="w-full rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}

function Layout() {
  const { logout, user } = useAuth();
  const navItems = [
    { to: '/', label: 'Dashboard' },
    { to: '/users', label: 'Users' },
    { to: '/departments', label: 'Departments' },
    { to: '/templates', label: 'Templates' },
    { to: '/settings', label: 'Settings' },
  ];

  return (
    <div className="flex min-h-screen bg-slate-100 text-slate-900">
      <aside className="w-64 bg-slate-900 text-white">
        <div className="px-6 py-5 text-xl font-bold">DocuForge AI</div>
        <nav className="space-y-1 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `block rounded-lg px-3 py-2 text-sm font-medium ${isActive ? 'bg-slate-700 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="flex-1">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
          <div className="text-sm text-slate-500">Phase 1 Workspace</div>
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-slate-700">{user?.full_name || user?.email}</span>
            <button onClick={logout} className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700">Logout</button>
          </div>
        </header>
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      try { setStats(await adminApi.stats()); } finally { setLoading(false); }
    };
    run();
  }, []);

  const cards = [
    { label: 'Users', value: stats?.total_users ?? 0 },
    { label: 'Templates', value: stats?.total_templates ?? 0 },
    { label: 'Documents', value: stats?.total_documents ?? 0 },
    { label: 'Departments', value: stats?.total_departments ?? 0 },
  ];

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Dashboard</h2>
      {loading ? <div>Loading...</div> : (
        <div className="grid gap-4 md:grid-cols-4">
          {cards.map((card) => (
            <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="text-sm text-slate-500">{card.label}</div>
              <div className="mt-4 text-3xl font-bold text-slate-900">{card.value}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  useEffect(() => {
    const run = async () => {
      try { setUsers(await usersApi.list()); } catch { toast.error('Unable to load users'); }
    };
    run();
  }, []);

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Users</h2>
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-700"><tr><th className="px-4 py-3">Email</th><th className="px-4 py-3">Role</th><th className="px-4 py-3">Status</th></tr></thead>
          <tbody>{users.map((user) => <tr key={user.id} className="border-t border-slate-200"><td className="px-4 py-3">{user.email}</td><td className="px-4 py-3">{user.role_name}</td><td className="px-4 py-3">{user.is_active ? 'Active' : 'Inactive'}</td></tr>)}</tbody>
        </table>
      </div>
    </div>
  );
}

function DepartmentsPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  useEffect(() => {
    const run = async () => {
      try { setDepartments(await departmentsApi.list()); } catch { toast.error('Unable to load departments'); }
    };
    run();
  }, []);

  return (<div><h2 className="mb-6 text-2xl font-bold">Departments</h2><div className="space-y-3">{departments.map((department) => <div key={department.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="font-semibold">{department.name}</div><div className="text-sm text-slate-500">{department.code || 'No code'}</div></div>)}</div></div>);
}

function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  useEffect(() => {
    const run = async () => {
      try { setTemplates(await templatesApi.list()); } catch { toast.error('Unable to load templates'); }
    };
    run();
  }, []);

  return (<div><h2 className="mb-6 text-2xl font-bold">Templates</h2><div className="grid gap-4 md:grid-cols-2">{templates.map((template) => <div key={template.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="text-lg font-semibold">{template.name}</div><div className="mt-1 text-sm text-slate-500">{template.code}</div><div className="mt-3 text-sm text-slate-600">{template.description || 'No description'}</div></div>)}</div></div>);
}

function SettingsPage() {
  return (<div><h2 className="mb-6 text-2xl font-bold">Settings</h2><div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"><p className="text-slate-600">Application settings and upcoming admin configuration will appear here.</p></div></div>);
}

export default App;
