import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import { Wrench, CheckCircle, AlertTriangle, ShieldAlert, Plus, Search, Filter, Sparkles, Check, X, Clock } from '../components/Icons';

export const OperationsView = ({ onSelectAsset }) => {
  const { user } = useAuth();
  const { notify } = useNotification();
  const [activeSubTab, setActiveSubTab] = useState('maintenance');
  const [inspections, setInspections] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);

  // Status update modal for maintenance
  const [updateMaintModal, setUpdateMaintModal] = useState(false);
  const [selectedMaint, setSelectedMaint] = useState(null);
  const [maintStatus, setMaintStatus] = useState('COMPLETED');
  const [workDone, setWorkDone] = useState('');
  const [conditionAfter, setConditionAfter] = useState('GOOD');

  const fetchOperationsData = async () => {
    try {
      setLoading(true);
      const [inspRes, maintRes, issuesRes] = await Promise.all([
        api.listInspections(),
        api.listMaintenance(),
        api.listIssues(),
      ]);
      setInspections(inspRes.items || []);
      setMaintenance(maintRes.items || []);
      setIssues(issuesRes.items || []);
    } catch (err) {
      console.error("Error loading operations:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOperationsData();
  }, []);

  const handleUpdateMaintStatus = async (e) => {
    e.preventDefault();
    try {
      await api.updateMaintenance(selectedMaint.id, {
        status: maintStatus,
        work_done: workDone,
        condition_after: maintStatus === 'COMPLETED' ? conditionAfter : undefined,
      });
      setUpdateMaintModal(false);
      await fetchOperationsData();
      notify.success("Work Order Updated", `Work order ${selectedMaint.code || ''} marked as ${maintStatus}.`);
    } catch (err) {
      notify.error("Update Failed", err.message);
    }
  };

  return (
    <div style={{ maxWidth: 1440, margin: '0 auto', padding: '28px 24px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
            Field Operations, Audits & Interventions
          </h1>
          <span className="badge badge-road">Active O&M Division</span>
        </div>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Executive command for active maintenance work orders, structural audits, and defect remediations across Gujarat infrastructure.
        </p>
      </div>

      {/* Operations Nav Pills */}
      <div style={{ display: 'flex', gap: 10, background: 'rgba(15, 23, 42, 0.5)', padding: '4px 6px', borderRadius: 12, border: '1px solid rgba(255, 255, 255, 0.08)', width: 'fit-content' }}>
        {[
          { id: 'maintenance', label: `Work Orders (${maintenance.length})` },
          { id: 'inspections', label: `Condition Audits (${inspections.length})` },
          { id: 'issues', label: `Defects & Distress (${issues.length})` },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveSubTab(t.id)}
            style={{
              padding: '8px 18px',
              borderRadius: 8,
              border: '1px solid',
              borderColor: activeSubTab === t.id ? 'rgba(56, 189, 248, 0.4)' : 'transparent',
              background: activeSubTab === t.id ? 'linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(37, 99, 235, 0.15) 100%)' : 'transparent',
              color: activeSubTab === t.id ? '#38bdf8' : '#94a3b8',
              fontWeight: activeSubTab === t.id ? 700 : 500,
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Maintenance Work Orders */}
      {activeSubTab === 'maintenance' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 20 }}>
            {maintenance.map((m) => (
              <div key={m.id} className="glass-card" style={{ padding: 22, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8' }}>
                      {m.code || 'WO-R&B-2026'}
                    </span>
                    <span className={`badge ${m.status === 'COMPLETED' ? 'badge-excellent' : m.status === 'IN_PROGRESS' ? 'badge-good' : 'badge-fair'}`}>
                      {m.status}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
                    {m.title || m.description || 'Structural Maintenance Order'}
                  </h3>
                  <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 14 }}>
                    {m.description || "Routine preventative maintenance package under Gujarat R&B specifications."}
                  </p>

                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 12, borderRadius: 10, display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.8rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Maintenance Type:</span>
                      <span style={{ color: '#f8fafc', fontWeight: 600 }}>{m.maintenance_type || 'PREVENTIVE'}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Contractor / Division:</span>
                      <span style={{ color: '#cbd5e1' }}>{m.contractor || m.assigned_division || 'R&B Maintenance Circle'}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#94a3b8' }}>Estimated Cost:</span>
                      <span style={{ color: '#34d399', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>₹{m.cost || 45} Lakhs</span>
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.74rem', color: '#64748b' }}>
                    Due: <strong>{m.scheduled_date || '2026-Q3'}</strong>
                  </span>

                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => {
                      setSelectedMaint(m);
                      setMaintStatus(m.status === 'COMPLETED' ? 'IN_PROGRESS' : 'COMPLETED');
                      setUpdateMaintModal(true);
                    }}
                  >
                    <Wrench size={14} /> Update Status
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Inspection Audits */}
      {activeSubTab === 'inspections' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 20 }}>
          {inspections.map((insp) => (
            <div key={insp.id} className="glass-card" style={{ padding: 22 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8' }}>
                  {insp.code || 'AUD-2026'}
                </span>
                <span className={`badge ${insp.overall_condition === 'EXCELLENT' ? 'badge-excellent' : insp.overall_condition === 'GOOD' ? 'badge-good' : 'badge-fair'}`}>
                  {insp.overall_condition || 'GOOD'} · PCI {insp.condition_score || 85}
                </span>
              </div>

              <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
                {insp.asset_name || 'Infrastructure Structural Audit'}
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 12 }}>
                {insp.summary || "180-Day periodic safety and distress assessment."}
              </p>

              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 12, borderRadius: 10, display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Auditor:</span>
                  <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{insp.inspector_name || 'Quality Division Lead'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Inspection Date:</span>
                  <span style={{ color: '#94a3b8' }}>{insp.inspection_date || '2026-03-15'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: Defects & Issues */}
      {activeSubTab === 'issues' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 20 }}>
          {issues.map((iss) => (
            <div key={iss.id} className="glass-card" style={{ padding: 22 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 700, color: '#f87171' }}>
                  {iss.code || 'ISSUE-2026'}
                </span>
                <span className={`badge ${iss.severity === 'CRITICAL' ? 'badge-critical' : iss.severity === 'HIGH' ? 'badge-poor' : 'badge-fair'}`}>
                  {iss.severity} SEVERITY
                </span>
              </div>

              <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
                {iss.title || 'Distress Notice'}
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 12 }}>
                {iss.description}
              </p>

              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 12, borderRadius: 10, display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Status:</span>
                  <span style={{ color: iss.status === 'RESOLVED' ? '#34d399' : '#fbbf24', fontWeight: 700 }}>{iss.status}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Recommended Action:</span>
                  <span style={{ color: '#cbd5e1' }}>{iss.recommended_action || 'Crack Sealing & Grouting'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Update Maintenance Modal */}
      {updateMaintModal && selectedMaint && (
        <div className="modal-backdrop" onClick={() => setUpdateMaintModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: 26 }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
              Update Work Order: {selectedMaint.code || selectedMaint.title}
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 16 }}>
              Log civil engineering work completion and update asset condition ratings.
            </p>

            <form onSubmit={handleUpdateMaintStatus} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Work Order Status</label>
                <select
                  className="input-field"
                  value={maintStatus}
                  onChange={(e) => setMaintStatus(e.target.value)}
                >
                  <option value="PLANNED">PLANNED</option>
                  <option value="IN_PROGRESS">IN_PROGRESS</option>
                  <option value="COMPLETED">COMPLETED</option>
                  <option value="VERIFIED">VERIFIED</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Work Done Summary</label>
                <textarea
                  className="input-field"
                  rows={3}
                  value={workDone}
                  onChange={(e) => setWorkDone(e.target.value)}
                  placeholder="Details of remedial works executed..."
                />
              </div>

              {maintStatus === 'COMPLETED' && (
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Condition Rating After Remediation</label>
                  <select
                    className="input-field"
                    value={conditionAfter}
                    onChange={(e) => setConditionAfter(e.target.value)}
                  >
                    <option value="EXCELLENT">EXCELLENT (PCI 90-100)</option>
                    <option value="GOOD">GOOD (PCI 75-89)</option>
                    <option value="FAIR">FAIR (PCI 60-74)</option>
                  </select>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setUpdateMaintModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Commit Status Update
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
