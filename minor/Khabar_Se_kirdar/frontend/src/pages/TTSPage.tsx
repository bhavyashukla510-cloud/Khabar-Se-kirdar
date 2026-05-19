import { useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { api, staticUrl } from '../lib/api'
import { useI18n, type LangCode } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'
import { ProcessingLangSelect } from '../components/LanguageSelector'

export default function TTSPage() {
  const { t } = useI18n()
  const [text, setText] = useState('')
  const [lang, setLang] = useState<LangCode>('en')
  const [url, setUrl] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  const run = async () => {
    setBusy(true)
    setUrl(null)
    try {
      const { data } = await api.post<{ audio_url: string }>('/ai/tts', { text, language: lang })
      setUrl(data.audio_url)
      toast.success('Audio ready')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-white">{t('tts_title')}</h1>
        <p className="mt-1 text-sm text-slate-400">{t('tts_hint')}</p>
      </div>
      <GlassCard className="space-y-4">
        <div>
          <label className="text-xs uppercase text-slate-500">{t('tts_text')}</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={8}
            className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/60 p-3 text-sm text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
          />
        </div>
        <ProcessingLangSelect label={t('language')} value={lang} onChange={setLang} />
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            disabled={busy || !text.trim()}
            onClick={() => void run()}
            className="rounded-xl bg-sky-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-40"
          >
            {busy ? '…' : t('run')}
          </button>
          {url && (
            <>
              <audio ref={audioRef} controls className="h-10 flex-1 min-w-[200px]" src={staticUrl(url)} />
              <a
                href={staticUrl(url)}
                download
                className="rounded-xl border border-white/15 px-4 py-2 text-sm text-slate-200 hover:bg-white/5"
              >
                {t('download')}
              </a>
            </>
          )}
        </div>
      </GlassCard>
    </div>
  )
}
