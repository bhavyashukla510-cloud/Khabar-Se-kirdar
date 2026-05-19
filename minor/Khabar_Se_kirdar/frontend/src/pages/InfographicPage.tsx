import { useMemo, useState } from 'react'
import toast from 'react-hot-toast'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api, staticUrl } from '../lib/api'
import { useI18n, type LangCode } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'
import { ProcessingLangSelect } from '../components/LanguageSelector'

export default function InfographicPage() {
  const { t } = useI18n()
  const [text, setText] = useState('')
  const [lang, setLang] = useState<LangCode>('en')
  const [img, setImg] = useState<string | null>(null)
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null)
  const [busy, setBusy] = useState(false)

  const chartData = useMemo(() => {
    const bar = (metrics?.bar as { labels?: string[]; values?: number[] }) || {}
    const labels = bar.labels || []
    const values = bar.values || []
    return labels.map((name, i) => ({ name, value: values[i] ?? 0 }))
  }, [metrics])

  const lineData = useMemo(() => {
    const line = (metrics?.line as { labels?: string[]; values?: number[] }) || {}
    const labels = line.labels || []
    const values = line.values || []
    return labels.map((name, i) => ({ name, value: values[i] ?? 0 }))
  }, [metrics])

  const run = async () => {
    setBusy(true)
    setImg(null)
    setMetrics(null)
    try {
      const { data } = await api.post<{ image_url: string; metrics: Record<string, unknown> }>('/ai/infographic', {
        text,
        caption_language: lang,
      })
      setImg(data.image_url)
      setMetrics(data.metrics)
      toast.success('Infographic ready')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-white">{t('infographic_title')}</h1>
        <p className="mt-1 text-sm text-slate-400">{t('infographic_hint')}</p>
      </div>
      <GlassCard className="space-y-4">
        <ProcessingLangSelect label={t('caption_lang')} value={lang} onChange={setLang} />
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={10}
          className="w-full rounded-xl border border-white/10 bg-slate-950/60 p-3 text-sm text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
          placeholder="Economic / market news…"
        />
        <button
          type="button"
          disabled={busy || text.length < 20}
          onClick={() => void run()}
          className="rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-3 text-sm font-semibold text-slate-900 disabled:opacity-40"
        >
          {busy ? '…' : t('run')}
        </button>
      </GlassCard>
      {img && (
        <div className="grid gap-6 lg:grid-cols-2">
          <GlassCard>
            <img src={staticUrl(img)} alt="Infographic" className="w-full rounded-xl border border-white/10" />
            <a href={staticUrl(img)} download className="mt-3 inline-block text-sm text-sky-400 hover:underline">
              {t('download')} PNG
            </a>
          </GlassCard>
          <GlassCard className="space-y-6">
            <h2 className="text-sm font-semibold text-slate-300">Interactive preview</h2>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                  <Bar dataKey="value" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                  <Line type="monotone" dataKey="value" stroke="#a855f7" strokeWidth={2} dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  )
}
