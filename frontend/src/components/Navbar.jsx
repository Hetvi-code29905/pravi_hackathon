import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import { RefreshCw, UserIcon, LogOut, Layers, ActivityIcon, Wrench, BuildingIcon, Bell, Sparkles, Check, CheckCircle, Info, AlertTriangle, ShieldCheck, ChevronDown } from './Icons';

export const Navbar = ({ activeTab, onTabChange, onReseedComplete }) => {
  const { user, logout } = useAuth();
  const { history, unreadCount, markAllRead, clearHistory, notify } = useNotification();
  const [reseeding, setReseeding] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notifMenuOpen, setNotifMenuOpen] = useState(false);

  const userMenuRef = useRef(null);
  const notifMenuRef = useRef(null);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setUserMenuOpen(false);
      }
      if (notifMenuRef.current && !notifMenuRef.current.contains(e.target)) {
        setNotifMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleReseed = async () => {
    if (confirm("Reset and re-seed database with realistic Gujarat R&B demo dataset?")) {
      try {
        setReseeding(true);
        const { api } = await import('../services/api');
        await api.reseedDatabase();
        if (onReseedComplete) onReseedComplete();
        notify.success("Database Reset Complete", "Gujarat R&B infrastructure projects, live assets, and lifecycle milestones successfully re-seeded into MongoDB.");
      } catch (err) {
        notify.error("Database Reset Failed", err.message);
      } finally {
        setReseeding(false);
      }
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Command Center & GIS', icon: ActivityIcon },
    { id: 'assets', label: 'Asset Passports', icon: BuildingIcon },
    { id: 'projects', label: 'Capital Pipeline', icon: Layers },
    { id: 'operations', label: 'Audits & Work Orders', icon: Wrench },
  ];

  const getRoleBadgeStyle = (role) => {
    switch (role?.toUpperCase()) {
      case 'SECRETARY':
        return { bg: 'linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(126, 34, 206, 0.15))', border: 'rgba(168, 85, 247, 0.4)', text: '#c084fc', iconColor: '#a855f7' };
      case 'ADMIN':
        return { bg: 'linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(2, 132, 199, 0.15))', border: 'rgba(14, 165, 233, 0.4)', text: '#38bdf8', iconColor: '#0ea5e9' };
      case 'ENGINEER':
        return { bg: 'linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(5, 150, 105, 0.15))', border: 'rgba(16, 185, 129, 0.4)', text: '#34d399', iconColor: '#10b981' };
      case 'INSPECTOR':
        return { bg: 'linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(217, 119, 6, 0.15))', border: 'rgba(245, 158, 11, 0.4)', text: '#fbbf24', iconColor: '#f59e0b' };
      default:
        return { bg: 'linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(79, 70, 229, 0.15))', border: 'rgba(99, 102, 241, 0.4)', text: '#818cf8', iconColor: '#6366f1' };
    }
  };

  const roleStyle = getRoleBadgeStyle(user?.role);

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'rgba(7, 11, 20, 0.82)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      padding: '0 24px',
      boxShadow: '0 4px 30px rgba(0, 0, 0, 0.5)',
    }}>
      <div style={{ maxWidth: 1440, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 70 }}>
        {/* Brand / Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #4f46e5 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 18px rgba(2, 132, 199, 0.45)',
            border: '1px solid rgba(255, 255, 255, 0.25)',
            position: 'relative',
          }}>
            <BuildingIcon size={24} color="#ffffff" />
            <div style={{
              position: 'absolute',
              top: -2,
              right: -2,
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: '#10b981',
              boxShadow: '0 0 10px #10b981',
              border: '2px solid #070b14',
            }} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.15rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
                PRAVI <span style={{ color: '#38bdf8' }}>R&B</span>
              </span>
              <span style={{
                fontSize: '0.65rem',
                fontWeight: 800,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
                padding: '2px 8px',
                borderRadius: 9999,
                background: 'rgba(14, 165, 233, 0.15)',
                color: '#38bdf8',
                border: '1px solid rgba(14, 165, 233, 0.35)',
              }}>
                Govt. of Gujarat
              </span>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 500, letterSpacing: '0.01em' }}>
              Infrastructure Lifecycle & GIS Asset Intelligence
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(15, 23, 42, 0.5)', padding: '4px 6px', borderRadius: 14, border: '1px solid rgba(255, 255, 255, 0.06)' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 16px',
                  borderRadius: 10,
                  border: '1px solid',
                  borderColor: isActive ? 'rgba(56, 189, 248, 0.4)' : 'transparent',
                  background: isActive ? 'linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(37, 99, 235, 0.15) 100%)' : 'transparent',
                  color: isActive ? '#38bdf8' : '#94a3b8',
                  fontSize: '0.86rem',
                  fontWeight: isActive ? 700 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                  boxShadow: isActive ? '0 4px 14px rgba(14, 165, 233, 0.2)' : 'none',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = '#f8fafc';
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = '#94a3b8';
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <Icon size={16} color={isActive ? '#38bdf8' : '#64748b'} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Right Action Suite: Reseed, Notification Center & User Profile */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Quick Re-seed Button */}
          <button
            onClick={handleReseed}
            disabled={reseeding}
            className="btn btn-secondary btn-sm"
            title="Re-populate MongoDB with Gujarat Demo Data"
            style={{ fontSize: '0.8rem', padding: '7px 13px', borderRadius: 10 }}
          >
            <RefreshCw size={13} className={reseeding ? "spin-icon" : ""} />
            {reseeding ? "Seeding DB..." : "Reset Demo Data"}
          </button>

          {/* Notification Bell Dropdown */}
          <div style={{ position: 'relative' }} ref={notifMenuRef}>
            <button
              onClick={() => {
                setNotifMenuOpen(!notifMenuOpen);
                if (!notifMenuOpen && unreadCount > 0) markAllRead();
              }}
              style={{
                width: 38,
                height: 38,
                borderRadius: 10,
                background: notifMenuOpen ? 'rgba(14, 165, 233, 0.2)' : 'rgba(30, 41, 59, 0.6)',
                border: '1px solid',
                borderColor: notifMenuOpen ? 'rgba(14, 165, 233, 0.5)' : 'rgba(255, 255, 255, 0.1)',
                color: notifMenuOpen ? '#38bdf8' : '#cbd5e1',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                transition: 'all 0.2s ease',
              }}
              title="State Infrastructure Activity & Alerts"
            >
              <Bell size={18} />
              {unreadCount > 0 && (
                <span
                  style={{
                    position: 'absolute',
                    top: -4,
                    right: -4,
                    minWidth: 18,
                    height: 18,
                    borderRadius: 9999,
                    background: '#ef4444',
                    color: '#ffffff',
                    fontSize: '0.65rem',
                    fontWeight: 800,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '0 4px',
                    border: '2px solid #070b14',
                    boxShadow: '0 0 10px rgba(239, 68, 68, 0.6)',
                  }}
                >
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notification Drawer Panel */}
            {notifMenuOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '120%',
                  right: 0,
                  width: 380,
                  background: '#0d1527',
                  border: '1px solid rgba(255, 255, 255, 0.14)',
                  borderRadius: 16,
                  boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(14, 165, 233, 0.15)',
                  padding: 16,
                  zIndex: 300,
                  animation: 'modalEnter 0.2s ease-out',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, paddingBottom: 10, borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 800, color: '#f8fafc', fontSize: '0.92rem' }}>State Activity Center</span>
                    <span style={{ fontSize: '0.7rem', background: 'rgba(14, 165, 233, 0.2)', color: '#38bdf8', padding: '2px 6px', borderRadius: 4, fontWeight: 700 }}>
                      Live R&B Stream
                    </span>
                  </div>
                  {history.length > 0 && (
                    <button
                      onClick={clearHistory}
                      style={{ background: 'none', border: 'none', color: '#64748b', fontSize: '0.72rem', cursor: 'pointer', fontWeight: 600 }}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#94a3b8'}
                      onMouseLeave={(e) => e.currentTarget.style.color = '#64748b'}
                    >
                      Clear
                    </button>
                  )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 340, overflowY: 'auto' }}>
                  {history.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '24px 0', color: '#64748b', fontSize: '0.82rem' }}>
                      No recent activity logs.
                    </div>
                  ) : (
                    history.map((item) => (
                      <div
                        key={item.id}
                        style={{
                          padding: '10px 12px',
                          borderRadius: 10,
                          background: item.read ? 'rgba(255, 255, 255, 0.02)' : 'rgba(14, 165, 233, 0.08)',
                          border: `1px solid ${item.read ? 'rgba(255, 255, 255, 0.05)' : 'rgba(14, 165, 233, 0.25)'}`,
                          display: 'flex',
                          flexDirection: 'column',
                          gap: 4,
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6 }}>
                          <span style={{ fontWeight: 700, fontSize: '0.82rem', color: item.type === 'success' ? '#34d399' : item.type === 'warning' ? '#fbbf24' : '#38bdf8' }}>
                            {item.title}
                          </span>
                          <span style={{ fontSize: '0.66rem', color: '#64748b' }}>
                            {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <p style={{ fontSize: '0.76rem', color: '#cbd5e1', lineHeight: 1.4 }}>
                          {item.message}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* User Profile Dropdown */}
          <div style={{ position: 'relative' }} ref={userMenuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '6px 14px 6px 8px',
                borderRadius: 12,
                background: 'rgba(30, 41, 59, 0.55)',
                border: `1px solid ${roleStyle.border}`,
                color: '#f8fafc',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(30, 41, 59, 0.85)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(30, 41, 59, 0.55)'}
            >
              <div style={{
                width: 32,
                height: 32,
                borderRadius: 9,
                background: roleStyle.bg,
                border: `1px solid ${roleStyle.border}`,
                color: roleStyle.text,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: '0.82rem',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
              }}>
                {user?.full_name ? user.full_name[0] : 'U'}
              </div>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontWeight: 700, fontSize: '0.82rem', lineHeight: 1.2, maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {user?.full_name || 'Officer'}
                </div>
                <div style={{ fontSize: '0.68rem', color: roleStyle.text, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {user?.role || 'VIEWER'}
                </div>
              </div>
              <ChevronDown size={14} color="#64748b" />
            </button>

            {/* Profile Dropdown Panel */}
            {userMenuOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '120%',
                  right: 0,
                  width: 290,
                  background: '#0d1527',
                  border: '1px solid rgba(255, 255, 255, 0.14)',
                  borderRadius: 16,
                  boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(14, 165, 233, 0.15)',
                  padding: 16,
                  zIndex: 300,
                  animation: 'modalEnter 0.2s ease-out',
                }}
              >
                <div style={{ marginBottom: 12, paddingBottom: 12, borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <div style={{
                      width: 40,
                      height: 40,
                      borderRadius: 10,
                      background: roleStyle.bg,
                      border: `1px solid ${roleStyle.border}`,
                      color: roleStyle.text,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 800,
                      fontSize: '1rem',
                    }}>
                      {user?.full_name ? user.full_name[0] : 'U'}
                    </div>
                    <div>
                      <div style={{ fontWeight: 800, color: '#f8fafc', fontSize: '0.9rem' }}>{user?.full_name}</div>
                      <div style={{ fontSize: '0.72rem', color: roleStyle.text, fontWeight: 700 }}>{user?.designation || user?.role}</div>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#94a3b8', marginTop: 4 }}>
                    <strong>Email:</strong> {user?.email}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: 2 }}>
                    <strong>Dept:</strong> {user?.department || 'Roads & Buildings Department'}
                  </div>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.03)', borderRadius: 10, padding: '8px 12px', marginBottom: 12, border: '1px solid rgba(255, 255, 255, 0.06)' }}>
                  <div style={{ fontSize: '0.68rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700 }}>Authority Level</div>
                  <div style={{ fontSize: '0.75rem', color: '#cbd5e1', marginTop: 2 }}>
                    {user?.role === 'SECRETARY' && "Full Administrative Sanctions, Handover Approvals, Capex Authorization"}
                    {user?.role === 'ADMIN' && "System Governance, Lifecycle Configuration, User Management"}
                    {user?.role === 'ENGINEER' && "Milestone Approvals, Work Order Dispatch, Handover Verification"}
                    {user?.role === 'INSPECTOR' && "Condition Audits, Defect Logging, Compliance Verification"}
                    {user?.role === 'CONTRACTOR' && "Milestone Dossier Submission, Quality Test Uploads"}
                  </div>
                </div>

                <button
                  onClick={() => {
                    logout();
                    setUserMenuOpen(false);
                  }}
                  className="btn btn-danger"
                  style={{
                    width: '100%',
                    justifyContent: 'center',
                    padding: '9px 12px',
                    fontSize: '0.82rem',
                    borderRadius: 10,
                  }}
                >
                  <LogOut size={15} />
                  Sign Out of Session
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
