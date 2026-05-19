import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api } from './api'

type User = { id: number; email: string; full_name: string }

type AuthState = {
  user: User | null
  loading: boolean
  login: (email: string, password: string, remember: boolean) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const { data } = await api.get<User>('/auth/me')
      setUser(data)
    } catch {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshUser()
  }, [refreshUser])

  const login = useCallback(async (email: string, password: string, remember: boolean) => {
    const { data } = await api.post<{ access_token: string }>('/auth/login', {
      email,
      password,
      remember_me: remember,
    })
    localStorage.setItem('token', data.access_token)
    await refreshUser()
  }, [refreshUser])

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      await api.post('/auth/register', { email, password, full_name: fullName })
      await login(email, password, true)
    },
    [login],
  )

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
    void api.post('/auth/logout').catch(() => {})
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshUser }),
    [user, loading, login, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth outside provider')
  return ctx
}
