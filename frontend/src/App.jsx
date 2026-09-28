import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { Navbar } from './components/Navbar';
import { LoginView } from './views/LoginView';
import { DashboardView } from './views/DashboardView';
import { AssetPassportView } from './views/AssetPassportView';
import { ProjectsView } from './views/ProjectsView';
import { OperationsView } from './views/OperationsView';

function MainContent() {
  const { user, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedAssetId, setSelectedAssetId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#94a3b8', gap: 16 }}>
        <div style={{
          width: 48,
          height: 48,
          borderRadius: '50%',
          border: '3px solid rgba(14, 165, 233, 0.15)',
          borderTopColor: '#0ea5e9',
          animation: 'spin 0.8s linear infinite',
          boxShadow: '0 0 20px rgba(14, 165, 233, 0.3)',
        }} />
        <div style={{ fontSize: '0.9rem', fontWeight: 600, letterSpacing: '0.02em', color: '#cbd5e1' }}>
          Initializing Gujarat R&B Digital Infrastructure Platform...
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginView />;
  }

  const handleSelectAsset = (assetId) => {
    setSelectedAssetId(assetId);
    setActiveTab('assets');
  };

  const handleReseedComplete = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
      <Navbar
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab);
          if (tab !== 'assets') setSelectedAssetId(null);
        }}
        onReseedComplete={handleReseedComplete}
      />

      <main style={{ flex: 1, position: 'relative' }}>
        {activeTab === 'dashboard' && (
          <DashboardView
            key={`dash-${refreshKey}`}
            onSelectAsset={handleSelectAsset}
            onNavigateTab={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === 'assets' && (
          <AssetPassportView
            key={`assets-${refreshKey}-${selectedAssetId}`}
            selectedAssetId={selectedAssetId}
            onClearSelection={() => setSelectedAssetId(null)}
          />
        )}

        {activeTab === 'projects' && (
          <ProjectsView
            key={`prj-${refreshKey}`}
            onSelectAsset={handleSelectAsset}
          />
        )}

        {activeTab === 'operations' && (
          <OperationsView
            key={`ops-${refreshKey}`}
            onSelectAsset={handleSelectAsset}
          />
        )}
      </main>

      <footer style={{
        borderTop: '1px solid rgba(255, 255, 255, 0.07)',
        padding: '22px 24px',
        background: 'rgba(5, 8, 15, 0.92)',
        backdropFilter: 'blur(16px)',
        fontSize: '0.8rem',
        color: '#64748b',
        textAlign: 'center',
        marginTop: 'auto',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, flexWrap: 'wrap' }}>
          <span style={{ fontWeight: 700, color: '#94a3b8' }}>
            PRAVI R&B Gujarat
          </span>
          <span>·</span>
          <span>Digital Infrastructure Lifecycle & GIS Asset Management Engine</span>
          <span>·</span>
          <span style={{ color: '#10b981', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <span className="live-pulse-dot" style={{ backgroundColor: '#10b981', width: 6, height: 6 }} />
            Live Mongo Sync Active
          </span>
        </div>
        <div style={{ marginTop: 6, fontSize: '0.72rem', color: '#475569' }}>
          Compliant with IRC:SP:35, Indian CPWD Infrastructure Standards & PIARC Asset Management Guidelines · Government of Gujarat
        </div>
      </footer>
    </div>
  );
}

export function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <MainContent />
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;
