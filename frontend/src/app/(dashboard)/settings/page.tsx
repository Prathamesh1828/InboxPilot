"use client";

import { useState } from "react";
import { User, Bell, Sliders, Shield, Palette, Save, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
    }, 800);
  };

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "automation", label: "Automation", icon: Sliders },
    { id: "security", label: "Security", icon: Shield },
    { id: "appearance", label: "Appearance", icon: Palette },
  ];

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
          {activeTab === "profile" && (
            <div className="space-y-6 max-w-xl">
              <div>
                <h3 className="text-lg font-medium text-foreground mb-4">Profile Information</h3>
                <p className="text-sm text-muted-foreground mb-6">Update your account&apos;s profile information and email address.</p>
              </div>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" defaultValue="Jane Doe" className="bg-background" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" defaultValue="jane.doe@example.com" className="bg-background" />
                </div>
              </div>
              <Button onClick={handleSave} disabled={isSaving} className="bg-primary text-primary-foreground hover:bg-primary/90 mt-4">
                {isSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                Save Changes
              </Button>
            </div>
          )}

          {activeTab === "automation" && (
            <div className="space-y-6 max-w-xl">
              <div>
                <h3 className="text-lg font-medium text-foreground mb-4">Automation Preferences</h3>
                <p className="text-sm text-muted-foreground mb-6">Configure how InboxPilot handles your emails autonomously.</p>
              </div>
              
              <div className="space-y-4">
                <Label>Automation Level</Label>
                <div className="grid gap-4">
                  <div className="border border-border p-4 rounded-xl cursor-pointer hover:border-primary transition-colors bg-secondary/30 relative">
                    <div className="absolute top-4 right-4 w-4 h-4 rounded-full border-4 border-primary bg-background" />
                    <h4 className="font-semibold text-foreground">Cautious (Recommended)</h4>
                    <p className="text-sm text-muted-foreground mt-1">Only automate trivial tasks. Ask for approval for everything else.</p>
                  </div>
                  <div className="border border-border p-4 rounded-xl cursor-pointer hover:border-primary transition-colors relative">
                    <div className="absolute top-4 right-4 w-4 h-4 rounded-full border border-muted-foreground/30 bg-background" />
                    <h4 className="font-semibold text-foreground">Balanced</h4>
                    <p className="text-sm text-muted-foreground mt-1">Automate obvious tasks. Ask for approval on medium-risk items.</p>
                  </div>
                </div>
              </div>
              
              <Button onClick={handleSave} disabled={isSaving} className="bg-primary text-primary-foreground hover:bg-primary/90 mt-4">
                {isSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
                Save Preferences
              </Button>
            </div>
          )}

          {activeTab === "appearance" && (
            <div className="space-y-6 max-w-xl">
              <div>
                <h3 className="text-lg font-medium text-foreground mb-4">Appearance</h3>
                <p className="text-sm text-muted-foreground mb-6">Customize the look and feel of your dashboard.</p>
              </div>
              
              <div className="space-y-4">
                <Label>Theme</Label>
                <div className="flex flex-wrap gap-4">
                  <button className="flex flex-col items-center gap-2" onClick={() => document.documentElement.classList.remove("dark")}>
                    <div className="w-24 h-16 rounded-lg border-2 border-primary bg-[#FFF8DF] overflow-hidden flex flex-col">
                      <div className="h-4 bg-[#FC6C26] w-full" />
                      <div className="flex-1 p-2">
                        <div className="w-full h-2 bg-[#5B2361]/20 rounded mb-1" />
                        <div className="w-2/3 h-2 bg-[#5B2361]/20 rounded" />
                      </div>
                    </div>
                    <span className="text-sm font-medium text-foreground">Light</span>
                  </button>
                  <button className="flex flex-col items-center gap-2" onClick={() => document.documentElement.classList.add("dark")}>
                    <div className="w-24 h-16 rounded-lg border-2 border-border bg-[#5B2361] overflow-hidden flex flex-col">
                      <div className="h-4 bg-[#FC6C26] w-full" />
                      <div className="flex-1 p-2">
                        <div className="w-full h-2 bg-[#FFF8DF]/20 rounded mb-1" />
                        <div className="w-2/3 h-2 bg-[#FFF8DF]/20 rounded" />
                      </div>
                    </div>
                    <span className="text-sm font-medium text-foreground">Dark</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {(activeTab === "notifications" || activeTab === "security") && (
            <div className="flex items-center justify-center h-full min-h-[300px]">
              <p className="text-muted-foreground">This section is under construction.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
