import React, { useEffect } from 'react';
import { AlertCircle, CheckCircle2, Info, X, AlertTriangle } from 'lucide-react';

export interface ToastProps {
  id?: string;
  type: 'error' | 'success' | 'info' | 'warning';
  title: string;
  message: string;
  onClose: () => void;
  durationMs?: number;
}

export const Toast: React.FC<ToastProps> = ({
  type,
  title,
  message,
  onClose,
  durationMs = 6000,
}) => {
  useEffect(() => {
    if (durationMs > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, durationMs);
      return () => clearTimeout(timer);
    }
  }, [durationMs, onClose]);

  const config = {
    error: {
      bg: 'bg-dark-900/95 border-accent-rose/40 shadow-accent-rose/10',
      icon: <AlertCircle className="h-5 w-5 text-accent-rose flex-shrink-0" />,
      titleColor: 'text-accent-rose',
      badge: 'AI Error',
    },
    warning: {
      bg: 'bg-dark-900/95 border-accent-amber/40 shadow-accent-amber/10',
      icon: <AlertTriangle className="h-5 w-5 text-accent-amber flex-shrink-0" />,
      titleColor: 'text-accent-amber',
      badge: 'Warning',
    },
    success: {
      bg: 'bg-dark-900/95 border-accent-emerald/40 shadow-accent-emerald/10',
      icon: <CheckCircle2 className="h-5 w-5 text-accent-emerald flex-shrink-0" />,
      titleColor: 'text-accent-emerald',
      badge: 'Success',
    },
    info: {
      bg: 'bg-dark-900/95 border-orange-500/40 shadow-orange-500/10',
      icon: <Info className="h-5 w-5 text-orange-400 flex-shrink-0" />,
      titleColor: 'text-orange-400',
      badge: 'Info',
    },
  }[type];

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 max-w-md w-full border rounded-xl p-4 shadow-2xl backdrop-blur-md transition-all duration-300 transform translate-y-0 opacity-100 ${config.bg}`}
      role="alert"
    >
      <div className="flex items-start space-x-3">
        {config.icon}
        <div className="flex-1 pr-2">
          <div className="flex items-center space-x-2">
            <h4 className={`text-xs font-bold uppercase tracking-wider ${config.titleColor}`}>
              {title}
            </h4>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-dark-950 border border-dark-750 text-slate-400">
              {config.badge}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-300 leading-relaxed break-words">
            {message}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-dark-800 transition-colors"
          aria-label="Close notification"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
