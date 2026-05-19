import { useState } from 'react'
import toast from 'react-hot-toast'
import { api } from '../lib/api'
import { useI18n, type LangCode } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'
import { ProcessingLangSelect } from '../components/LanguageSelector'

export default function STTPage() {
  const { t } = useI18n()
  const [file, setFile] = useState<File | null>(null)
  const [lang, setLang] = useState<LangCode>('en')
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)

  const run = async () => {
    if (!file) return
    setBusy(true)
    setText('')
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('language', lang)
      const { data } = await api.post<{ text: string }>('/ai/stt', fd)
      setText(data.text)
      toast.success('Transcribed')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-white">{t('stt_title')}</h1>
        <p className="mt-1 text-sm text-slate-400">{t('stt_hint')}</p>
      </div>
      <GlassCard className="space-y-4">
        <ProcessingLangSelect label={t('language')} value={lang} onChange={setLang} />
        <div>
          <label className="text-xs uppercase text-slate-500">{t('upload')}</label>
          <input
            type="file"
            accept="audio/*,video/*"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="mt-2 block w-full text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-sky-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
          />
        </div>
        <button
          type="button"
          disabled={busy || !file}
          onClick={() => void run()}
          className="rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
        >
          {busy ? '…' : t('transcribe')}
        </button>
        {text && (
          <div>
            <h2 className="text-xs uppercase text-slate-500">{t('transcript')}</h2>
            <pre className="mt-2 whitespace-pre-wrap rounded-xl bg-black/30 p-4 text-sm text-slate-100">{text}</pre>
            <a
              href={`data:text/plain;charset=utf-8,${encodeURIComponent(text)}`}
              download="transcript.txt"
              className="mt-3 inline-block text-sm text-sky-400 hover:underline"
            >
              {t('download')} .txt
            </a>
          </div>
        )}
      </GlassCard>
    </div>
  )
}
