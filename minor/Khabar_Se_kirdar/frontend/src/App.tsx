import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './lib/auth'
import { I18nProvider } from './lib/i18n'
import { ProtectedRoute } from './components/ProtectedRoute'
import { DashboardLayout } from './components/DashboardLayout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import DashboardHome from './pages/DashboardHome'
import SummarizePage from './pages/SummarizePage'
import TTSPage from './pages/TTSPage'
import STTPage from './pages/STTPage'
import VideoPage from './pages/VideoPage'
import InfographicPage from './pages/InfographicPage'
import HistoryPage from './pages/HistoryPage'
import SettingsPage from './pages/SettingsPage'

function RootRedirect() {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex min-h-svh items-center justify-center text-slate-400">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" />
      </div>
    )
  }
  if (user) return <Navigate to="/app" replace />
  return <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <I18nProvider>
        <AuthProvider>
          <Toaster position="top-center" toastOptions={{ className: 'dark-toast', style: { background: '#0f172a', color: '#e2e8f0' } }} />
          <Routes>
            <Route path="/" element={<RootRedirect />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route
              path="/app"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardHome />} />
              <Route path="summarize" element={<SummarizePage />} />
              <Route path="tts" element={<TTSPage />} />
              <Route path="stt" element={<STTPage />} />
              <Route path="video" element={<VideoPage />} />
              <Route path="infographic" element={<InfographicPage />} />
              <Route path="history" element={<HistoryPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </I18nProvider>
    </BrowserRouter>
  )
}
