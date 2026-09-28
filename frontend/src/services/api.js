/**
 * Centralized API Client for Gujarat R&B Lifecycle Platform.
 */

const API_BASE = "http://127.0.0.1:8000/api";

function getAuthHeaders() {
  const token = localStorage.getItem("rnb_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      const message = errorData.detail || `Request failed with status ${res.status}`;
      throw new Error(typeof message === "string" ? message : JSON.stringify(message));
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Auth
  async login(username, password) {
    const res = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    if (res.access_token) {
      localStorage.setItem("rnb_token", res.access_token);
      localStorage.setItem("rnb_user", JSON.stringify(res.user));
    }
    return res;
  },

  async register(userData) {
    return await request("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  async getMe() {
    return await request("/auth/me");
  },

  logout() {
    localStorage.removeItem("rnb_token");
    localStorage.removeItem("rnb_user");
  },

  // Dashboard & GIS
  async getDashboardStats() {
    return await request("/dashboard/stats");
  },

  async getGeoAssets() {
    return await request("/dashboard/geo-assets");
  },

  // Infrastructure & Classifications
  async getInfrastructureClasses() {
    return await request("/infrastructure/classes");
  },

  async getAssetTypes(classId = null) {
    const query = classId ? `?infrastructure_class_id=${classId}` : "";
    return await request(`/infrastructure/asset-types${query}`);
  },

  // Projects
  async listProjects() {
    return await request("/projects");
  },

  async getProject(id) {
    return await request(`/projects/${id}`);
  },

  async createProject(data) {
    return await request("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async handoverProjectToAsset(projectId, data) {
    return await request(`/projects/${projectId}/create-asset`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async reviewProject(projectId, data) {
    return await request(`/projects/${projectId}/review`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async advanceProject(projectId, data = {}) {
    return await request(`/projects/${projectId}/advance`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Assets & Asset Passport
  async listAssets(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.append(k, v);
    });
    return await request(`/assets?${params.toString()}`);
  },

  async getAsset(id) {
    return await request(`/assets/${id}`);
  },

  async createAsset(data) {
    return await request("/assets", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateAsset(id, data) {
    return await request(`/assets/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  async getAssetLifecycle(id) {
    return await request(`/assets/${id}/lifecycle`);
  },

  async transitionAsset(id, data) {
    return await request(`/assets/${id}/lifecycle/transition`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getAssetTimeline(id) {
    return await request(`/assets/${id}/timeline`);
  },

  async getAssetComponents(id) {
    return await request(`/assets/${id}/components`);
  },

  async createAssetComponent(id, data) {
    return await request(`/assets/${id}/components`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getAssetDocuments(id) {
    return await request(`/assets/${id}/documents`);
  },

  async getAssetCosts(id) {
    return await request(`/assets/${id}/costs`);
  },

  // Operations: Inspections
  async listInspections(assetId = null) {
    const query = assetId ? `/assets/${assetId}/inspections` : "/inspections";
    return await request(query);
  },

  async createInspection(assetId, data) {
    return await request(`/assets/${assetId}/inspections`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Operations: Condition Assessments
  async listConditions(assetId) {
    return await request(`/assets/${assetId}/conditions`);
  },

  async createCondition(assetId, data) {
    return await request(`/assets/${assetId}/conditions`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Operations: Maintenance
  async listMaintenance(assetId = null) {
    const query = assetId ? `/assets/${assetId}/maintenance` : "/maintenance";
    return await request(query);
  },

  async createMaintenance(assetId, data) {
    return await request(`/assets/${assetId}/maintenance`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateMaintenance(id, data) {
    return await request(`/maintenance/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  // Operations: Issues
  async listIssues(assetId = null) {
    const query = assetId ? `/assets/${assetId}/issues` : "/issues";
    return await request(query);
  },

  async createIssue(assetId, data) {
    return await request(`/assets/${assetId}/issues`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateIssue(id, data) {
    return await request(`/issues/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  // Operations: Risk Assessment Engine
  async assessRisk(assetId, data) {
    return await request(`/assets/${assetId}/risk/assess`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getRiskHistory(assetId) {
    return await request(`/assets/${assetId}/risk/history`);
  },

  // Seed
  async reseedDatabase() {
    return await request("/seed", { method: "POST" });
  },
};
