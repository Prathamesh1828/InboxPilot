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
    apiClient.get<unknown[]>(`/emails/${id}/audit`),
};
