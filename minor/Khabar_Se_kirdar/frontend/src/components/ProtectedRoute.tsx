import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const { user, loading } = useAuth()
  const loc = useLocation()

  if (loading) {
    return (
      <div className="flex min-h-svh items-center justify-center text-slate-400">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-sky-500 border-t-transparent" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: loc.pathname }} />
  }

  return children
}
