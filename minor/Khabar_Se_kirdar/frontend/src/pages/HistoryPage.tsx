import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useI18n } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'

type Row = {
  id: number
  kind: string
  title: string
  language: string
  input_preview: string
  output_preview: string
  created_at: string
}

export default function HistoryPage() {
  const { t } = useI18n()
  const [rows, setRows] = useState<Row[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get<Row[]>('/history')
      .then((r) => setRows(r.data))
      .catch(() => setRows([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <h1 className="font-display text-2xl font-semibold text-white">{t('history_title')}</h1>
      <GlassCard>
        {loading ? (
          <p className="text-sm text-slate-500">…</p>
        ) : rows.length === 0 ? (
          <p className="text-sm text-slate-500">{t('history_empty')}</p>
        ) : (
          <ul className="divide-y divide-white/10">
            {rows.map((r) => (
              <li key={r.id} className="py-4 first:pt-0">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs font-medium uppercase text-sky-300">
                    {r.kind}
                  </span>
                  <span className="text-xs text-slate-500">{r.created_at}</span>
                </div>
                <p className="mt-2 line-clamp-2 text-sm text-slate-400">{r.input_preview}</p>
                <p className="mt-1 line-clamp-2 text-sm text-slate-200">{r.output_preview}</p>
              </li>
            ))}
          </ul>
        )}
      </GlassCard>
    </div>
  )
}
