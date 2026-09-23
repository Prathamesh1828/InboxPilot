import { apiClient } from "./client";

export interface IntegrationStatus {
  status: "CONNECTED" | "NOT_CONNECTED" | "CONNECTING" | "ERROR";
  email?: string | null;
  account?: string | null;
}

export interface IntegrationsResponse {
  gmail: IntegrationStatus;
  calendar: IntegrationStatus;
  telegram: IntegrationStatus;
  telegram_configured: boolean;
}

export const integrationsApi = {
  getStatus: () => apiClient.get<IntegrationsResponse>("/integrations"),
  disconnectGmail: () => apiClient.post<{ status: string }>("/integrations/gmail/disconnect", {}),
  disconnectTelegram: () => apiClient.post<{ status: string }>("/integrations/telegram/disconnect", {}),
  connectTelegram: () => apiClient.get<{ link: string }>("/integrations/telegram/connect"),
};
