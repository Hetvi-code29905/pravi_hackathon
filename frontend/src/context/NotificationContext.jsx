import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { CheckCircle, AlertTriangle, ShieldAlert, Info, Sparkles, X, ActivityIcon } from '../components/Icons';

const NotificationContext = createContext(null);

export const NotificationProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const [history, setHistory] = useState([
    {
      id: 'init-1',
      title: 'Gujarat R&B GIS Sync Completed',
      message: '3,842km State Highway asset network coordinates reconciled with N-DEx Gujarat spatial database.',
      type: 'info',
      timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
      read: false,
    },
    {
      id: 'init-2',
      title: 'Quality Audit Triggered: Vadodara Circle',
      message: 'Automated 180-day structural audit scheduled for 14 Major Bridges along NH-48 feeder corridors.',
      type: 'warning',
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
      read: false,
    },
    {
      id: 'init-3',
      title: 'EPC Milestone Verified',
      message: 'Surat Ring Road Phase 2 - Subgrade structural inspection passed with PCI 94/100.',
      type: 'success',
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      read: true,
    }
  ]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addNotification = useCallback(({ title, message, type = 'info', duration = 6000, actionLabel, onAction }) => {
    const id = 'notif-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
    const newNotif = {
      id,
      title,
      message,
      type, // 'success' | 'error' | 'warning' | 'info' | 'lifecycle'
      timestamp: new Date().toISOString(),
      read: false,
      duration,
      actionLabel,
      onAction,
    };

    // Add to toasts for floating display
    setToasts((prev) => [newNotif, ...prev.slice(0, 4)]);

    // Add to history drawer
    setHistory((prev) => [newNotif, ...prev.slice(0, 19)]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }

    return id;
  }, [removeToast]);

  const markAllRead = useCallback(() => {
    setHistory((prev) => prev.map((item) => ({ ...item, read: true })));
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  const unreadCount = history.filter((h) => !h.read).length;

  const notify = {
    success: (title, message, options) => addNotification({ title, message, type: 'success', ...options }),
    error: (title, message, options) => addNotification({ title, message, type: 'error', ...options }),
    warning: (title, message, options) => addNotification({ title, message, type: 'warning', ...options }),
    info: (title, message, options) => addNotification({ title, message, type: 'info', ...options }),
    lifecycle: (title, message, options) => addNotification({ title, message, type: 'lifecycle', duration: 8000, ...options }),
  };

  return (
    <NotificationContext.Provider
      value={{
        toasts,
        history,
        unreadCount,
        addNotification,
        removeToast,
        markAllRead,
        clearHistory,
        notify,
      }}
    >
      {children}
      {/* Global Toast Overlay */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

const ToastContainer = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 80,
        right: 24,
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        maxWidth: 420,
        width: 'calc(100vw - 48px)',
        pointerEvents: 'none',
      }}
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={() => onDismiss(toast.id)} />
      ))}
    </div>
  );
};

const ToastItem = ({ toast, onDismiss }) => {
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    if (!toast.duration || toast.duration <= 0) return;
    const interval = 50;
    const step = (interval / toast.duration) * 100;
    const timer = setInterval(() => {
      setProgress((prev) => Math.max(0, prev - step));
    }, interval);
    return () => clearInterval(timer);
  }, [toast.duration]);

  const typeConfig = {
    success: {
      border: 'rgba(16, 185, 129, 0.4)',
      bg: 'linear-gradient(135deg, rgba(6, 44, 30, 0.95), rgba(10, 24, 20, 0.95))',
      glow: '0 8px 30px rgba(16, 185, 129, 0.25)',
      icon: <CheckCircle size={20} color="#34d399" />,
      accentColor: '#10b981',
      titleColor: '#34d399',
    },
    error: {
      border: 'rgba(239, 68, 68, 0.4)',
      bg: 'linear-gradient(135deg, rgba(50, 15, 20, 0.95), rgba(28, 10, 14, 0.95))',
      glow: '0 8px 30px rgba(239, 68, 68, 0.25)',
      icon: <ShieldAlert size={20} color="#f87171" />,
      accentColor: '#ef4444',
      titleColor: '#f87171',
    },
    warning: {
      border: 'rgba(245, 158, 11, 0.4)',
      bg: 'linear-gradient(135deg, rgba(48, 30, 8, 0.95), rgba(26, 18, 8, 0.95))',
      glow: '0 8px 30px rgba(245, 158, 11, 0.22)',
      icon: <AlertTriangle size={20} color="#fbbf24" />,
      accentColor: '#f59e0b',
      titleColor: '#fbbf24',
    },
    lifecycle: {
      border: 'rgba(14, 165, 233, 0.5)',
      bg: 'linear-gradient(135deg, rgba(12, 38, 70, 0.96), rgba(8, 20, 42, 0.96))',
      glow: '0 10px 35px rgba(14, 165, 233, 0.35)',
      icon: <Sparkles size={20} color="#38bdf8" />,
      accentColor: '#0ea5e9',
      titleColor: '#38bdf8',
    },
    info: {
      border: 'rgba(99, 102, 241, 0.4)',
      bg: 'linear-gradient(135deg, rgba(20, 26, 60, 0.95), rgba(12, 16, 38, 0.95))',
      glow: '0 8px 30px rgba(99, 102, 241, 0.25)',
      icon: <Info size={20} color="#818cf8" />,
      accentColor: '#6366f1',
      titleColor: '#818cf8',
    },
  };

  const cfg = typeConfig[toast.type] || typeConfig.info;

  return (
    <div
      style={{
        pointerEvents: 'auto',
        background: cfg.bg,
        border: `1px solid ${cfg.border}`,
        borderRadius: 14,
        padding: '14px 16px',
        boxShadow: `${cfg.glow}, 0 12px 36px rgba(0, 0, 0, 0.5)`,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        position: 'relative',
        overflow: 'hidden',
        animation: 'toastSlideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        <div style={{ marginTop: 2, flexShrink: 0 }}>{cfg.icon}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
            <span style={{ fontWeight: 700, fontSize: '0.88rem', color: cfg.titleColor, letterSpacing: '-0.01em' }}>
              {toast.title}
            </span>
            <button
              onClick={onDismiss}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                padding: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: 4,
                transition: 'color 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = '#ffffff')}
              onMouseLeave={(e) => (e.currentTarget.style.color = '#94a3b8')}
            >
              <X size={15} />
            </button>
          </div>
          {toast.message && (
            <p style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.45, marginTop: 3 }}>
              {toast.message}
            </p>
          )}
          {toast.actionLabel && toast.onAction && (
            <button
              onClick={() => {
                toast.onAction();
                onDismiss();
              }}
              style={{
                marginTop: 8,
                padding: '4px 10px',
                borderRadius: 6,
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: '#ffffff',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {toast.actionLabel} →
            </button>
          )}
        </div>
      </div>

      {/* Decay Progress Bar */}
      {toast.duration > 0 && (
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            height: 3,
            width: `${progress}%`,
            background: cfg.accentColor,
            transition: 'width 50ms linear',
          }}
        />
      )}
    </div>
  );
};
