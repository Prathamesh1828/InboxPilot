"use client";

import { useState } from "react";
import { Mail, Calendar, Smartphone, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function IntegrationsPage() {
  const [isConnectingGmail, setIsConnectingGmail] = useState(false);
  
  const handleConnectGmail = () => {
    setIsConnectingGmail(true);
    setTimeout(() => {
      setIsConnectingGmail(false);
      // In reality, this would redirect to OAuth
    }, 1000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Integrations</h1>
        <p className="text-muted-foreground mt-1">Manage connected services and API keys.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Gmail Integration */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col h-full">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-red-500/10 rounded-xl flex items-center justify-center text-red-500">
              <Mail className="w-6 h-6" />
            </div>
            <div className="flex items-center gap-1.5 text-sm font-medium text-green-600 bg-green-500/10 px-2.5 py-1 rounded-full">
              <CheckCircle2 className="w-4 h-4" /> Connected
            </div>
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">Gmail</h3>
          <p className="text-sm text-muted-foreground mb-6 flex-1">
            Allow InboxPilot to securely read incoming emails and perform actions on your behalf.
          </p>
          <div className="space-y-4 pt-4 border-t border-border">
            <div className="text-sm">
              <span className="text-muted-foreground">Account:</span>{" "}
              <span className="font-medium text-foreground">jane.doe@example.com</span>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" className="w-full text-foreground border-border hover:bg-secondary">
                Reconnect
              </Button>
              <Button variant="outline" className="w-full text-destructive border-border hover:bg-destructive/10">
                Disconnect
              </Button>
            </div>
          </div>
        </div>

        {/* Google Calendar Integration */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col h-full">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center text-blue-500">
              <Calendar className="w-6 h-6" />
            </div>
            <div className="flex items-center gap-1.5 text-sm font-medium text-green-600 bg-green-500/10 px-2.5 py-1 rounded-full">
              <CheckCircle2 className="w-4 h-4" /> Connected
            </div>
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">Google Calendar</h3>
          <p className="text-sm text-muted-foreground mb-6 flex-1">
            Allow InboxPilot to automatically draft and schedule meetings based on email context.
          </p>
          <div className="space-y-4 pt-4 border-t border-border">
            <div className="text-sm">
              <span className="text-muted-foreground">Account:</span>{" "}
              <span className="font-medium text-foreground">jane.doe@example.com</span>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" className="w-full text-foreground border-border hover:bg-secondary">
                Reconnect
              </Button>
              <Button variant="outline" className="w-full text-destructive border-border hover:bg-destructive/10">
                Disconnect
              </Button>
            </div>
          </div>
        </div>

        {/* Telegram Integration */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col h-full relative overflow-hidden">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 bg-[#229ED9]/10 rounded-xl flex items-center justify-center text-[#229ED9]">
              <Smartphone className="w-6 h-6" />
            </div>
            <div className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground bg-secondary px-2.5 py-1 rounded-full">
              <XCircle className="w-4 h-4" /> Not Connected
            </div>
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">Telegram Notifications</h3>
          <p className="text-sm text-muted-foreground mb-6 flex-1">
            Receive instant push notifications and approve or reject actions directly from Telegram.
          </p>
          <div className="space-y-4 pt-4 border-t border-border">
            <div className="text-sm opacity-0">
              <span className="text-muted-foreground">Account:</span>{" "}
              <span className="font-medium text-foreground">-</span>
            </div>
            <Button onClick={handleConnectGmail} disabled={isConnectingGmail} className="w-full bg-[#229ED9] text-white hover:bg-[#229ED9]/90">
              {isConnectingGmail ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              Connect Telegram
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
