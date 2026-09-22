import { apiClient } from "./client";
import { ApprovalData } from "@/components/approvals/ApprovalCard";

export const approvalsApi = {
  getMany: (skip = 0, limit = 50) => 
    apiClient.get<ApprovalData[]>(`/approvals?skip=${skip}&limit=${limit}`),
    
  getOne: (id: string) => 
    apiClient.get<ApprovalData>(`/approvals/${id}`),
    
  approve: (id: string) => 
    apiClient.post<{ status: string }>(`/approvals/${id}/approve`, {}),
    
  reject: (id: string) => 
    apiClient.post<{ status: string }>(`/approvals/${id}/reject`, {}),
};
