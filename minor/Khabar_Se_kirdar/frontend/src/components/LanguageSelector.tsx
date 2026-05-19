import { LANG_OPTIONS, useI18n, type LangCode } from '../lib/i18n'

export function LanguageSelector({ compact }: { compact?: boolean }) {
  const { lang, setLang, t } = useI18n()
  return (
    <label className={`flex flex-col gap-1 ${compact ? '' : 'min-w-[140px]'}`}>
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{t('ui_lang')}</span>
      <select
        value={lang}
        onChange={(e) => setLang(e.target.value as LangCode)}
        className="rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
      >
        {LANG_OPTIONS.map((o) => (
          <option key={o.code} value={o.code}>
            {o.native}
          </option>
        ))}
      </select>
    </label>
  )
}

export function ProcessingLangSelect({
  value,
  onChange,
  label,
}: {
  value: LangCode
  onChange: (v: LangCode) => void
  label: string
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as LangCode)}
        className="rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
      >
        {LANG_OPTIONS.map((o) => (
          <option key={o.code} value={o.code}>
            {o.native}
          </option>
        ))}
      </select>
    </label>
  )
}
