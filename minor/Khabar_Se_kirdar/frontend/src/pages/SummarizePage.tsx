import { useState } from 'react'
import toast from 'react-hot-toast'
import { api } from '../lib/api'
import { useI18n, type LangCode } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'
import { ProcessingLangSelect } from '../components/LanguageSelector'

export default function SummarizePage() {
  const { t } = useI18n()
  const [text, setText] = useState('')
  const [lang, setLang] = useState<LangCode>('en')
  const [out, setOut] = useState('')
  const [busy, setBusy] = useState(false)

  const run = async () => {
    setBusy(true)
    setOut('')
    try {
      const { data } = await api.post<{ summary: string }>('/ai/summarize', {
        text,
        output_language: lang,
      })
      setOut(data.summary)
      toast.success('Done')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-white">{t('summarize_title')}</h1>
        <p className="mt-1 text-sm text-slate-400">{t('summarize_hint')}</p>
      </div>
      <GlassCard>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="md:col-span-2">
            <label className="text-xs uppercase text-slate-500">{t('article')}</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              className="mt-1 w-full resize-y rounded-xl border border-white/10 bg-slate-950/60 p-3 text-sm text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
              placeholder="Paste news…"
            />
          </div>
          <div className="flex flex-col gap-4">
            <ProcessingLangSelect label={t('output_lang')} value={lang} onChange={setLang} />
            <button
              type="button"
              disabled={busy || text.length < 20}
              onClick={() => void run()}
              className="mt-auto rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 py-3 text-sm font-semibold text-white disabled:opacity-40"
            >
              {busy ? '…' : t('run')}
            </button>
          </div>
        </div>
      </GlassCard>
      {out && (
        <GlassCard>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">{t('result')}</h2>
          <p className="mt-3 whitespace-pre-wrap text-slate-100">{out}</p>
        </GlassCard>
      )}
    </div>
  )
}
