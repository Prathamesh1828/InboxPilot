import { apiClient } from "./client";

export interface UserSettings {
  user_id: string;
  
  notify_email_approvals: boolean;
  notify_email_completions: boolean;
  notify_email_failures: boolean;
  notify_email_alerts: boolean;
  
  notify_telegram_approvals: boolean;
  notify_telegram_completions: boolean;
  notify_telegram_failures: boolean;
  
  automation_mode: string;
  confidence_threshold: number;
  pause_all_automations: boolean;
  
  approval_required_sending: boolean;
  approval_required_forwarding: boolean;
  approval_required_deleting: boolean;
  approval_required_calendar: boolean;
  approval_required_other: boolean;
  
  theme: string;
  density: string;
}

export const settingsApi = {
  getSettings: () => 
    apiClient.get<UserSettings>("/settings"),
    
  updateSettings: (data: Partial<UserSettings>) =>
    apiClient.patch<UserSettings>("/settings", data),

  updateProfile: (data: { name: string }) =>
    apiClient.patch<{ message: string }>("/settings/profile", data),

  changePassword: (data: any) =>
    apiClient.post<{ message: string }>("/settings/change-password", data),
    
  logoutAll: () =>
    apiClient.post<{ message: string }>("/settings/logout-all", {}),
    
  deleteAccount: () =>
    apiClient.delete<{ message: string }>("/settings/account"),
};
