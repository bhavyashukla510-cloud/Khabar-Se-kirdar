import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

export function GlassCard({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-panel p-6 ${className}`}
    >
      {children}
    </motion.div>
  )
}
