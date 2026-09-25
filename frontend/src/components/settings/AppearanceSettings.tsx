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
    
    // Apply theme immediately for preview
    if (key === "theme") {
      if (value === "DARK") {
        document.documentElement.classList.add("dark");
      } else if (value === "LIGHT") {
        document.documentElement.classList.remove("dark");
      } else {
        if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
          document.documentElement.classList.add("dark");
        } else {
          document.documentElement.classList.remove("dark");
        }
      }
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await settingsApi.updateSettings({
        theme: settings.theme,
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
        
        <div className="space-y-4">
          <Label>Theme</Label>
          <div className="flex flex-wrap gap-4">
            <button 
              className="flex flex-col items-center gap-2" 
              onClick={() => handleChange("theme", "LIGHT")}
            >
              <div className={`w-32 h-20 rounded-lg border-2 overflow-hidden flex flex-col transition-all ${settings.theme === "LIGHT" ? "border-primary ring-2 ring-primary/20" : "border-border hover:border-primary/50 bg-[#FFF8DF]"}`}>
                <div className="h-4 bg-[#FC6C26] w-full" />
                <div className="flex-1 p-2 bg-[#FFF8DF]">
                  <div className="w-full h-2 bg-[#5B2361]/20 rounded mb-1.5" />
                  <div className="w-2/3 h-2 bg-[#5B2361]/20 rounded" />
                </div>
              </div>
              <span className={`text-sm font-medium ${settings.theme === "LIGHT" ? "text-primary" : "text-foreground"}`}>Light</span>
            </button>
            <button 
              className="flex flex-col items-center gap-2" 
              onClick={() => handleChange("theme", "DARK")}
            >
              <div className={`w-32 h-20 rounded-lg border-2 overflow-hidden flex flex-col transition-all ${settings.theme === "DARK" ? "border-primary ring-2 ring-primary/20" : "border-border hover:border-primary/50 bg-[#5B2361]"}`}>
                <div className="h-4 bg-[#FC6C26] w-full" />
                <div className="flex-1 p-2 bg-[#5B2361]">
                  <div className="w-full h-2 bg-[#FFF8DF]/20 rounded mb-1.5" />
                  <div className="w-2/3 h-2 bg-[#FFF8DF]/20 rounded" />
                </div>
              </div>
              <span className={`text-sm font-medium ${settings.theme === "DARK" ? "text-primary" : "text-foreground"}`}>Dark</span>
            </button>
            <button 
              className="flex flex-col items-center gap-2" 
              onClick={() => handleChange("theme", "SYSTEM")}
            >
              <div className={`w-32 h-20 rounded-lg border-2 overflow-hidden flex flex-col transition-all ${settings.theme === "SYSTEM" ? "border-primary ring-2 ring-primary/20" : "border-border hover:border-primary/50 bg-gradient-to-br from-[#FFF8DF] to-[#5B2361]"}`}>
                <div className="h-4 bg-[#FC6C26] w-full" />
                <div className="flex-1 p-2 flex bg-gradient-to-br from-[#FFF8DF] to-[#5B2361]">
                </div>
              </div>
              <span className={`text-sm font-medium ${settings.theme === "SYSTEM" ? "text-primary" : "text-foreground"}`}>System</span>
            </button>
          </div>
        </div>
      </div>

      <div className="pt-8 border-t border-border">
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
