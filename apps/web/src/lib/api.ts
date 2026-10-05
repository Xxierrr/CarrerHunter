import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach JWT token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor: handle 401 (expired token)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; name: string }) =>
    api.post("/api/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/api/auth/login", data),
  me: () => api.get("/api/auth/me"),
  refresh: (refreshToken: string) =>
    api.post("/api/auth/refresh", { refresh_token: refreshToken }),
};

// ─── Profile ─────────────────────────────────────────
export const profileApi = {
  get: () => api.get("/api/profile"),
  update: (data: any) => api.put("/api/profile", data),
  updateSkills: (skills: any[]) =>
    api.put("/api/profile/skills", { skills }),
  getExperiences: () => api.get("/api/profile/experiences"),
  createExperience: (data: any) => api.post("/api/profile/experiences", data),
  updateExperience: (id: string, data: any) =>
    api.put(`/api/profile/experiences/${id}`, data),
  deleteExperience: (id: string) =>
    api.delete(`/api/profile/experiences/${id}`),
  uploadResume: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/api/profile/resume/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ─── Internships ─────────────────────────────────────
export const internshipApi = {
  list: (params?: Record<string, any>) =>
    api.get("/api/internships", { params }),
  get: (id: string) => api.get(`/api/internships/${id}`),
  save: (id: string) => api.post(`/api/internships/${id}/save`),
  unsave: (id: string) => api.delete(`/api/internships/${id}/save`),
  getSaved: () => api.get("/api/internships/saved/list"),
  getRecommendations: (limit?: number) =>
    api.get("/api/internships/recommendations", { params: { limit } }),
};

// ─── Applications ────────────────────────────────────
export const applicationApi = {
  list: (status?: string) =>
    api.get("/api/applications", { params: status ? { status } : {} }),
  create: (data: { internship_id: string; status?: string; notes?: string }) =>
    api.post("/api/applications", data),
  update: (id: string, data: any) => api.patch(`/api/applications/${id}`, data),
  delete: (id: string) => api.delete(`/api/applications/${id}`),
  getEvents: (id: string) => api.get(`/api/applications/${id}/events`),
};

// ─── Notifications ───────────────────────────────────
export const notificationApi = {
  list: (params?: { unread_only?: boolean; page?: number }) =>
    api.get("/api/notifications", { params }),
  markRead: (id: string) => api.patch(`/api/notifications/${id}/read`),
  markAllRead: () => api.patch("/api/notifications/read-all"),
  getPreferences: () => api.get("/api/notifications/preferences"),
  updatePreferences: (data: any) =>
    api.put("/api/notifications/preferences", data),
};

// ─── AI ──────────────────────────────────────────────
export const aiApi = {
  analyzeJob: (data: { title: string; description: string }) =>
    api.post("/api/ai/analyze-job", data),
  getUsage: () => api.get("/api/ai/usage"),
};

// ─── Admin ───────────────────────────────────────────
export const adminApi = {
  getStats: () => api.get("/api/admin/stats"),
  getSources: () => api.get("/api/admin/sources"),
  getAiUsage: () => api.get("/api/admin/ai-usage"),
  getCrawlRuns: (limit?: number) =>
    api.get("/api/admin/crawl-runs", { params: { limit } }),
};

export default api;
