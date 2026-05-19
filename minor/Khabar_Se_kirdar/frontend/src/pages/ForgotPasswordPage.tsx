import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { api } from '../lib/api'
import { useI18n } from '../lib/i18n'
import { GlassCard } from '../components/GlassCard'

const schema = z.object({ email: z.string().email() })

export default function ForgotPasswordPage() {
  const { t } = useI18n()
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { email: '' },
  })

  const onSubmit = handleSubmit(async (v) => {
    try {
      await api.post('/auth/forgot-password', v)
      toast.success('If an account exists, instructions would be sent.')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Request failed')
    }
  })

  return (
    <div className="flex min-h-svh items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <GlassCard>
          <h1 className="font-display text-2xl font-semibold text-white">{t('forgot_title')}</h1>
          <p className="mt-2 text-sm text-slate-400">{t('forgot_hint')}</p>
          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div>
              <label className="text-xs uppercase text-slate-500">{t('email')}</label>
              <input
                type="email"
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2.5 text-slate-100 outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('email')}
              />
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-xl bg-white/10 py-3 text-sm font-semibold text-white hover:bg-white/15 disabled:opacity-50"
            >
              {t('send')}
            </button>
          </form>
          <p className="mt-4 text-center text-sm">
            <Link to="/login" className="text-sky-400 hover:underline">
              {t('back_login')}
            </Link>
          </p>
        </GlassCard>
      </motion.div>
    </div>
  )
}
