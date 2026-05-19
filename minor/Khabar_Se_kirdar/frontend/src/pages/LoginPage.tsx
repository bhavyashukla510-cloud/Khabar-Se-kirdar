import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { useAuth } from '../lib/auth'
import { useI18n } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  remember: z.boolean(),
})

type Form = z.infer<typeof schema>

export default function LoginPage() {
  const { login } = useAuth()
  const { t } = useI18n()
  const nav = useNavigate()
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '', remember: true },
  })

  const onSubmit = handleSubmit(async (values) => {
    try {
      await login(values.email, values.password, values.remember)
      toast.success('Signed in')
      nav('/app', { replace: true })
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Login failed')
    }
  })

  return (
    <div className="flex min-h-svh items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <GlassCard>
          <h1 className="font-display text-2xl font-semibold text-white">{t('login_title')}</h1>
          <p className="mt-1 text-sm text-slate-500">{t('tagline')}</p>
          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div>
              <label className="text-xs uppercase text-slate-500">{t('email')}</label>
              <input
                type="email"
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2.5 text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('email')}
              />
            </div>
            <div>
              <label className="text-xs uppercase text-slate-500">{t('password')}</label>
              <input
                type="password"
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2.5 text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('password')}
              />
            </div>
            <label className="flex items-center gap-2 text-sm text-slate-400">
              <input type="checkbox" {...register('remember')} className="rounded border-white/20 bg-slate-900" />
              {t('remember')}
            </label>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-violet-500 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 transition hover:opacity-95 disabled:opacity-50"
            >
              {isSubmitting && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />}
              {t('submit_login')}
            </button>
          </form>
          <div className="mt-4 flex flex-wrap justify-between gap-2 text-sm">
            <Link to="/forgot-password" className="text-sky-400 hover:underline">
              {t('forgot')}
            </Link>
            <Link to="/register" className="text-slate-400 hover:text-slate-200">
              {t('no_account')}
            </Link>
          </div>
        </GlassCard>
      </motion.div>
    </div>
  )
}
