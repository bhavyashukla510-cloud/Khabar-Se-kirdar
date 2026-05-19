import { useAuth } from '../lib/auth'
import { useI18n } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'
import { LanguageSelector } from '../components/LanguageSelector'

export default function SettingsPage() {
  const { user } = useAuth()
  const { t } = useI18n()

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="font-display text-2xl font-semibold text-white">{t('settings_title')}</h1>
      <GlassCard className="space-y-4">
        <div>
          <p className="text-xs uppercase text-slate-500">{t('settings_email')}</p>
          <p className="mt-1 text-lg text-white">{user?.email}</p>
          {user?.full_name && <p className="text-sm text-slate-400">{user.full_name}</p>}
        </div>
        <LanguageSelector />
      </GlassCard>
    </div>
  )
}
