import { NavLink, Outlet } from 'react-router-dom'
import {
  Film,
  History,
  Home,
  Image as ImageIcon,
  LogOut,
  Mic,
  Settings,
  Sparkles,
  Volume2,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { useI18n } from '../lib/i18n'
import { LanguageSelector } from './LanguageSelector'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
    isActive ? 'bg-sky-500/15 text-sky-300' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
  }`

export function DashboardLayout() {
  const { user, logout } = useAuth()
  const { t } = useI18n()

  const items = [
    { to: '/app', icon: Home, end: true, label: t('nav_home') },
    { to: '/app/summarize', icon: Sparkles, label: t('nav_summarize') },
    { to: '/app/tts', icon: Volume2, label: t('nav_tts') },
    { to: '/app/stt', icon: Mic, label: t('nav_stt') },
    { to: '/app/video', icon: Film, label: t('nav_video') },
    { to: '/app/infographic', icon: ImageIcon, label: t('nav_infographic') },
    { to: '/app/history', icon: History, label: t('nav_history') },
    { to: '/app/settings', icon: Settings, label: t('nav_settings') },
  ]

  return (
    <div className="flex min-h-svh">
      <aside className="sticky top-0 hidden h-svh w-64 shrink-0 flex-col border-r border-white/5 bg-slate-950/40 p-4 backdrop-blur-xl md:flex">
        <div className="mb-8 px-2">
          <div className="font-display text-lg font-semibold tracking-tight text-white">{t('brand')}</div>
          <p className="mt-1 text-xs text-slate-500">{t('tagline')}</p>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {items.map(({ to, icon: Icon, label, end }) => (
            <NavLink key={to} to={to} end={end} className={linkClass}>
              <Icon className="h-4 w-4 shrink-0 opacity-80" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto space-y-3 border-t border-white/5 pt-4">
          <LanguageSelector compact />
          <div className="rounded-xl bg-white/5 px-3 py-2 text-xs text-slate-400">
            <div className="truncate font-medium text-slate-200">{user?.full_name || user?.email}</div>
            <div className="truncate text-slate-500">{user?.email}</div>
          </div>
          <button
            type="button"
            onClick={() => logout()}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2 text-sm text-slate-300 transition hover:bg-white/5"
          >
            <LogOut className="h-4 w-4" />
            {t('logout')}
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between gap-4 border-b border-white/5 bg-slate-950/70 px-4 py-3 backdrop-blur-xl md:hidden">
          <span className="font-display font-semibold text-white">{t('brand')}</span>
          <LanguageSelector compact />
        </header>
        <main className="flex-1 p-4 pb-24 md:p-8 md:pb-8">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
            <Outlet />
          </motion.div>
        </main>
        <nav className="fixed bottom-0 left-0 right-0 z-20 flex justify-around border-t border-white/10 bg-slate-950/95 p-2 backdrop-blur-xl md:hidden">
          {items.slice(0, 6).map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-1 text-[10px] ${isActive ? 'text-sky-400' : 'text-slate-500'}`
              }
            >
              <Icon className="h-5 w-5" />
              <span className="max-w-[52px] truncate">{label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  )
}
