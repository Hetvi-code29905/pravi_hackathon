import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  BuildingIcon, RoadIcon, BridgeIcon, Search, Filter, AlertTriangle,
  ShieldAlert, CheckCircle, Clock, IndianRupee, FileText, Wrench,
  ActivityIcon, ArrowRight, Plus, ChevronRight, UserIcon
} from '../components/Icons';

export const AssetPassportView = ({ selectedAssetId, onClearSelection }) => {
  const { user } = useAuth();
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [assetDetails, setAssetDetails] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [components, setComponents] = useState([]);
  const [inspections, setInspections] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [costs, setCosts] = useState(null);
  const [lifecycleInfo, setLifecycleInfo] = useState(null);

  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedCondition, setSelectedCondition] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('');

  // Modals
  const [transitionModalOpen, setTransitionModalOpen] = useState(false);
  const [transitionStage, setTransitionStage] = useState('');
  const [transitionNotes, setTransitionNotes] = useState('');
  const [transitionLoading, setTransitionLoading] = useState(false);

  const [inspectionModalOpen, setInspectionModalOpen] = useState(false);
  const [inspectionForm, setInspectionForm] = useState({
    inspection_type: 'ROUTINE',
    inspection_date: new Date().toISOString().split('T')[0],
    inspector_name: user?.full_name || 'Inspector',
    overall_condition: 'GOOD',
    condition_score: 80,
    findings: '',
    recommendations: '',
    requires_immediate_action: false,
  });

  const [maintenanceModalOpen, setMaintenanceModalOpen] = useState(false);
  const [maintenanceForm, setMaintenanceForm] = useState({
    maintenance_type: 'PREVENTIVE',
    title: '',
    description: '',
    priority: 'MEDIUM',
    estimated_cost: 10,
    scheduled_date: new Date().toISOString().split('T')[0],
  });

  const [riskModalOpen, setRiskModalOpen] = useState(false);
  const [riskForm, setRiskForm] = useState({
    criticality: 'MEDIUM',
    safety_impact: 'LOW',
    service_impact: 'LOW',
  });

  const fetchAssetsList = async () => {
    try {
      setLoading(true);
      const res = await api.listAssets({
        search: search || undefined,
        infrastructure_class_code: selectedClass || undefined,
        condition_rating: selectedCondition || undefined,
        risk_level: selectedRisk || undefined,
      });
      setAssets(res.items || []);

      if (selectedAssetId) {
        const found = (res.items || []).find((a) => a.id === selectedAssetId);
        if (found) loadAssetPassport(found);
      } else if (!selectedAsset && res.items?.length > 0) {
        loadAssetPassport(res.items[0]);
      }
    } catch (err) {
      console.error("Error loading assets list:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssetsList();
  }, [selectedClass, selectedCondition, selectedRisk]);

  useEffect(() => {
    if (selectedAssetId && assets.length > 0) {
      const match = assets.find((a) => a.id === selectedAssetId);
      if (match) loadAssetPassport(match);
    }
  }, [selectedAssetId, assets]);

  const loadAssetPassport = async (asset) => {
    setSelectedAsset(asset);
    setDetailsLoading(true);
    try {
      const [fullAsset, lc, tl, comps, insp, maint, docs, csts] = await Promise.all([
        api.getAsset(asset.id),
        api.getAssetLifecycle(asset.id),
        api.getAssetTimeline(asset.id),
        api.getAssetComponents(asset.id),
        api.listInspections(asset.id),
        api.listMaintenance(asset.id),
        api.getAssetDocuments(asset.id),
        api.getAssetCosts(asset.id),
      ]);
      setAssetDetails(fullAsset);
      setLifecycleInfo(lc);
      setTimeline(tl.timeline || []);
      setComponents(comps || []);
      setInspections(insp || []);
      setMaintenance(maint || []);
      setDocuments(docs || []);
      setCosts(csts);

      if (lc.allowed_transitions?.length > 0) {
        setTransitionStage(lc.allowed_transitions[0].to_stage);
      }
    } catch (err) {
      console.error("Error loading passport details:", err);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleExecuteTransition = async (e) => {
    e.preventDefault();
    if (!transitionStage) return;
    try {
      setTransitionLoading(true);
      await api.transitionAsset(selectedAsset.id, {
        to_stage: transitionStage,
        notes: transitionNotes,
      });
      setTransitionModalOpen(false);
      setTransitionNotes('');
      // Refresh passport
      loadAssetPassport(selectedAsset);
      fetchAssetsList();
      alert(`✅ Lifecycle transitioned successfully to ${transitionStage}`);
    } catch (err) {
      alert(`Transition error: ${err.message}`);
    } finally {
      setTransitionLoading(false);
    }
  };

  const handleRecordInspection = async (e) => {
    e.preventDefault();
    try {
      await api.createInspection(selectedAsset.id, inspectionForm);
      setInspectionModalOpen(false);
      loadAssetPassport(selectedAsset);
      fetchAssetsList();
      alert("✅ On-site inspection recorded successfully. Condition & Risk recalculated.");
    } catch (err) {
      alert("Inspection error: " + err.message);
    }
  };

  const handleScheduleMaintenance = async (e) => {
    e.preventDefault();
    try {
      await api.createMaintenance(selectedAsset.id, maintenanceForm);
      setMaintenanceModalOpen(false);
      loadAssetPassport(selectedAsset);
      alert("✅ Maintenance work order scheduled successfully.");
    } catch (err) {
      alert("Maintenance error: " + err.message);
    }
  };

  const handleAssessRisk = async (e) => {
    e.preventDefault();
    try {
      await api.assessRisk(selectedAsset.id, riskForm);
      setRiskModalOpen(false);
      loadAssetPassport(selectedAsset);
      fetchAssetsList();
      alert("✅ Risk assessment evaluated and updated across portfolio.");
    } catch (err) {
      alert("Risk assessment error: " + err.message);
    }
  };

  const getClassIcon = (code) => {
    if (code === 'BUILDING') return <BuildingIcon size={18} color="#60a5fa" />;
    if (code === 'ROAD') return <RoadIcon size={18} color="#34d399" />;
    return <BridgeIcon size={18} color="#fbbf24" />;
  };

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: 24, width: '100%', boxSizing: 'border-box' }}>
      {/* Search & Filter Header Bar */}
      <div className="glass-card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 260 }}>
          <Search size={18} color="#64748b" />
          <input
            type="text"
            className="input-field"
            placeholder="Search by asset code, name, city, district..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchAssetsList()}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <select
            className="input-field"
            style={{ width: 'auto' }}
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
          >
            <option value="">All Classes</option>
            <option value="BUILDING">Buildings</option>
            <option value="ROAD">Roads</option>
            <option value="BRIDGE">Bridges</option>
          </select>

          <select
            className="input-field"
            style={{ width: 'auto' }}
            value={selectedCondition}
            onChange={(e) => setSelectedCondition(e.target.value)}
          >
            <option value="">All Conditions</option>
            <option value="EXCELLENT">Excellent</option>
            <option value="GOOD">Good</option>
            <option value="FAIR">Fair</option>
            <option value="POOR">Poor</option>
            <option value="CRITICAL">Critical</option>
          </select>

          <select
            className="input-field"
            style={{ width: 'auto' }}
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>
        </div>
      </div>

      {/* Main Split Layout: Left Inventory List, Right Asset Passport Detail */}
      <div className="asset-passport-grid">
        {/* Left Side: Asset Master Inventory */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 4px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#94a3b8' }}>
              PHYSICAL ASSETS ({assets.length})
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 'calc(100vh - 230px)', overflowY: 'auto' }}>
            {assets.map((ast) => {
              const isSelected = selectedAsset?.id === ast.id;
              return (
                <div
                  key={ast.id}
                  onClick={() => loadAssetPassport(ast)}
                  className={`glass-card ${isSelected ? '' : 'glass-card-interactive'}`}
                  style={{
                    padding: 16,
                    borderColor: isSelected ? 'var(--border-focus)' : 'var(--border-subtle)',
                    background: isSelected ? 'rgba(30, 41, 59, 0.9)' : 'var(--bg-card)',
                    boxShadow: isSelected ? '0 0 20px rgba(59, 130, 246, 0.25)' : 'none',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {getClassIcon(ast.infrastructure_class_code)}
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', fontWeight: 700, color: '#60a5fa' }}>
                        {ast.code}
                      </span>
                    </div>
                    <span className={`badge badge-${ast.current_condition_rating?.toLowerCase()}`}>
                      {ast.current_condition_rating}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#f8fafc', marginBottom: 6 }}>
                    {ast.name}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8' }}>
                    <span>{ast.location?.district || 'Gujarat'} · {ast.asset_type_name?.split('/')[0]}</span>
                    <span style={{
                      fontWeight: 700,
                      color: ast.current_risk_level === 'CRITICAL' ? '#f87171' : ast.current_risk_level === 'HIGH' ? '#fb923c' : '#34d399',
                    }}>
                      Risk: {ast.current_risk_level}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side: The Digital Asset Passport */}
        {selectedAsset && assetDetails ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20, minWidth: 0, width: '100%' }}>
            {/* Passport Banner Card */}
            <div className="glass-card" style={{ padding: 24, position: 'relative', overflow: 'hidden' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      color: '#93c5fd',
                      background: 'rgba(59, 130, 246, 0.15)',
                      padding: '3px 10px',
                      borderRadius: 6,
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                    }}>
                      {assetDetails.code}
                    </span>
                    <span className={`badge badge-${assetDetails.infrastructure_class_code?.toLowerCase()}`}>
                      {assetDetails.infrastructure_class_code}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                      {assetDetails.asset_type_name}
                    </span>
                  </div>

                  <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
                    {assetDetails.name}
                  </h2>
                  <p style={{ fontSize: '0.84rem', color: '#94a3b8', marginTop: 4, maxWidth: 650 }}>
                    {assetDetails.description}
                  </p>
                </div>

                {/* Transition Action Trigger */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
                  <button
                    className="btn btn-primary"
                    onClick={() => setTransitionModalOpen(true)}
                  >
                    Execute Lifecycle Transition <ArrowRight size={15} />
                  </button>
                  <span style={{ fontSize: '0.74rem', color: '#94a3b8' }}>
                    Current State: <strong style={{ color: '#38bdf8' }}>{assetDetails.current_stage}</strong>
                  </span>
                </div>
              </div>

              {/* Lifecycle State Machine Visualizer */}
              <div style={{ marginTop: 22, paddingTop: 18, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', marginBottom: 12 }}>
                  Lifecycle State Machine Progression
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, overflowX: 'auto', paddingBottom: 6 }}>
                  {lifecycleInfo?.template?.stages?.map((stage, idx) => {
                    const isCurrent = stage.code === assetDetails.current_stage;
                    const isAllowedNext = lifecycleInfo?.allowed_transitions?.some((t) => t.to_stage === stage.code);

                    return (
                      <React.Fragment key={stage.code}>
                        <div
                          style={{
                            padding: '7px 12px',
                            borderRadius: 8,
                            fontSize: '0.78rem',
                            fontWeight: isCurrent ? 800 : 600,
                            whiteSpace: 'nowrap',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            background: isCurrent
                              ? 'linear-gradient(135deg, #2563eb, #1d4ed8)'
                              : isAllowedNext
                              ? 'rgba(16, 185, 129, 0.15)'
                              : 'rgba(255, 255, 255, 0.04)',
                            color: isCurrent ? '#ffffff' : isAllowedNext ? '#34d399' : '#64748b',
                            border: '1px solid',
                            borderColor: isCurrent
                              ? '#60a5fa'
                              : isAllowedNext
                              ? 'rgba(16, 185, 129, 0.4)'
                              : 'rgba(255, 255, 255, 0.05)',
                            boxShadow: isCurrent ? '0 0 16px rgba(37, 99, 235, 0.4)' : 'none',
                          }}
                        >
                          {isCurrent && <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#60a5fa' }} />}
                          {stage.name || stage.code}
                          {isAllowedNext && <span style={{ fontSize: '0.68rem', color: '#10b981' }}>★ Next</span>}
                        </div>
                        {idx < lifecycleInfo.template.stages.length - 1 && (
                          <ChevronRight size={14} color="rgba(255, 255, 255, 0.2)" />
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Condition, Risk & Next Action Triage Bar */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
              {/* Condition Gauge */}
              <div className="glass-card" style={{ padding: 18 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                    Condition Health
                  </span>
                  <button className="btn btn-secondary btn-sm" onClick={() => setInspectionModalOpen(true)}>
                    + Record Audit
                  </button>
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 8 }}>
                  <span style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
                    {assetDetails.current_condition_score || '--'}
                  </span>
                  <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>/100</span>
                  <span className={`badge badge-${assetDetails.current_condition_rating?.toLowerCase()}`} style={{ marginLeft: 'auto' }}>
                    {assetDetails.current_condition_rating}
                  </span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: 6 }}>
                  Last audit: {assetDetails.last_inspection_date || 'None'}
                </div>
              </div>

              {/* Multi-Factor Risk Score */}
              <div className="glass-card" style={{ padding: 18 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
                    Risk Evaluation
                  </span>
                  <button className="btn btn-secondary btn-sm" onClick={() => setRiskModalOpen(true)}>
                    Re-Score Risk
                  </button>
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 8 }}>
                  <span style={{ fontSize: '2rem', fontWeight: 800, color: assetDetails.current_risk_level === 'CRITICAL' ? '#f87171' : '#f8fafc' }}>
                    {assetDetails.risk_score || '--'}
                  </span>
                  <span className={`badge badge-${assetDetails.current_risk_level === 'CRITICAL' ? 'critical' : 'poor'}`} style={{ marginLeft: 'auto' }}>
                    {assetDetails.current_risk_level} RISK
                  </span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: 6 }}>
                  Condition × Criticality × Safety Impact
                </div>
              </div>

              {/* Recommended Next Action */}
              <div className="glass-card" style={{ padding: 18, borderLeft: '4px solid #f59e0b' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase' }}>
                    Recommended Next Action
                  </span>
                  <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: 4,
                    background: assetDetails.next_action_priority === 'URGENT' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: assetDetails.next_action_priority === 'URGENT' ? '#f87171' : '#fbbf24',
                  }}>
                    {assetDetails.next_action_priority}
                  </span>
                </div>
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc', marginTop: 8 }}>
                  {assetDetails.next_action}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: 6 }}>
                  Due Target: <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{assetDetails.next_action_due || 'ASAP'}</span>
                </div>
              </div>
            </div>

            {/* Passport Detail Tabs */}
            <div className="glass-card" style={{ overflow: 'hidden', minWidth: 0, width: '100%' }}>
              <div className="tabs-scrollable" style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.08)', background: 'rgba(0, 0, 0, 0.2)' }}>
                {[
                  { id: 'overview', label: 'Overview & Specs' },
                  { id: 'timeline', label: `Lifecycle Timeline (${timeline.length})` },
                  { id: 'components', label: `Sub-Components (${components.length})` },
                  { id: 'inspections', label: `Inspections (${inspections.length})` },
                  { id: 'maintenance', label: `Maintenance Logs (${maintenance.length})` },
                  { id: 'costs', label: 'Life-Cycle Costing' },
                  { id: 'documents', label: `Documents (${documents.length})` },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setActiveTab(t.id)}
                    style={{
                      padding: '14px 18px',
                      background: activeTab === t.id ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                      border: 'none',
                      borderBottom: activeTab === t.id ? '2px solid #3b82f6' : '2px solid transparent',
                      color: activeTab === t.id ? '#60a5fa' : '#94a3b8',
                      fontSize: '0.84rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              <div style={{ padding: 22 }}>
                {/* 1. Overview Tab */}
                {activeTab === 'overview' && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                      <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>
                        Administrative Custody & Operations
                      </h4>
                      <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 14, borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.84rem' }}>
                        <div><strong>Custodian:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.responsibility?.custodian || 'R&B Department'}</span></div>
                        <div><strong>Operating Agency:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.responsibility?.operator || 'Gujarat Government'}</span></div>
                        <div><strong>Maintenance Wing:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.responsibility?.maintenance_agency || 'State Circle'}</span></div>
                        <div><strong>Commissioned Date:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.commissioned_date || 'N/A'}</span></div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                      <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>
                        Location & Geometry
                      </h4>
                      <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 14, borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.84rem' }}>
                        <div><strong>District:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.location?.district}</span></div>
                        <div><strong>Taluka / City:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.location?.city || assetDetails.location?.taluka}</span></div>
                        <div><strong>Address:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.location?.address}</span></div>
                        <div><strong>GPS Coordinates:</strong> <span style={{ color: '#60a5fa', fontFamily: 'var(--font-mono)' }}>{assetDetails.location?.latitude}, {assetDetails.location?.longitude}</span></div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                      <h4 style={{ fontSize: '0.85rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>
                        Valuation & Planned Life
                      </h4>
                      <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 14, borderRadius: 8, display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.84rem' }}>
                        <div><strong>Estimated Book Value:</strong> <span style={{ color: '#34d399', fontWeight: 700 }}>₹{assetDetails.estimated_value} Lakhs</span></div>
                        <div><strong>Replacement Valuation:</strong> <span style={{ color: '#cbd5e1' }}>₹{assetDetails.replacement_value} Lakhs</span></div>
                        <div><strong>Design Life:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.planned_lifecycle?.design_life_years || 50} Years</span></div>
                        <div><strong>Expected End of Life:</strong> <span style={{ color: '#cbd5e1' }}>{assetDetails.planned_lifecycle?.expected_end_of_life || '2075'}</span></div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. Unified Timeline Tab */}
                {activeTab === 'timeline' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 14, position: 'relative' }}>
                    {timeline.map((ev, idx) => (
                      <div
                        key={idx}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 16,
                          paddingLeft: 12,
                          borderLeft: '2px solid rgba(59, 130, 246, 0.3)',
                          position: 'relative',
                        }}
                      >
                        <div style={{
                          position: 'absolute',
                          left: -6,
                          top: 4,
                          width: 10,
                          height: 10,
                          borderRadius: '50%',
                          background: ev.type === 'lifecycle' ? '#3b82f6' : ev.type === 'inspection' ? '#10b981' : '#f59e0b',
                        }} />
                        <div style={{ flex: 1, background: 'rgba(255, 255, 255, 0.02)', padding: 12, borderRadius: 8 }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                            <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc' }}>{ev.title}</span>
                            <span style={{ fontSize: '0.74rem', color: '#64748b' }}>{new Date(ev.date).toLocaleDateString()}</span>
                          </div>
                          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{ev.description}</p>
                          <div style={{ fontSize: '0.72rem', color: '#60a5fa', marginTop: 4 }}>By: {ev.performed_by}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* 3. Sub-Components Tab */}
                {activeTab === 'components' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
                      {components.map((comp) => (
                        <div key={comp.id} style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: 8, padding: 14 }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                            <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 600 }}>{comp.component_type}</span>
                            <span className={`badge badge-${comp.condition?.toLowerCase()}`}>
                              {comp.condition} ({comp.condition_score || '--'}%)
                            </span>
                          </div>
                          <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.9rem' }}>{comp.name}</div>
                          {comp.is_critical && (
                            <div style={{ fontSize: '0.7rem', color: '#f87171', marginTop: 6, fontWeight: 700 }}>
                              ⚠ CRITICAL COMPONENT
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 4. Inspections Tab */}
                {activeTab === 'inspections' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <button className="btn btn-primary btn-sm" onClick={() => setInspectionModalOpen(true)}>
                        <Plus size={14} /> Record New Field Inspection
                      </button>
                    </div>
                    {inspections.map((insp) => (
                      <div key={insp.id} style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: 8, padding: 16 }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                          <div>
                            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f8fafc' }}>
                              {insp.inspection_type} Inspection
                            </span>
                            <span style={{ fontSize: '0.78rem', color: '#94a3b8', marginLeft: 10 }}>
                              {insp.inspection_date} · Inspector: {insp.inspector_name}
                            </span>
                          </div>
                          <span className={`badge badge-${insp.overall_condition?.toLowerCase()}`}>
                            {insp.overall_condition} ({insp.condition_score}/100)
                          </span>
                        </div>
                        <p style={{ fontSize: '0.82rem', color: '#cbd5e1' }}><strong>Findings:</strong> {insp.findings}</p>
                        <p style={{ fontSize: '0.82rem', color: '#fbbf24', marginTop: 4 }}><strong>Recommendations:</strong> {insp.recommendations}</p>
                        {insp.defects_found?.length > 0 && (
                          <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
                            {insp.defects_found.map((d, i) => (
                              <span key={i} style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: 4, background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
                                Defect: {d}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* 5. Maintenance Tab */}
                {activeTab === 'maintenance' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <button className="btn btn-primary btn-sm" onClick={() => setMaintenanceModalOpen(true)}>
                        <Wrench size={14} /> Schedule Maintenance Work Order
                      </button>
                    </div>
                    {maintenance.map((m) => (
                      <div key={m.id} style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: 8, padding: 16 }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                          <div>
                            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f8fafc' }}>{m.title}</span>
                            <span style={{ fontSize: '0.74rem', color: '#94a3b8', marginLeft: 10 }}>Type: {m.maintenance_type}</span>
                          </div>
                          <span style={{
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            padding: '3px 8px',
                            borderRadius: 6,
                            background: m.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                            color: m.status === 'COMPLETED' ? '#34d399' : '#fbbf24',
                          }}>
                            {m.status}
                          </span>
                        </div>
                        <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>{m.description}</p>
                        <div style={{ display: 'flex', gap: 16, marginTop: 8, fontSize: '0.75rem', color: '#cbd5e1' }}>
                          <span>Cost: ₹{m.actual_cost || m.estimated_cost} Lakhs</span>
                          <span>Assigned: {m.assigned_agency}</span>
                          <span>Scheduled: {m.scheduled_date || 'N/A'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* 6. Life-Cycle Costing Tab */}
                {activeTab === 'costs' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
                      <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 8 }}>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Total Lifetime Cost Incurred</div>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#f8fafc', marginTop: 6 }}>
                          ₹{costs?.grand_total || 0} Lakhs
                        </div>
                      </div>
                      <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 8 }}>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Capital Construction Outlay</div>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8', marginTop: 6 }}>
                          ₹{costs?.total_by_type?.CAPITAL || 0} Lakhs
                        </div>
                      </div>
                      <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: 16, borderRadius: 8 }}>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Cumulative Maintenance Spend</div>
                        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981', marginTop: 6 }}>
                          ₹{costs?.total_by_type?.MAINTENANCE || 0} Lakhs
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 7. Documents Tab */}
                {activeTab === 'documents' && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
                    {documents.map((doc) => (
                      <div key={doc.id} style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: 8, padding: 14 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#38bdf8', marginBottom: 6 }}>
                          <FileText size={18} />
                          <span style={{ fontSize: '0.75rem', fontWeight: 700 }}>{doc.document_type}</span>
                        </div>
                        <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.88rem' }}>{doc.title}</div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: 4 }}>{doc.file_name}</div>
                        <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: 6 }}>Uploaded by: {doc.uploaded_by}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', height: 400 }}>
            Select an asset from the left inventory to open its Asset Passport
          </div>
        )}
      </div>

      {/* Modal 1: Lifecycle Transition Modal */}
      {transitionModalOpen && (
        <div className="modal-backdrop" onClick={() => setTransitionModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: 24 }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
              Execute Lifecycle State Machine Transition
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 18 }}>
              Validates transition rules, inspection sign-offs, and creates immutable audit event.
            </p>

            <form onSubmit={handleExecuteTransition} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: '#cbd5e1', fontWeight: 600 }}>Target Lifecycle Stage</label>
                <select
                  className="input-field"
                  value={transitionStage}
                  onChange={(e) => setTransitionStage(e.target.value)}
                  style={{ marginTop: 6 }}
                  required
                >
                  {lifecycleInfo?.allowed_transitions?.map((t) => (
                    <option key={t.to_stage} value={t.to_stage}>
                      {t.stage_name} ({t.to_stage}) {t.requires_inspection ? '· Requires Inspection' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: '#cbd5e1', fontWeight: 600 }}>Engineer Justification / Notes</label>
                <textarea
                  className="input-field"
                  rows={3}
                  value={transitionNotes}
                  onChange={(e) => setTransitionNotes(e.target.value)}
                  placeholder="State technical justification, quality clearance reference, or executive sanction..."
                  style={{ marginTop: 6 }}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setTransitionModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={transitionLoading}>
                  {transitionLoading ? "Transitioning..." : "Confirm & Commit State Change"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: Record Inspection Modal */}
      {inspectionModalOpen && (
        <div className="modal-backdrop" onClick={() => setInspectionModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: 24 }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
              Record Quality Control / Field Inspection
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 18 }}>
              Updates structural, functional and safety condition ratings. Auto-triggers Risk Engine recalculation.
            </p>

            <form onSubmit={handleRecordInspection} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Inspection Type</label>
                  <select
                    className="input-field"
                    value={inspectionForm.inspection_type}
                    onChange={(e) => setInspectionForm({ ...inspectionForm, inspection_type: e.target.value })}
                  >
                    <option value="ROUTINE">Routine Periodic</option>
                    <option value="SPECIAL">Special Structural Audit</option>
                    <option value="EMERGENCY">Emergency Assessment</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Overall Condition Rating</label>
                  <select
                    className="input-field"
                    value={inspectionForm.overall_condition}
                    onChange={(e) => setInspectionForm({ ...inspectionForm, overall_condition: e.target.value })}
                  >
                    <option value="EXCELLENT">Excellent</option>
                    <option value="GOOD">Good</option>
                    <option value="FAIR">Fair</option>
                    <option value="POOR">Poor</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>
                  Condition Score (0 - 100): <strong>{inspectionForm.condition_score}</strong>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={inspectionForm.condition_score}
                  onChange={(e) => setInspectionForm({ ...inspectionForm, condition_score: parseFloat(e.target.value) })}
                  style={{ width: '100%', marginTop: 6 }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Detailed Findings</label>
                <textarea
                  className="input-field"
                  rows={2}
                  value={inspectionForm.findings}
                  onChange={(e) => setInspectionForm({ ...inspectionForm, findings: e.target.value })}
                  placeholder="Record structural deflections, crack patterns, surface spalling..."
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Recommended Intervention</label>
                <input
                  type="text"
                  className="input-field"
                  value={inspectionForm.recommendations}
                  onChange={(e) => setInspectionForm({ ...inspectionForm, recommendations: e.target.value })}
                  placeholder="e.g., Immediate bearing jacketing, epoxy injection..."
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setInspectionModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-success">
                  Submit Inspection Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 3: Schedule Maintenance Modal */}
      {maintenanceModalOpen && (
        <div className="modal-backdrop" onClick={() => setMaintenanceModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: 24 }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
              Issue Maintenance Work Order
            </h3>
            <form onSubmit={handleScheduleMaintenance} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Intervention Title</label>
                <input
                  type="text"
                  className="input-field"
                  value={maintenanceForm.title}
                  onChange={(e) => setMaintenanceForm({ ...maintenanceForm, title: e.target.value })}
                  placeholder="e.g., Expansion Joint Resealing & Bearing Replacement"
                  required
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Maintenance Type</label>
                  <select
                    className="input-field"
                    value={maintenanceForm.maintenance_type}
                    onChange={(e) => setMaintenanceForm({ ...maintenanceForm, maintenance_type: e.target.value })}
                  >
                    <option value="PREVENTIVE">Preventive Maintenance</option>
                    <option value="CORRECTIVE">Corrective Repair</option>
                    <option value="REHABILITATION">Structural Rehabilitation</option>
                    <option value="RECONSTRUCTION">Reconstruction</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Estimated Cost (₹ Lakhs)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={maintenanceForm.estimated_cost}
                    onChange={(e) => setMaintenanceForm({ ...maintenanceForm, estimated_cost: parseFloat(e.target.value) })}
                    required
                  />
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setMaintenanceModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Issue Work Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 4: Risk Re-Assessment Modal */}
      {riskModalOpen && (
        <div className="modal-backdrop" onClick={() => setRiskModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: 24 }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
              Trigger Multi-Factor Risk Assessment Engine
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 18 }}>
              Evaluates asset condition score with asset criticality, public safety impact, and service disruption impact.
            </p>
            <form onSubmit={handleAssessRisk} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Asset Criticality</label>
                <select
                  className="input-field"
                  value={riskForm.criticality}
                  onChange={(e) => setRiskForm({ ...riskForm, criticality: e.target.value })}
                >
                  <option value="LOW">Low (Local access / non-critical)</option>
                  <option value="MEDIUM">Medium (District connection / general admin)</option>
                  <option value="HIGH">High (Major highway / river bridge / apex hospital)</option>
                  <option value="CRITICAL">Critical (Life safety / state lifeline)</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Public Safety Impact</label>
                <select
                  className="input-field"
                  value={riskForm.safety_impact}
                  onChange={(e) => setRiskForm({ ...riskForm, safety_impact: e.target.value })}
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical (Catastrophic collapse risk)</option>
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setRiskModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Compute Risk Score
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
