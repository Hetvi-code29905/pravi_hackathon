import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import { Layers, BuildingIcon, RoadIcon, BridgeIcon, Plus, ArrowRight, IndianRupee, CheckCircle, Clock, Sparkles, Check, ChevronRight } from '../components/Icons';

const PROJECT_STAGES = [
  'NEED', 'PLANNING', 'DESIGN', 'TENDER', 'CONSTRUCTION', 'QUALITY_ACCEPTANCE', 'COMMISSIONING', 'HANDOVER'
];

export const ProjectsView = ({ onSelectAsset }) => {
  const { user } = useAuth();
  const { notify } = useNotification();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState(null);
  const [advancingId, setAdvancingId] = useState(null);

  // New Project Modal
  const [newProjectModal, setNewProjectModal] = useState(false);
  const [classes, setClasses] = useState([]);
  const [assetTypes, setAssetTypes] = useState([]);
  const [newProjectForm, setNewProjectForm] = useState({
    name: '',
    description: '',
    infrastructure_class_id: '',
    asset_type_id: '',
    estimated_cost: 5000,
    sanctioned_cost: 4800,
    contractor: '',
    supervising_officer: '',
  });

  // Handover Modal
  const [handoverModal, setHandoverModal] = useState(false);
  const [handoverForm, setHandoverForm] = useState({
    name: '',
    custodian: 'Roads & Buildings Department',
    operator: 'Gujarat State Authority',
    maintenance_agency: 'R&B Maintenance Division',
  });

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const res = await api.listProjects();
      setProjects(res.items || []);
      const cls = await api.getInfrastructureClasses();
      setClasses(cls || []);
      if (cls && cls.length > 0) {
        setNewProjectForm((prev) => ({ ...prev, infrastructure_class_id: cls[0].id }));
        const types = await api.getAssetTypes(cls[0].id);
        setAssetTypes(types || []);
        if (types && types.length > 0) setNewProjectForm((prev) => ({ ...prev, asset_type_id: types[0].id }));
      }
    } catch (err) {
      console.error("Error fetching projects:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleClassChange = async (classId) => {
    setNewProjectForm((prev) => ({ ...prev, infrastructure_class_id: classId }));
    const types = await api.getAssetTypes(classId);
    setAssetTypes(types || []);
    if (types && types.length > 0) setNewProjectForm((prev) => ({ ...prev, asset_type_id: types[0].id }));
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await api.createProject(newProjectForm);
      setNewProjectModal(false);
      await fetchProjects();
      notify.success("Capital Project Sanctioned", `Project "${newProjectForm.name}" created in PLANNING stage in MongoDB.`);
    } catch (err) {
      notify.error("Project Creation Failed", err.message);
    }
  };

  const handleAdvanceStage = async (prj) => {
    setAdvancingId(prj.id);
    try {
      const res = await api.advanceProject(prj.id);
      notify.lifecycle(
        `Lifecycle Advanced: ${res.old_status} → ${res.new_status}`,
        `Project ${prj.code} advanced by ${user?.full_name || user?.role}. MongoDB registry updated.`
      );
      await fetchProjects();
    } catch (err) {
      notify.error("Stage Progression Failed", err.message);
    } finally {
      setAdvancingId(null);
    }
  };

  const handleOpenHandover = (project) => {
    setSelectedProject(project);
    setHandoverForm({
      name: project.name,
      custodian: 'Roads & Buildings Department',
      operator: 'Gujarat State Authority',
      maintenance_agency: 'R&B Circle Division',
    });
    setHandoverModal(true);
  };

  const handleCommitHandover = async (e) => {
    e.preventDefault();
    try {
      const res = await api.handoverProjectToAsset(selectedProject.id, handoverForm);
      setHandoverModal(false);
      await fetchProjects();
      notify.lifecycle(
        "Project Handover Completed",
        `Physical Asset Passport ${res.asset?.code || 'Created'} is now live in MongoDB.`
      );
      if (onSelectAsset && res.asset?.id) {
        onSelectAsset(res.asset.id);
      }
    } catch (err) {
      notify.error("Handover Failed", err.message);
    }
  };

  const getStageColor = (status) => {
    switch (status) {
      case 'PLANNING':
      case 'NEED':
        return '#818cf8';
      case 'DESIGN':
      case 'TENDER':
        return '#38bdf8';
      case 'CONSTRUCTION':
        return '#f59e0b';
      case 'QUALITY_ACCEPTANCE':
      case 'COMMISSIONING':
        return '#06b6d4';
      case 'HANDOVER':
      case 'CLOSED':
        return '#10b981';
      default:
        return '#94a3b8';
    }
  };

  const isAuthorizedToAdvance = ['SECRETARY', 'ADMIN', 'ENGINEER'].includes((user?.role || '').toUpperCase());

  return (
    <div style={{ maxWidth: 1440, margin: '0 auto', padding: '28px 24px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
              Capital Projects & Handover Pipeline
            </h1>
            <span className="badge badge-road">
              {projects.length} Active Packages
            </span>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            Tracks temporary project lifecycle (PLANNING → DESIGN → TENDER → CONSTRUCTION → QUALITY → COMMISSIONING) and creates persistent Physical Asset Passports upon Handover.
          </p>
        </div>
        {isAuthorizedToAdvance && (
          <button className="btn btn-primary" onClick={() => setNewProjectModal(true)}>
            <Plus size={16} /> Sanction New Capital Project
          </button>
        )}
      </div>

      {/* Projects Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 20 }}>
        {projects.map((prj) => {
          const currentStageIndex = PROJECT_STAGES.indexOf(prj.status);
          const isReadyForHandover = prj.status === 'HANDOVER' || prj.status === 'COMMISSIONING';

          return (
            <div key={prj.id} className="glass-card" style={{ padding: 22, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', position: 'relative' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8' }}>
                    {prj.code}
                  </span>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '3px 10px',
                    borderRadius: 9999,
                    background: `${getStageColor(prj.status)}22`,
                    color: getStageColor(prj.status),
                    border: `1px solid ${getStageColor(prj.status)}44`,
                  }}>
                    {prj.status}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.08rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6, lineHeight: 1.3 }}>
                  {prj.name}
                </h3>
                <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 14, minHeight: 38 }}>
                  {prj.description || "Capital infrastructure package under R&B Gujarat jurisdiction."}
                </p>

                {/* Micro Pipeline Progress Bar */}
                <div style={{ marginBottom: 16, background: 'rgba(255, 255, 255, 0.03)', padding: '8px 10px', borderRadius: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#64748b', marginBottom: 4, fontWeight: 700 }}>
                    <span>STAGE {currentStageIndex + 1} OF 8</span>
                    <span style={{ color: getStageColor(prj.status) }}>{prj.status}</span>
                  </div>
                  <div style={{ height: 4, background: 'rgba(255, 255, 255, 0.1)', borderRadius: 2, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${Math.max(12, ((currentStageIndex + 1) / PROJECT_STAGES.length) * 100)}%`,
                      background: getStageColor(prj.status),
                      transition: 'width 0.3s ease',
                    }} />
                  </div>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: 12, borderRadius: 10, display: 'flex', flexDirection: 'column', gap: 7, fontSize: '0.8rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Sanctioned Capex:</span>
                    <span style={{ fontWeight: 700, color: '#34d399', fontFamily: 'var(--font-mono)' }}>₹{prj.sanctioned_cost || prj.estimated_cost} Lakhs</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>EPC Contractor:</span>
                    <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{prj.contractor || 'In Tender Stage'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8' }}>Supervising Division:</span>
                    <span style={{ color: '#cbd5e1' }}>{prj.supervising_officer || 'Executive Engineer R&B'}</span>
                  </div>
                </div>
              </div>

              {/* Action Controls */}
              <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
                <span style={{ fontSize: '0.74rem', color: '#64748b' }}>
                  Target: <strong>{prj.expected_completion || '2026-Q4'}</strong>
                </span>

                <div style={{ display: 'flex', gap: 8 }}>
                  {isReadyForHandover ? (
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() => handleOpenHandover(prj)}
                    >
                      <Sparkles size={14} /> Create Asset Passport →
                    </button>
                  ) : (
                    isAuthorizedToAdvance && (
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleAdvanceStage(prj)}
                        disabled={advancingId === prj.id}
                        title={`Advance from ${prj.status} to next lifecycle stage in MongoDB`}
                      >
                        <ChevronRight size={14} />
                        {advancingId === prj.id ? "Updating..." : "Advance Stage →"}
                      </button>
                    )
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal 1: Sanction New Project */}
      {newProjectModal && (
        <div className="modal-backdrop" onClick={() => setNewProjectModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: 26 }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
              Sanction New Capital Infrastructure Project
            </h3>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: 16 }}>
              Registers a new capital package in the Gujarat R&B project lifecycle pipeline in PLANNING stage.
            </p>

            <form onSubmit={handleCreateProject} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Project Title</label>
                <input
                  type="text"
                  className="input-field"
                  value={newProjectForm.name}
                  onChange={(e) => setNewProjectForm({ ...newProjectForm, name: e.target.value })}
                  placeholder="e.g. Surat-Navsari Coastal Highway Widening"
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Scope / Description</label>
                <textarea
                  className="input-field"
                  rows={2}
                  value={newProjectForm.description}
                  onChange={(e) => setNewProjectForm({ ...newProjectForm, description: e.target.value })}
                  placeholder="Detailed civil works scope..."
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Infrastructure Class</label>
                  <select
                    className="input-field"
                    value={newProjectForm.infrastructure_class_id}
                    onChange={(e) => handleClassChange(e.target.value)}
                  >
                    {classes.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Asset Type</label>
                  <select
                    className="input-field"
                    value={newProjectForm.asset_type_id}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, asset_type_id: e.target.value })}
                  >
                    {assetTypes.map((t) => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Estimated Cost (₹ Lakhs)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={newProjectForm.estimated_cost}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, estimated_cost: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Sanctioned Cost (₹ Lakhs)</label>
                  <input
                    type="number"
                    className="input-field"
                    value={newProjectForm.sanctioned_cost}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, sanctioned_cost: parseFloat(e.target.value) })}
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setNewProjectModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Sanction Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: Handover to Asset */}
      {handoverModal && selectedProject && (
        <div className="modal-backdrop" onClick={() => setHandoverModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: 26 }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc', marginBottom: 6 }}>
              Official Project Handover & Physical Asset Creation
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: 18 }}>
              Converts temporary project <strong>{selectedProject.code}</strong> into a permanent Physical Asset with full Digital Asset Passport in MongoDB.
            </p>

            <form onSubmit={handleCommitHandover} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Physical Asset Name</label>
                <input
                  type="text"
                  className="input-field"
                  value={handoverForm.name}
                  onChange={(e) => setHandoverForm({ ...handoverForm, name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Administrative Custodian</label>
                <input
                  type="text"
                  className="input-field"
                  value={handoverForm.custodian}
                  onChange={(e) => setHandoverForm({ ...handoverForm, custodian: e.target.value })}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#cbd5e1', fontWeight: 600 }}>Maintenance Division</label>
                <input
                  type="text"
                  className="input-field"
                  value={handoverForm.maintenance_agency}
                  onChange={(e) => setHandoverForm({ ...handoverForm, maintenance_agency: e.target.value })}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 10 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setHandoverModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-success">
                  <Sparkles size={15} /> Complete Handover & Create Passport
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
