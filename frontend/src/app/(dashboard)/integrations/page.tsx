"use client";

import { useState, useEffect } from "react";
import { Mail, Calendar, Smartphone, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { integrationsApi, IntegrationsResponse, IntegrationStatus } from "@/lib/api/integrations";
import { API_BASE_URL } from "@/lib/api/client";
import { toast } from "sonner";

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<IntegrationsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const [isConnectingGmail, setIsConnectingGmail] = useState(false);
  const [isConnectingTelegram, setIsConnectingTelegram] = useState(false);

  const fetchIntegrations = async () => {
    try {
      const data = await integrationsApi.getStatus();
      setIntegrations(data);
    } catch (error) {
      toast.error("Failed to load integrations status.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (integrations?.telegram?.status === "CONNECTING") {
      interval = setInterval(() => {
        fetchIntegrations();
      }, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [integrations?.telegram?.status]);

  const handleConnectGmail = () => {
    setIsConnectingGmail(true);
    // Redirect to the backend OAuth initialization endpoint with intent=connect
    window.location.href = `${API_BASE_URL}/auth/gmail/login?intent=connect`;
    
    // Reset loading state after a few seconds in case the user cancels navigation
    // or returns to the page via back button (bfcache)
    setTimeout(() => {
      setIsConnectingGmail(false);
    }, 5000);
  };

  const handleDisconnectGmail = async () => {
    if (!window.confirm("Are you sure you want to disconnect Gmail? This will also disconnect Google Calendar.")) return;
    try {
      await integrationsApi.disconnectGmail();
      toast.success("Successfully disconnected Gmail and Calendar.");
      fetchIntegrations();
    } catch (error: any) {
      toast.error(error?.message || "Failed to disconnect Gmail.");
    }
  };

  const handleConnectTelegram = async () => {
    setIsConnectingTelegram(true);
    try {
      const response = await integrationsApi.connectTelegram();
      // Open the Telegram deep link in a new tab
      window.open(response.link, "_blank");
      toast.success("Telegram opened! Press 'Start' in the bot to connect.");
      // Refresh status after a delay, as they might take a moment to click Start
      setTimeout(fetchIntegrations, 5000);
      // Change status to connecting locally
      if (integrations) {
        setIntegrations({
          ...integrations,
          telegram: { ...integrations.telegram, status: "CONNECTING" }
        });
      }
    } catch (error: any) {
      toast.error(error?.message || "Failed to generate Telegram link.");
    } finally {
      setIsConnectingTelegram(false);
    }
  };

  const handleDisconnectTelegram = async () => {
    if (!window.confirm("Are you sure you want to disconnect Telegram notifications?")) return;
    try {
      await integrationsApi.disconnectTelegram();
      toast.success("Successfully disconnected Telegram.");
      fetchIntegrations();
    } catch (error: any) {
      toast.error(error?.message || "Failed to disconnect Telegram.");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 pb-20 animate-in fade-in duration-500">
        <div>
          <Skeleton className="h-9 w-48 mb-2" />
          <Skeleton className="h-5 w-96" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-[280px] w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  const renderStatusBadge = (status: IntegrationStatus["status"]) => {
    switch (status) {
      case "CONNECTED":
        return (
          <div className="flex items-center gap-1.5 text-sm font-medium text-green-600 bg-green-500/10 px-2.5 py-1 rounded-full">
            <CheckCircle2 className="w-4 h-4" /> Connected
          </div>
        );
      case "CONNECTING":
        return (
          <div className="flex items-center gap-1.5 text-sm font-medium text-amber-600 bg-amber-500/10 px-2.5 py-1 rounded-full">
            <Loader2 className="w-4 h-4 animate-spin" /> Pending
          </div>
        );
      case "ERROR":
        return (
          <div className="flex items-center gap-1.5 text-sm font-medium text-destructive bg-destructive/10 px-2.5 py-1 rounded-full">
            <XCircle className="w-4 h-4" /> Error
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground bg-secondary px-2.5 py-1 rounded-full">
            <XCircle className="w-4 h-4" /> Not Connected
          </div>
        );
    }
  };

  return (
    <div className="space-y-6 pb-20">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Integrations</h1>
        <p className="text-muted-foreground mt-1">Manage connected services and notification channels.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        
        {/* Gmail Integration */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col h-full">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center text-red-500">
              <Mail className="w-6 h-6" />
            </div>
            {renderStatusBadge(integrations?.gmail.status || "NOT_CONNECTED")}
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">Gmail</h3>
          <p className="text-sm text-muted-foreground mb-6 flex-1">
            Allow InboxPilot to securely read incoming emails and perform actions on your behalf.
          </p>
          <div className="space-y-4 pt-4 border-t border-border">
            <div className="text-sm min-h-[20px]">
              {integrations?.gmail.status === "CONNECTED" && (
                <>
                  <span className="text-muted-foreground">Account:</span>{" "}
                  <span className="font-medium text-foreground">{integrations.gmail.email}</span>
                </>
              )}
            </div>
            <div className="flex gap-2">
              {integrations?.gmail.status === "CONNECTED" ? (
                <>
                  <Button onClick={handleConnectGmail} disabled={isConnectingGmail} variant="outline" className="flex-1 text-foreground border-border hover:bg-secondary">
                    Reconnect
                  </Button>
                  <Button onClick={handleDisconnectGmail} variant="outline" className="flex-1 text-destructive border-border hover:bg-destructive/10">
                    Disconnect
                  </Button>
                </>
              ) : (
                <Button onClick={handleConnectGmail} disabled={isConnectingGmail} className="w-full bg-red-600 text-white hover:bg-red-700">
                  {isConnectingGmail && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                  Connect Gmail
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Google Calendar Integration */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col h-full opacity-95">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-500">
              <Calendar className="w-6 h-6" />
            </div>
            {renderStatusBadge(integrations?.calendar.status || "NOT_CONNECTED")}
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">Google Calendar</h3>
          <p className="text-sm text-muted-foreground mb-6 flex-1">
            Allow InboxPilot to automatically draft and schedule meetings. (Bundled with Gmail connection).
          </p>
          <div className="space-y-4 pt-4 border-t border-border">
            <div className="text-sm min-h-[20px]">
              {integrations?.calendar.status === "CONNECTED" && (
                <>
                  <span className="text-muted-foreground">Account:</span>{" "}
                  <span className="font-medium text-foreground">{integrations.calendar.email}</span>
                </>
              )}
            </div>
            <div className="flex gap-2">
              {integrations?.calendar.status === "CONNECTED" ? (
                <Button onClick={handleDisconnectGmail} variant="outline" className="w-full text-destructive border-border hover:bg-destructive/10">
                  Disconnect
                </Button>
              ) : (
                <Button onClick={handleConnectGmail} disabled={isConnectingGmail} variant="outline" className="w-full">
                  Connect via Gmail
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Telegram Integration */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col h-full">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-[#229ED9]/10 rounded-xl flex items-center justify-center text-[#229ED9]">
              <Smartphone className="w-6 h-6" />
            </div>
            {renderStatusBadge(integrations?.telegram.status || "NOT_CONNECTED")}
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">Telegram Notifications</h3>
          <p className="text-sm text-muted-foreground mb-6 flex-1">
            Receive instant push notifications and approve or reject actions directly from Telegram.
          </p>
          
          {!integrations?.telegram_configured && (
            <div className="text-xs text-amber-600 bg-amber-500/10 p-2 rounded mb-4">
              Telegram is not configured on the backend (Missing bot token).
            </div>
          )}

          <div className="space-y-4 pt-4 border-t border-border mt-auto">
            <div className="text-sm min-h-[20px]">
              {integrations?.telegram.status === "CONNECTED" && (
                <>
                  <span className="text-muted-foreground">Account:</span>{" "}
                  <span className="font-medium text-foreground">{integrations.telegram.account}</span>
                </>
              )}
            </div>
            <div className="flex gap-2">
              {integrations?.telegram.status === "CONNECTED" ? (
                <>
                  <Button onClick={handleConnectTelegram} disabled={isConnectingTelegram} variant="outline" className="flex-1 text-foreground border-border hover:bg-secondary">
                    Reconnect
                  </Button>
                  <Button onClick={handleDisconnectTelegram} variant="outline" className="flex-1 text-destructive border-border hover:bg-destructive/10">
                    Disconnect
                  </Button>
                </>
              ) : integrations?.telegram.status === "CONNECTING" ? (
                <>
                  <Button 
                    onClick={handleConnectTelegram} 
                    disabled={isConnectingTelegram} 
                    variant="outline"
                    className="flex-1 text-foreground border-border hover:bg-secondary"
                  >
                    {isConnectingTelegram && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                    Retry
                  </Button>
                  <Button onClick={handleDisconnectTelegram} variant="outline" className="flex-1 text-destructive border-border hover:bg-destructive/10">
                    Cancel
                  </Button>
                </>
              ) : (
                <Button 
                  onClick={handleConnectTelegram} 
                  disabled={isConnectingTelegram || !integrations?.telegram_configured} 
                  className="w-full bg-[#229ED9] text-white hover:bg-[#229ED9]/90 disabled:opacity-50"
                >
                  {isConnectingTelegram && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                  Connect Telegram
                </Button>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
