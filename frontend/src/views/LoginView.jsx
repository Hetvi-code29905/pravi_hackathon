import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { BuildingIcon, UserIcon, ShieldAlert, ArrowRight } from '../components/Icons';

export const LoginView = () => {
  const { login, register, loginDemoUser, DEMO_USERS } = useAuth();
  const [isFirstTime, setIsFirstTime] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [designation, setDesignation] = useState('');
  const [role, setRole] = useState('engineer');
  const [department, setDepartment] = useState('Roads & Buildings Department');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isFirstTime) {
        await register({
          username: username.trim(),
          email: username.trim(),
          password: password,
          full_name: fullName.trim() || username.split('@')[0],
          role: role.toLowerCase(),
          department: department,
          designation: designation.trim() || 'Officer / Engineer',
        });
      } else {
        await login(username, password);
      }
    } catch (err) {
      setError(err.message || (isFirstTime ? 'Registration failed. User might already exist.' : 'Invalid username or password'));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (demoUser) => {
    setError('');
    setLoading(true);
    try {
      await loginDemoUser(demoUser);
    } catch (err) {
      setError(err.message || 'Quick login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background visual accents */}
      <div style={{
        position: 'absolute',
        top: '15%',
        left: '20%',
        width: 380,
        height: 380,
        background: 'radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%)',
        borderRadius: '50%',
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '15%',
        right: '20%',
        width: 420,
        height: 420,
        background: 'radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        pointerEvents: 'none',
      }} />

      <div className="glass-card" style={{
        width: '100%',
        maxWidth: 480,
        padding: '36px 32px',
        position: 'relative',
        zIndex: 10,
        border: '1px solid rgba(255, 255, 255, 0.12)',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(59, 130, 246, 0.1)',
      }}>
        {/* Header Emblem & Title */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{
            width: 58,
            height: 58,
            borderRadius: 14,
            background: 'linear-gradient(135deg, #1e3a8a, #0284c7)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 24px rgba(2, 132, 199, 0.4)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            marginBottom: 14,
          }}>
            <BuildingIcon size={30} color="#ffffff" />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 4 }}>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
              PRAVI <span style={{ color: '#38bdf8' }}>R&B</span>
            </h1>
            <span style={{
              fontSize: '0.65rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              padding: '2px 6px',
              borderRadius: 4,
              background: 'rgba(56, 189, 248, 0.15)',
              color: '#38bdf8',
              border: '1px solid rgba(56, 189, 248, 0.3)',
            }}>
              Govt. of Gujarat
            </span>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
            Infrastructure Lifecycle & Asset Management Portal
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            borderRadius: 8,
            padding: '10px 14px',
            color: '#f87171',
            fontSize: '0.82rem',
            marginBottom: 18,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}>
            <ShieldAlert size={16} />
            {error}
          </div>
        )}

        {/* Mode Switcher Tabs */}
        <div style={{
          display: 'flex',
          background: 'rgba(15, 23, 42, 0.6)',
          borderRadius: 8,
          padding: 3,
          marginBottom: 20,
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <button
            type="button"
            onClick={() => { setIsFirstTime(false); setError(''); }}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 6,
              border: 'none',
              background: !isFirstTime ? 'rgba(59, 130, 246, 0.25)' : 'transparent',
              color: !isFirstTime ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Officer Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsFirstTime(true); setError(''); }}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 6,
              border: 'none',
              background: isFirstTime ? 'rgba(59, 130, 246, 0.25)' : 'transparent',
              color: isFirstTime ? '#38bdf8' : '#94a3b8',
              fontWeight: 600,
              fontSize: '0.8rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            First-Time User (Set Password)
          </button>
        </div>

        {/* Login / Registration Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {isFirstTime && (
            <>
              <div>
                <label style={{ fontSize: '0.78rem', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
                  Full Name
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Er. Hardik Patel"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
                  Designation / Title
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Executive Engineer / Project Director"
                  value={designation}
                  onChange={(e) => setDesignation(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
                  Stakeholder Role & Authority Level
                </label>
                <select
                  className="input-field"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="secretary">SECRETARY (Cabinet & Sanction Authority)</option>
                  <option value="admin">ADMIN (Platform Governance & IT Chief)</option>
                  <option value="engineer">ENGINEER (Technical & Milestone Authority)</option>
                  <option value="inspector">INSPECTOR (Quality & Safety Auditor)</option>
                  <option value="contractor">CONTRACTOR (EPC Delivery & Execution)</option>
                </select>
              </div>
            </>
          )}

          <div>
            <label style={{ fontSize: '0.78rem', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
              Official Email / Username
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. engineer@rnb.gujarat.gov.in"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div>
            <label style={{ fontSize: '0.78rem', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
              {isFirstTime ? "Set New Password (min 6 characters)" : "Password"}
            </label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '11px', marginTop: 6, fontSize: '0.92rem' }}
            disabled={loading}
          >
            {loading ? "Processing..." : (isFirstTime ? "Create Account & Enter Portal →" : "Sign In to Portal →")}
          </button>
        </form>

        {/* Quick Persona Access for Reviewers */}
        <div style={{ marginTop: 28, paddingTop: 20, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 12, textAlign: 'center' }}>
            Instant Demo Persona Access
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {DEMO_USERS.map((u) => (
              <button
                key={u.role}
                type="button"
                onClick={() => handleQuickLogin(u)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '9px 12px',
                  borderRadius: 8,
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  color: '#f8fafc',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  fontSize: '0.8rem',
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.5)'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)'}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, textAlign: 'left' }}>
                  <div style={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    background: u.role === 'ADMIN' ? 'rgba(59, 130, 246, 0.2)' : u.role === 'ENGINEER' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: u.role === 'ADMIN' ? '#60a5fa' : u.role === 'ENGINEER' ? '#34d399' : '#fbbf24',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '0.72rem',
                  }}>
                    {u.role[0]}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, color: '#f8fafc' }}>{u.name}</div>
                    <div style={{ fontSize: '0.68rem', color: '#94a3b8' }}>{u.title} · {u.role}</div>
                  </div>
                </div>
                <ArrowRight size={14} color="#64748b" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
