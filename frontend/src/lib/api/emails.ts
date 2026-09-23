import { apiClient } from "./client";
import { EmailData } from "@/components/inbox/EmailRow";

export interface DashboardStats {
  emails_processed: number;
  pending_approvals: number;
  actions_executed: number;
  automation_rate: number;
  system_status: {
    gmail_integration: string;
    google_calendar: string;
    telegram: string;
  };
  recent_activity: unknown[];
}

export interface PaginatedEmailResponse {
  items: EmailData[];
  total: number;
  page: number;
  size: number;
}

export interface EmailDetailData extends EmailData {
  received_at?: string;
  body?: string;
  classification_confidence?: number | null;
  classification_reasoning?: string;
  action_plan?: {
    action: string;
    parameters: Record<string, unknown>;
    risk_level?: string;
    requires_approval?: boolean;
  };
  safety_result?: {
    action: string;
    risk_level: string;
    requires_approval: boolean;
  };
  execution_result?: Record<string, unknown>;
  error_message?: string;
  approval_id?: number;
  approval_status?: string;
}

export interface EmailQueryParams {
  search?: string;
  category?: string;
  status?: string;
  confidence_min?: number;
  confidence_max?: number;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  limit?: number;
}

export const emailsApi = {
  getMany: (params: EmailQueryParams = {}) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        searchParams.append(key, String(value));
      }
    });
    const qs = searchParams.toString();
    return apiClient.get<PaginatedEmailResponse>(`/emails${qs ? `?${qs}` : ""}`);
  },
  getOne: (id: string) => 
    apiClient.get<EmailDetailData>(`/emails/${id}`),
    
  process: (id: string) => 
    apiClient.post<{ status: string }>(`/emails/${id}/process`, {}),
    
  getAudit: (id: string) => 
    apiClient.get<Record<string, unknown>[]>(`/emails/${id}/audit`),
};

export const auditApi = {
  getGlobalAudit: (skip = 0, limit = 50) =>
    apiClient.get<Record<string, unknown>[]>(`/audit?skip=${skip}&limit=${limit}`),
};

export const dashboardApi = {
  getStats: () => apiClient.get<DashboardStats>('/dashboard/stats'),
};

export const approvalsApi = {
  getPending: () => apiClient.get<Record<string, unknown>[]>('/approvals'),
  approve: (id: string | number) => apiClient.post<Record<string, unknown>>(`/approvals/${id}/approve`, {}),
  reject: (id: string | number) => apiClient.post<Record<string, unknown>>(`/approvals/${id}/reject`, {}),
};
