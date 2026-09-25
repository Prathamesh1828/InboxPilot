import { useState } from "react";
import { Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { settingsApi, UserSettings } from "@/lib/api/settings";
import { toast } from "sonner";
import Link from "next/link";

export function NotificationSettings({ 
  initialSettings,
  isTelegramConnected
}: { 
  initialSettings: UserSettings;
  isTelegramConnected: boolean;
}) {
  const [settings, setSettings] = useState<UserSettings>(initialSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (key: keyof UserSettings, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await settingsApi.updateSettings({
        notify_email_approvals: settings.notify_email_approvals,
        notify_email_completions: settings.notify_email_completions,
        notify_email_failures: settings.notify_email_failures,
        notify_email_alerts: settings.notify_email_alerts,
        notify_telegram_approvals: settings.notify_telegram_approvals,
        notify_telegram_completions: settings.notify_telegram_completions,
        notify_telegram_failures: settings.notify_telegram_failures,
      });
      toast.success("Notification preferences saved");
      setHasChanges(false);
    } catch (error: any) {
      toast.error(error.message || "Failed to save preferences");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-2xl animate-in fade-in duration-300">
      <div>
        <h3 className="text-lg font-medium text-foreground mb-1">Email Notifications</h3>
        <p className="text-sm text-muted-foreground mb-6">Choose what updates you want to receive via email.</p>
        
        <div className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div className="space-y-0.5">
              <Label className="text-base font-medium">Approval Requests</Label>
              <p className="text-sm text-muted-foreground">Receive an email when an action requires your approval.</p>
            </div>
            <Switch 
              checked={settings.notify_email_approvals} 
              onCheckedChange={(v) => handleChange("notify_email_approvals", v)} 
            />
          </div>
          
          <div className="flex items-center justify-between gap-4">
            <div className="space-y-0.5">
              <Label className="text-base font-medium">Workflow Completions</Label>
              <p className="text-sm text-muted-foreground">Receive an email when a workflow finishes successfully.</p>
            </div>
            <Switch 
              checked={settings.notify_email_completions} 
              onCheckedChange={(v) => handleChange("notify_email_completions", v)} 
            />
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="space-y-0.5">
              <Label className="text-base font-medium">Workflow Failures</Label>
              <p className="text-sm text-muted-foreground">Get notified immediately if an automation fails.</p>
            </div>
            <Switch 
              checked={settings.notify_email_failures} 
              onCheckedChange={(v) => handleChange("notify_email_failures", v)} 
            />
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="space-y-0.5">
              <Label className="text-base font-medium">System Alerts</Label>
              <p className="text-sm text-muted-foreground">Important security and account notifications.</p>
            </div>
            <Switch 
              checked={settings.notify_email_alerts} 
              onCheckedChange={(v) => handleChange("notify_email_alerts", v)} 
            />
          </div>
        </div>
      </div>

      <div className="pt-6 border-t border-border">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-1">Telegram Notifications</h3>
            <p className="text-sm text-muted-foreground">Get instant alerts directly in Telegram.</p>
          </div>
          {!isTelegramConnected && (
            <Link href="/integrations">
              <Button variant="outline" size="sm">Connect Telegram</Button>
            </Link>
          )}
        </div>
        
        <div className={`space-y-6 ${!isTelegramConnected ? "opacity-50 pointer-events-none grayscale" : ""}`}>
          <div className="flex items-center justify-between gap-4">
            <div className="space-y-0.5">
              <Label className="text-base font-medium">Approval Requests</Label>
              <p className="text-sm text-muted-foreground">Instant messages for pending approvals.</p>
            </div>
            <Switch 
              checked={settings.notify_telegram_approvals} 
              onCheckedChange={(v) => handleChange("notify_telegram_approvals", v)} 
            />
          </div>
          
          <div className="flex items-center justify-between gap-4">
            <div className="space-y-0.5">
              <Label className="text-base font-medium">Workflow Completions</Label>
              <p className="text-sm text-muted-foreground">Messages when workflows finish.</p>
            </div>
            <Switch 
              checked={settings.notify_telegram_completions} 
              onCheckedChange={(v) => handleChange("notify_telegram_completions", v)} 
            />
          </div>

          <div className="flex items-center justify-between gap-4">
            <div className="space-y-0.5">
              <Label className="text-base font-medium">Workflow Failures</Label>
              <p className="text-sm text-muted-foreground">Instant alerts for failed automations.</p>
            </div>
            <Switch 
              checked={settings.notify_telegram_failures} 
              onCheckedChange={(v) => handleChange("notify_telegram_failures", v)} 
            />
          </div>
        </div>
      </div>

      <Button 
        onClick={handleSave} 
        disabled={isSaving || !hasChanges} 
        className="bg-primary text-primary-foreground hover:bg-primary/90 mt-8"
      >
        {isSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
        Save Preferences
      </Button>
    </div>
  );
}
