import { useState, useEffect } from "react";
import { Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { settingsApi, UserSettings } from "@/lib/api/settings";
import { toast } from "sonner";

export function AppearanceSettings({ initialSettings }: { initialSettings: UserSettings }) {
  const [settings, setSettings] = useState<UserSettings>(initialSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  
  const handleChange = (key: keyof UserSettings, value: string) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await settingsApi.updateSettings({
        density: settings.density,
      });
      toast.success("Appearance preferences saved");
      setHasChanges(false);
    } catch (error: any) {
      toast.error(error.message || "Failed to save preferences");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-10 max-w-xl animate-in fade-in duration-300">
      <div>
        <h3 className="text-lg font-medium text-foreground mb-4">Appearance</h3>
        <p className="text-sm text-muted-foreground mb-6">Customize the look and feel of your dashboard.</p>
      </div>

      <div className="pt-2">
        <div className="space-y-4">
          <Label>Display Density</Label>
          <div className="grid gap-4 md:grid-cols-2">
            <div 
              onClick={() => handleChange("density", "COMFORTABLE")}
              className={`border p-4 rounded-xl cursor-pointer transition-colors relative ${
                settings.density === "COMFORTABLE" 
                  ? "border-primary bg-primary/5" 
                  : "border-border hover:border-primary/50 bg-card"
              }`}
            >
              <div className={`absolute top-4 right-4 w-4 h-4 rounded-full border flex items-center justify-center ${
                settings.density === "COMFORTABLE" ? "border-primary bg-primary" : "border-muted-foreground/30 bg-background"
              }`}>
                {settings.density === "COMFORTABLE" && <div className="w-1.5 h-1.5 bg-background rounded-full" />}
              </div>
              <h4 className="font-semibold text-foreground">Comfortable</h4>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">More padding and spacing for a relaxed reading experience.</p>
            </div>
            <div 
              onClick={() => handleChange("density", "COMPACT")}
              className={`border p-4 rounded-xl cursor-pointer transition-colors relative ${
                settings.density === "COMPACT" 
                  ? "border-primary bg-primary/5" 
                  : "border-border hover:border-primary/50 bg-card"
              }`}
            >
              <div className={`absolute top-4 right-4 w-4 h-4 rounded-full border flex items-center justify-center ${
                settings.density === "COMPACT" ? "border-primary bg-primary" : "border-muted-foreground/30 bg-background"
              }`}>
                {settings.density === "COMPACT" && <div className="w-1.5 h-1.5 bg-background rounded-full" />}
              </div>
              <h4 className="font-semibold text-foreground">Compact</h4>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">Show more information on screen at once with tighter spacing.</p>
            </div>
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
