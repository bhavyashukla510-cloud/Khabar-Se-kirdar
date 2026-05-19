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
  full_name: z.string().max(255).optional(),
})

type Form = z.infer<typeof schema>

export default function RegisterPage() {
  const { register: reg } = useAuth()
  const { t } = useI18n()
  const nav = useNavigate()
  const {
    register: field,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '', full_name: '' },
  })

  const onSubmit = handleSubmit(async (values) => {
    try {
      await reg(values.email, values.password, values.full_name || '')
      toast.success('Account created')
      nav('/app', { replace: true })
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Registration failed')
    }
  })

  return (
    <div className="flex min-h-svh items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <GlassCard>
          <h1 className="font-display text-2xl font-semibold text-white">{t('register_title')}</h1>
          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div>
              <label className="text-xs uppercase text-slate-500">{t('full_name')}</label>
              <input
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2.5 text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
                {...field('full_name')}
              />
            </div>
            <div>
              <label className="text-xs uppercase text-slate-500">{t('email')}</label>
              <input
                type="email"
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2.5 text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
                {...field('email')}
              />
            </div>
            <div>
              <label className="text-xs uppercase text-slate-500">{t('password')}</label>
              <input
                type="password"
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2.5 text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
                {...field('password')}
              />
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-sky-500 py-3 text-sm font-semibold text-white shadow-lg disabled:opacity-50"
            >
              {isSubmitting && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />}
              {t('submit_register')}
            </button>
          </form>
          <p className="mt-4 text-center text-sm text-slate-500">
            <Link to="/login" className="text-sky-400 hover:underline">
              {t('have_account')}
            </Link>
          </p>
        </GlassCard>
      </motion.div>
    </div>
  )
}
