import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BarChart3, ChevronRight, Film, Sparkles, Volume2 } from 'lucide-react'
import { api } from '../lib/api'
import { useI18n } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'

type HistoryRow = { id: number; kind: string }

export default function DashboardHome() {
  const { t } = useI18n()
  const [rows, setRows] = useState<HistoryRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get<HistoryRow[]>('/history?limit=200')
      .then((r) => setRows(r.data))
      .catch(() => setRows([]))
      .finally(() => setLoading(false))
  }, [])

  const count = (k: string) => rows.filter((r) => r.kind === k).length

  const cards = [
    { label: t('cards_summaries'), value: count('summarize'), icon: Sparkles, to: '/app/summarize', color: 'from-sky-500/30' },
    { label: t('cards_audio'), value: count('tts') + count('stt'), icon: Volume2, to: '/app/tts', color: 'from-violet-500/30' },
    { label: t('cards_videos'), value: count('video'), icon: Film, to: '/app/video', color: 'from-emerald-500/30' },
    { label: t('cards_infographics'), value: count('infographic'), icon: BarChart3, to: '/app/infographic', color: 'from-amber-500/30' },
  ]

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-white md:text-4xl">{t('dashboard')}</h1>
        <p className="mt-2 text-slate-400">{t('analytics')}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(({ label, value, icon: Icon, to, color }) => (
          <Link key={to} to={to}>
            <GlassCard className={`h-full bg-gradient-to-br ${color} to-transparent`}>
              <div className="flex items-start justify-between">
                <Icon className="h-8 w-8 text-sky-300/90" />
                <span className="rounded-lg bg-black/30 px-2 py-1 text-2xl font-semibold text-white">
                  {loading ? '—' : value}
                </span>
              </div>
              <p className="mt-4 text-sm font-medium text-slate-300">{label}</p>
            </GlassCard>
          </Link>
        ))}
      </div>

      <GlassCard>
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg font-semibold text-white">{t('recent')}</h2>
          <Link to="/app/history" className="text-sm text-sky-400 hover:underline">
            {t('nav_history')}
          </Link>
        </div>
        {loading ? (
          <p className="mt-4 text-sm text-slate-500">…</p>
        ) : rows.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">{t('history_empty')}</p>
        ) : (
          <ul className="mt-4 space-y-2">
            {rows.slice(0, 8).map((r) => (
              <li key={r.id} className="flex items-center justify-between rounded-lg bg-white/5 px-3 py-2 text-sm">
                <span className="capitalize text-slate-300">{r.kind}</span>
                <ChevronRight className="h-4 w-4 text-slate-600" aria-hidden />
              </li>
            ))}
          </ul>
        )}
      </GlassCard>
    </div>
  )
}
