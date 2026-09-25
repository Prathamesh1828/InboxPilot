"use client";

import { useState, useEffect } from "react";
import { User, Bell, Sliders, Shield, Palette, Plug, Loader2 } from "lucide-react";
import { settingsApi, UserSettings } from "@/lib/api/settings";
import { integrationsApi, IntegrationsResponse } from "@/lib/api/integrations";
import { ProfileSettings } from "@/components/settings/ProfileSettings";
import { NotificationSettings } from "@/components/settings/NotificationSettings";
import { AutomationSettings } from "@/components/settings/AutomationSettings";
import { SecuritySettings } from "@/components/settings/SecuritySettings";
import { AppearanceSettings } from "@/components/settings/AppearanceSettings";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [integrations, setIntegrations] = useState<IntegrationsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [settingsData, integrationsData] = await Promise.all([
          settingsApi.getSettings(),
          integrationsApi.getStatus()
        ]);
        setSettings(settingsData);
        setIntegrations(integrationsData);
      } catch (error) {
        console.error("Failed to load settings data", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "automation", label: "Automation", icon: Sliders },
    { id: "security", label: "Security", icon: Shield },
    { id: "appearance", label: "Appearance", icon: Palette },
    { id: "integrations", label: "Integrations", icon: Plug },
  ];

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account settings and automation preferences.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        <aside className="w-full md:w-64 shrink-0">
          <nav className="flex md:flex-col gap-2 overflow-x-auto pb-4 md:pb-0">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id 
                    ? "bg-primary/10 text-primary" 
                    : "text-foreground/70 hover:bg-secondary hover:text-foreground"
                }`}
              >
                <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? "text-primary" : "text-muted-foreground"}`} />
                {tab.label}
              </button>
            ))}
          </nav>
        </aside>

        <div className="flex-1 bg-card border border-border rounded-xl shadow-sm p-6 lg:p-8 min-h-[400px]">
          {activeTab === "profile" && <ProfileSettings />}
          {activeTab === "notifications" && settings && (
            <NotificationSettings 
              initialSettings={settings} 
              isTelegramConnected={integrations?.telegram.status === "CONNECTED"} 
            />
          )}
          {activeTab === "automation" && settings && <AutomationSettings initialSettings={settings} />}
          {activeTab === "security" && <SecuritySettings />}
          {activeTab === "appearance" && settings && <AppearanceSettings initialSettings={settings} />}
          
          {activeTab === "integrations" && (
            <div className="space-y-6 max-w-xl animate-in fade-in duration-300">
              <div>
                <h3 className="text-lg font-medium text-foreground mb-4">Connected Services</h3>
                <p className="text-sm text-muted-foreground mb-6">Manage your external service connections on the Integrations page.</p>
              </div>
              <div className="space-y-4">
                <div className="p-4 bg-secondary/20 border border-border rounded-xl flex items-center justify-between">
                  <div>
                    <p className="font-medium">Gmail</p>
                    <p className="text-sm text-muted-foreground">{integrations?.gmail.email || "Not connected"}</p>
                  </div>
                  <div className={`text-sm font-medium px-3 py-1 rounded-full ${integrations?.gmail.status === 'CONNECTED' ? 'bg-success/10 text-success' : 'bg-muted-foreground/10 text-muted-foreground'}`}>
                    {integrations?.gmail.status}
                  </div>
                </div>
                <div className="p-4 bg-secondary/20 border border-border rounded-xl flex items-center justify-between">
                  <div>
                    <p className="font-medium">Telegram</p>
                    <p className="text-sm text-muted-foreground">{integrations?.telegram.status === "CONNECTED" ? "Active" : "Not connected"}</p>
                  </div>
                  <div className={`text-sm font-medium px-3 py-1 rounded-full ${integrations?.telegram.status === 'CONNECTED' ? 'bg-success/10 text-success' : 'bg-muted-foreground/10 text-muted-foreground'}`}>
                    {integrations?.telegram.status}
                  </div>
                </div>
              </div>
              <div className="pt-6">
                <Link href="/integrations">
                  <Button className="w-full sm:w-auto">Manage Integrations</Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
