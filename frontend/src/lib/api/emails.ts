import { apiClient } from "./client";
import { EmailData } from "@/components/inbox/EmailRow";

export const emailsApi = {
  getMany: (skip = 0, limit = 50) => 
    apiClient.get<EmailData[]>(`/emails?skip=${skip}&limit=${limit}`),
    
  getOne: (id: string) => 
    apiClient.get<EmailData>(`/emails/${id}`),
    
  process: (id: string) => 
    apiClient.post<{ status: string }>(`/emails/${id}/process`, {}),
    
  getAudit: (id: string) => 
    apiClient.get<any[]>(`/emails/${id}/audit`),
};

export const auditApi = {
  getGlobalAudit: (skip = 0, limit = 50) =>
    apiClient.get<any[]>(`/audit?skip=${skip}&limit=${limit}`),
};

export const dashboardApi = {
  getStats: () => apiClient.get<any>('/dashboard/stats'),
};

export const approvalsApi = {
  getPending: () => apiClient.get<any[]>('/approvals'),
  approve: (id: string | number) => apiClient.post<any>(`/approvals/${id}/approve`, {}),
  reject: (id: string | number) => apiClient.post<any>(`/approvals/${id}/reject`, {}),
};
