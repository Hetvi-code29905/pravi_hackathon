import React, { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import { BuildingIcon, RoadIcon, BridgeIcon, AlertTriangle, ShieldAlert } from './Icons';

/**
 * Donut Chart for Condition or Risk Distribution
 */
export const DonutChart = ({ data, total, title, size = 180 }) => {
  const [hovered, setHovered] = useState(null);
  const strokeWidth = 24;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  let accumulated = 0;
  const slices = data.map((item) => {
    const ratio = total > 0 ? item.value / total : 0;
    const strokeDasharray = `${ratio * circumference} ${circumference}`;
    const strokeDashoffset = -accumulated * circumference;
    accumulated += ratio;
    return { ...item, strokeDasharray, strokeDashoffset, ratio };
  });

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
      <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255, 255, 255, 0.05)"
            strokeWidth={strokeWidth}
          />
          {slices.map((slice, idx) => (
            <circle
              key={idx}
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={slice.color}
              strokeWidth={hovered === slice.label ? strokeWidth + 4 : strokeWidth}
              strokeDasharray={slice.strokeDasharray}
              strokeDashoffset={slice.strokeDashoffset}
              strokeLinecap="round"
              style={{
                transition: 'all 0.25s ease',
                cursor: 'pointer',
                opacity: hovered && hovered !== slice.label ? 0.45 : 1,
              }}
              onMouseEnter={() => setHovered(slice.label)}
              onMouseLeave={() => setHovered(null)}
            />
          ))}
        </svg>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none',
          }}
        >
          <span style={{ fontSize: '1.45rem', fontWeight: 800, color: '#f8fafc' }}>
            {hovered ? slices.find((s) => s.label === hovered)?.value : total}
          </span>
          <span style={{ fontSize: '0.68rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            {hovered || title || 'Total'}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 7, minWidth: 140 }}>
        {data.map((item, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 12,
              fontSize: '0.8rem',
              cursor: 'pointer',
              padding: '2px 6px',
              borderRadius: 4,
              background: hovered === item.label ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
              transition: 'background 0.15s ease',
            }}
            onMouseEnter={() => setHovered(item.label)}
            onMouseLeave={() => setHovered(null)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: item.color, flexShrink: 0 }} />
              <span style={{ color: '#cbd5e1' }}>{item.label}</span>
            </div>
            <span style={{ fontWeight: 700, color: '#f8fafc' }}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Lifecycle Stage Funnel Progress Bar
 */
export const LifecycleFunnel = ({ distribution = {} }) => {
  const stageMeta = [
    { code: 'PLANNING', label: 'Planning', color: '#6366f1' },
    { code: 'CONSTRUCTION', label: 'Construction', color: '#3b82f6' },
    { code: 'COMMISSIONED', label: 'Commissioned', color: '#06b6d4' },
    { code: 'OPERATIONAL', label: 'Operational', color: '#10b981' },
    { code: 'SPECIAL_MONITORING', label: 'Monitoring', color: '#f59e0b' },
    { code: 'MAINTENANCE', label: 'Maintenance', color: '#ec4899' },
    { code: 'MAJOR_REHABILITATION', label: 'Rehab', color: '#f97316' },
    { code: 'DECOMMISSIONED', label: 'Decommissioned', color: '#64748b' },
  ];

  const total = Object.values(distribution).reduce((a, b) => a + b, 0) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ height: 14, borderRadius: 8, overflow: 'hidden', display: 'flex', background: 'rgba(255, 255, 255, 0.05)', padding: 2 }}>
        {stageMeta.map((s) => {
          const count = distribution[s.code] || 0;
          if (count === 0) return null;
          const pct = (count / total) * 100;
          return (
            <div
              key={s.code}
              title={`${s.label}: ${count} assets (${pct.toFixed(0)}%)`}
              style={{
                width: `${pct}%`,
                background: s.color,
                borderRadius: 4,
                marginRight: 2,
                transition: 'width 0.3s ease',
              }}
            />
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: 8 }}>
        {stageMeta.map((s) => {
          const count = distribution[s.code] || 0;
          return (
            <div key={s.code} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.78rem' }}>
              <span style={{ width: 8, height: 8, borderRadius: 2, background: s.color }} />
              <span style={{ color: '#94a3b8' }}>{s.label}</span>
              <span style={{ fontWeight: 700, marginLeft: 'auto', color: '#f8fafc' }}>{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/**
 * Interactive 3x3 Risk Matrix: Probability vs Consequence
 */
export const RiskMatrix = ({ alerts = [], onSelectAsset }) => {
  const levels = ['HIGH', 'MEDIUM', 'LOW'];

  const getCellColor = (prob, cons) => {
    if (prob === 'HIGH' && (cons === 'HIGH' || cons === 'CRITICAL')) return 'rgba(239, 68, 68, 0.35)';
    if (prob === 'HIGH' || cons === 'CRITICAL') return 'rgba(249, 115, 22, 0.25)';
    if (prob === 'MEDIUM' || cons === 'HIGH') return 'rgba(245, 158, 11, 0.2)';
    return 'rgba(16, 185, 129, 0.15)';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontWeight: 600 }}>PROBABILITY vs CONSEQUENCE</span>
        <div style={{ display: 'flex', gap: 12, fontSize: '0.72rem' }}>
          <span style={{ color: '#34d399' }}>● Low</span>
          <span style={{ color: '#fbbf24' }}>● Med</span>
          <span style={{ color: '#fb923c' }}>● High</span>
          <span style={{ color: '#f87171' }}>● Critical</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '70px 1fr 1fr 1fr', gap: 6, fontSize: '0.75rem' }}>
        <div />
        <div style={{ textAlign: 'center', color: '#94a3b8', fontWeight: 600 }}>LOW</div>
        <div style={{ textAlign: 'center', color: '#94a3b8', fontWeight: 600 }}>MEDIUM</div>
        <div style={{ textAlign: 'center', color: '#94a3b8', fontWeight: 600 }}>HIGH</div>

        {levels.map((prob) => (
          <React.Fragment key={prob}>
            <div style={{ display: 'flex', alignItems: 'center', color: '#94a3b8', fontWeight: 600 }}>{prob}</div>
            {['LOW', 'MEDIUM', 'HIGH'].map((cons) => {
              const matching = alerts.filter(
                (a) => (a.risk_level === 'CRITICAL' && prob === 'HIGH' && cons === 'HIGH') ||
                       (a.risk_level === 'HIGH' && prob === 'HIGH' && cons === 'MEDIUM') ||
                       (a.risk_level === 'MEDIUM' && prob === 'MEDIUM') ||
                       (a.risk_level === 'LOW' && prob === 'LOW' && cons === 'LOW')
              );

              return (
                <div
                  key={`${prob}-${cons}`}
                  style={{
                    height: 52,
                    background: getCellColor(prob, cons),
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: 6,
                    padding: 4,
                    display: 'flex',
                    flexWrap: 'wrap',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 4,
                    overflow: 'hidden',
                  }}
                >
                  {matching.slice(0, 3).map((ast) => (
                    <button
                      key={ast.id}
                      onClick={() => onSelectAsset && onSelectAsset(ast.id)}
                      title={`${ast.name} (${ast.code})`}
                      style={{
                        padding: '2px 5px',
                        background: 'rgba(15, 23, 42, 0.9)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: 3,
                        color: '#f8fafc',
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                      }}
                    >
                      {ast.code.split('-')[1]}
                    </button>
                  ))}
                  {matching.length > 3 && (
                    <span style={{ fontSize: '0.62rem', color: '#cbd5e1' }}>+{matching.length - 3}</span>
                  )}
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
      <div style={{ textAlign: 'center', fontSize: '0.72rem', color: '#64748b' }}>CONSEQUENCE IMPACT →</div>
    </div>
  );
};

/**
 * Real Live Interactive Gujarat GIS Map using Leaflet.js
 * Features: Real OpenStreetMap / CartoDB tiles, Zoom In (+), Zoom Out (-), Pan, Real GPS Markers & Popups
 */
export const GujaratGisMap = ({ assets = [], onSelectAsset }) => {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [tileMode, setTileMode] = useState('VOYAGER'); // 'VOYAGER' or 'DARK'

  // Default Gujarat R&B asset coordinates fallback (if any asset doesn't have lat/lng)
  const defaultAssetCoords = {
    'ast-brg-001': { lat: 23.0225, lng: 72.5714, name: 'Atal Pedestrian Bridge, Sabarmati' },
    'ast-rd-002': { lat: 23.0753, lng: 72.5074, name: 'Sarkhej–Gandhinagar (SG) Highway' },
    'ast-bld-003': { lat: 23.0525, lng: 72.5950, name: 'New Civil Hospital 1200-Bed Trauma Complex' },
    'ast-brg-004': { lat: 21.7051, lng: 72.9959, name: 'Bharuch Old Golden Bridge' },
    'ast-rd-005': { lat: 21.1702, lng: 72.8311, name: 'Surat–Dumas Coastal Road' },
    'ast-rd-006': { lat: 22.3039, lng: 70.8022, name: 'Rajkot–Ahmedabad Greenfield Expressway' },
    'ast-bld-007': { lat: 22.3072, lng: 73.1812, name: 'Vadodara Central Bus Terminal Complex' },
    'ast-bld-008': { lat: 21.7645, lng: 72.1519, name: 'Bhavnagar R&B Quality Control Laboratory' },
  };

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Clean up previous instance if exists
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    // Initialize Leaflet map centered on Gujarat state
    const map = L.map(mapContainerRef.current, {
      center: [22.45, 71.9], // Geographic center of Gujarat
      zoom: 7,
      minZoom: 6,
      maxZoom: 18,
      zoomControl: true,
      scrollWheelZoom: true,
      attributionControl: true,
    });

    // Tile URLs: OpenStreetMap (free, no API key needed)
    const tileUrl = tileMode === 'DARK'
      ? 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
      : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

    L.tileLayer(tileUrl, {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      subdomains: 'abc',
      maxZoom: 19,
    }).addTo(map);

    // Add Live Asset Markers
    const markersList = [];

    assets.forEach((ast) => {
      let lat = ast.lat;
      let lng = ast.lng;

      if (!lat || !lng) {
        const fallback = defaultAssetCoords[ast.id] || defaultAssetCoords[ast.code?.toLowerCase()];
        if (fallback) {
          lat = fallback.lat;
          lng = fallback.lng;
        }
      }

      if (!lat || !lng) return;

      const isCritical = ast.risk_level === 'CRITICAL' || ast.condition_rating === 'CRITICAL';
      const isPoor = ast.condition_rating === 'POOR' || ast.risk_level === 'HIGH';
      const isFair = ast.condition_rating === 'FAIR' || ast.risk_level === 'MEDIUM';
      const color = isCritical ? '#ef4444' : isPoor ? '#f97316' : isFair ? '#f59e0b' : '#10b981';

      // Custom Glowing HTML Pin
      const customIcon = L.divIcon({
        className: 'rnb-leaflet-marker',
        html: `
          <div style="position: relative; display: flex; align-items: center; justify-content: center; cursor: pointer;">
            ${isCritical ? `
              <div style="
                position: absolute;
                width: 38px;
                height: 38px;
                border-radius: 50%;
                border: 2px solid #ef4444;
                opacity: 0.8;
                box-shadow: 0 0 12px #ef4444;
                animation: leafletPing 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;
              "></div>
            ` : ''}
            <div style="
              padding: 4px 9px;
              border-radius: 12px;
              background: #0f172a;
              border: 2px solid ${color};
              box-shadow: 0 4px 12px rgba(0,0,0,0.6), 0 0 8px ${color};
              color: #ffffff;
              font-size: 11px;
              font-weight: 800;
              font-family: 'Plus Jakarta Sans', sans-serif;
              white-space: nowrap;
              display: flex;
              align-items: center;
              gap: 6px;
            ">
              <span style="width: 8px; height: 8px; border-radius: 50%; background: ${color}; box-shadow: 0 0 6px ${color};"></span>
              <span>${ast.code ? ast.code.split('-')[1] : 'AST'}</span>
            </div>
          </div>
        `,
        iconSize: [60, 30],
        iconAnchor: [30, 15],
      });

      const marker = L.marker([lat, lng], { icon: customIcon }).addTo(map);

      // Rich Interactive Popup
      const popupHtml = `
        <div style="font-family: 'Plus Jakarta Sans', system-ui, sans-serif; min-width: 220px; color: #0f172a; padding: 4px;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 11px; font-weight: 800; color: #2563eb; letter-spacing: 0.02em;">${ast.code || ''}</span>
            <span style="font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; background: ${color}20; color: ${color}; border: 1px solid ${color};">
              PCI: ${ast.condition_score || '--'}/100 (${ast.condition_rating || 'Good'})
            </span>
          </div>
          <div style="font-size: 13px; font-weight: 800; color: #0f172a; line-height: 1.3; margin-bottom: 4px;">
            ${ast.name}
          </div>
          <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">
            📍 ${ast.district || 'Gujarat'}, Gujarat · ${ast.infrastructure_class_code || 'INFRA'}
          </div>
          <div style="font-size: 11px; color: #b45309; margin-bottom: 8px; background: #fffbeb; padding: 4px 6px; border-radius: 4px; border: 1px solid #fef3c7;">
            <strong>Action Due:</strong> ${ast.next_action || 'Routine QC Audit'}
          </div>
          <button
            id="passport-btn-${ast.id}"
            style="
              width: 100%;
              padding: 7px;
              background: linear-gradient(135deg, #1d4ed8, #0284c7);
              color: #ffffff;
              border: none;
              border-radius: 6px;
              font-weight: 700;
              font-size: 11px;
              cursor: pointer;
              box-shadow: 0 2px 6px rgba(2, 132, 199, 0.4);
            "
          >
            Open Digital Asset Passport →
          </button>
        </div>
      `;

      marker.bindPopup(popupHtml);

      marker.on('popupopen', () => {
        setSelectedAsset(ast);
        setTimeout(() => {
          const btn = document.getElementById(`passport-btn-${ast.id}`);
          if (btn) {
            btn.onclick = () => {
              if (onSelectAsset) onSelectAsset(ast.id);
            };
          }
        }, 50);
      });

      marker.on('click', () => {
        setSelectedAsset(ast);
      });

      markersList.push(marker);
    });

    mapInstanceRef.current = map;

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [assets, tileMode]);

  const handleResetBounds = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([22.45, 71.9], 7);
    }
  };

  const handleZoomIn = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.zoomIn();
    }
  };

  const handleZoomOut = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.zoomOut();
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', background: '#0a0f1d', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(59, 130, 246, 0.25)', boxShadow: '0 10px 35px rgba(0,0,0,0.6)' }}>
      {/* Top Map Control Bar */}
      <div style={{
        padding: '12px 18px',
        background: 'rgba(15, 23, 42, 0.95)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 12,
        zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 9, height: 9, borderRadius: '50%', background: '#38bdf8', boxShadow: '0 0 10px #38bdf8' }} />
          <div>
            <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.01em' }}>
              Real-time Gujarat GIS Asset Command Map
            </span>
            <span style={{ fontSize: '0.68rem', marginLeft: 8, padding: '2px 8px', borderRadius: 10, background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', fontWeight: 700, border: '1px solid rgba(56, 189, 248, 0.3)' }}>
              LIVE GIS · ZOOM & PAN ACTIVE
            </span>
          </div>
        </div>

        {/* Map Interactive Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Zoom In & Out Quick Buttons */}
          <div style={{ display: 'flex', background: 'rgba(255, 255, 255, 0.05)', borderRadius: 6, border: '1px solid rgba(255, 255, 255, 0.1)', overflow: 'hidden' }}>
            <button
              onClick={handleZoomIn}
              title="Zoom In"
              style={{ padding: '5px 11px', background: 'transparent', border: 'none', color: '#f8fafc', cursor: 'pointer', fontWeight: 800, fontSize: '0.9rem' }}
            >
              +
            </button>
            <button
              onClick={handleZoomOut}
              title="Zoom Out"
              style={{ padding: '5px 11px', background: 'transparent', border: 'none', borderLeft: '1px solid rgba(255, 255, 255, 0.1)', color: '#f8fafc', cursor: 'pointer', fontWeight: 800, fontSize: '0.9rem' }}
            >
              -
            </button>
          </div>

          {/* Reset Gujarat View */}
          <button
            onClick={handleResetBounds}
            style={{
              padding: '5px 10px',
              borderRadius: 6,
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#cbd5e1',
              fontSize: '0.74rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            ⟲ Reset State View
          </button>

          {/* Tile Layer Toggle */}
          <button
            onClick={() => setTileMode(tileMode === 'VOYAGER' ? 'DARK' : 'VOYAGER')}
            style={{
              padding: '5px 10px',
              borderRadius: 6,
              background: tileMode === 'DARK' ? 'rgba(59, 130, 246, 0.25)' : 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${tileMode === 'DARK' ? '#38bdf8' : 'rgba(255, 255, 255, 0.1)'}`,
              color: tileMode === 'DARK' ? '#38bdf8' : '#cbd5e1',
              fontSize: '0.74rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {tileMode === 'DARK' ? "🌙 Dark Satellite Grid" : "☀️ OpenStreetMap GIS"}
          </button>
        </div>
      </div>

      {/* Real Interactive Leaflet Container */}
      <div
        ref={mapContainerRef}
        style={{
          width: '100%',
          height: 520,
          background: '#070c18',
          zIndex: 1,
        }}
      />

      {/* Selected Asset Bottom Drawer */}
      {selectedAsset && (
        <div style={{
          padding: '12px 18px',
          background: 'rgba(15, 23, 42, 0.96)',
          borderTop: '1px solid rgba(56, 189, 248, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
          boxShadow: '0 -4px 20px rgba(0,0,0,0.5)',
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#38bdf8' }}>{selectedAsset.code}</span>
              <span className={`badge badge-${selectedAsset.condition_rating?.toLowerCase()}`}>
                {selectedAsset.condition_rating} ({selectedAsset.condition_score || '--'}/100)
              </span>
              <span className="badge badge-critical" style={{ background: selectedAsset.risk_level === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)' }}>
                Risk: {selectedAsset.risk_level}
              </span>
            </div>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#f8fafc' }}>{selectedAsset.name}</div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
              Action Due: <span style={{ color: '#fbbf24', fontWeight: 600 }}>{selectedAsset.next_action || 'Routine QC Audit'}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setSelectedAsset(null)}
            >
              Dismiss
            </button>
            <button
              className="btn btn-primary btn-sm"
              onClick={() => onSelectAsset && onSelectAsset(selectedAsset.id)}
            >
              Open Digital Asset Passport →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};


