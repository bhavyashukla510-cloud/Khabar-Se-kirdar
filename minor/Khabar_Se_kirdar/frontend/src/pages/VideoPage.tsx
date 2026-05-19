import { useState } from 'react'
import toast from 'react-hot-toast'
import { api, staticUrl } from '../lib/api'
import { useI18n, type LangCode } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'
import { ProcessingLangSelect } from '../components/LanguageSelector'

export default function VideoPage() {
  const { t } = useI18n()
  const [text, setText] = useState('')
  const [nar, setNar] = useState<LangCode>('en')
  const [sub, setSub] = useState<LangCode>('en')
  const [busy, setBusy] = useState(false)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [summary, setSummary] = useState('')

  const run = async () => {
    setBusy(true)
    setVideoUrl(null)
    try {
      const { data } = await api.post<{ video_url: string; summary: string }>('/ai/video', {
        text,
        narration_language: nar,
        subtitle_language: sub,
      })
      setVideoUrl(data.video_url)
      setSummary(data.summary)
      toast.success('Video ready')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-white">{t('video_title')}</h1>
        <p className="mt-1 text-sm text-slate-400">{t('video_hint')}</p>
        <p className="mt-2 text-xs text-amber-200/80">Rendering uses FFmpeg via MoviePy and may take a few minutes.</p>
      </div>
      <GlassCard className="space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          className="w-full rounded-xl border border-white/10 bg-slate-950/60 p-3 text-sm text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
          placeholder="News article…"
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <ProcessingLangSelect label={t('narration_lang')} value={nar} onChange={setNar} />
          <ProcessingLangSelect label={t('subtitle_lang')} value={sub} onChange={setSub} />
        </div>
        <button
          type="button"
          disabled={busy || text.length < 20}
          onClick={() => void run()}
          className="rounded-xl bg-gradient-to-r from-emerald-500 to-sky-500 px-6 py-3 text-sm font-semibold text-white disabled:opacity-40"
        >
          {busy ? 'Rendering…' : t('render_video')}
        </button>
      </GlassCard>
      {videoUrl && (
        <GlassCard>
          <video controls className="w-full max-h-[480px] rounded-xl border border-white/10" src={staticUrl(videoUrl)} />
          {summary && (
            <p className="mt-4 text-sm text-slate-300">
              <span className="font-semibold text-slate-400">Narration script: </span>
              {summary}
            </p>
          )}
          <a href={staticUrl(videoUrl)} download className="mt-3 inline-block text-sm text-sky-400 hover:underline">
            {t('download')} MP4
          </a>
        </GlassCard>
      )}
    </div>
  )
}
