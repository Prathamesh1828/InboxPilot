import { useState } from "react";
import { Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { settingsApi, UserSettings } from "@/lib/api/settings";
import { toast } from "sonner";

export function AutomationSettings({ initialSettings }: { initialSettings: UserSettings }) {
  const [settings, setSettings] = useState<UserSettings>(initialSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (key: keyof UserSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await settingsApi.updateSettings({
        automation_mode: settings.automation_mode,
        confidence_threshold: settings.confidence_threshold,
        pause_all_automations: settings.pause_all_automations,
        approval_required_sending: settings.approval_required_sending,
        approval_required_forwarding: settings.approval_required_forwarding,
        approval_required_deleting: settings.approval_required_deleting,
        approval_required_calendar: settings.approval_required_calendar,
        approval_required_other: settings.approval_required_other,
      });
      toast.success("Automation preferences saved");
      setHasChanges(false);
    } catch (error: any) {
      toast.error(error.message || "Failed to save preferences");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-2xl animate-in fade-in duration-300">
      
      <div className="flex items-center justify-between p-4 bg-destructive/10 border border-destructive/20 rounded-xl">
        <div className="space-y-0.5">
          <Label className="text-base font-medium text-destructive">Pause All Automations</Label>
          <p className="text-sm text-destructive/80">Temporarily stop InboxPilot from processing any emails.</p>
        </div>
        <Switch 
          checked={settings.pause_all_automations} 
          onCheckedChange={(v) => handleChange("pause_all_automations", v)} 
          className="data-[state=checked]:bg-destructive"
        />
      </div>

      <div className={settings.pause_all_automations ? "opacity-50 pointer-events-none" : ""}>
        <div>
          <h3 className="text-lg font-medium text-foreground mb-4">Automation Level</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {[
              { id: "MANUAL", title: "Manual", desc: "Always ask before performing any action." },
              { id: "ASSISTED", title: "Assisted", desc: "Automate trivial tasks, ask for important ones." },
              { id: "AUTOMATIC", title: "Automatic", desc: "Autonomously perform most actions." }
            ].map((mode) => (
              <div 
                key={mode.id}
                onClick={() => handleChange("automation_mode", mode.id)}
                className={`border p-4 rounded-xl cursor-pointer transition-colors relative ${
                  settings.automation_mode === mode.id 
                    ? "border-primary bg-primary/5" 
                    : "border-border hover:border-primary/50 bg-card"
                }`}
              >
                <div className={`absolute top-4 right-4 w-4 h-4 rounded-full border flex items-center justify-center ${
                  settings.automation_mode === mode.id ? "border-primary bg-primary" : "border-muted-foreground/30 bg-background"
                }`}>
                  {settings.automation_mode === mode.id && <div className="w-1.5 h-1.5 bg-background rounded-full" />}
                </div>
                <h4 className="font-semibold text-foreground">{mode.title}</h4>
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{mode.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-8 mt-8 border-t border-border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-foreground">Confidence Threshold</h3>
            <span className="text-lg font-bold text-primary">{settings.confidence_threshold}%</span>
          </div>
          <p className="text-sm text-muted-foreground mb-6">
            The minimum AI confidence required before performing actions without explicit approval.
          </p>
          <Slider
            value={[settings.confidence_threshold]}
            min={50}
            max={100}
            step={1}
            onValueChange={(val) => handleChange("confidence_threshold", Array.isArray(val) ? val[0] : val)}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-2">
            <span>Aggressive (50%)</span>
            <span>Conservative (100%)</span>
          </div>
        </div>

        <div className="pt-8 mt-8 border-t border-border">
          <h3 className="text-lg font-medium text-foreground mb-1">Require Approvals</h3>
          <p className="text-sm text-muted-foreground mb-6">Even in automatic mode, always require manual approval for these actions:</p>
          
          <div className="space-y-6">
            {[
              { key: "approval_required_sending", label: "Sending Emails", desc: "Require approval before sending any new emails or replies." },
              { key: "approval_required_forwarding", label: "Forwarding Emails", desc: "Require approval before forwarding emails to others." },
              { key: "approval_required_deleting", label: "Deleting/Archiving", desc: "Require approval before permanently removing emails." },
              { key: "approval_required_calendar", label: "Calendar Changes", desc: "Require approval before scheduling or modifying events." },
              { key: "approval_required_other", label: "Other Actions", desc: "Require approval for all other miscellaneous actions." },
            ].map(({ key, label, desc }) => (
              <div key={key} className="flex items-center justify-between gap-4">
                <div className="space-y-0.5">
                  <Label className="text-base font-medium">{label}</Label>
                  <p className="text-sm text-muted-foreground">{desc}</p>
                </div>
                <Switch 
                  checked={settings[key as keyof UserSettings] as boolean} 
                  onCheckedChange={(v) => handleChange(key as keyof UserSettings, v)} 
                />
              </div>
            ))}
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
