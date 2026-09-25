import { useState } from "react";
import { Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { settingsApi } from "@/lib/api/settings";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";

export function ProfileSettings() {
  const { user, login } = useAuth(); // Assuming login or updateUser is available? We can just refresh
  const [name, setName] = useState(user?.name || "");
  const [isSaving, setIsSaving] = useState(false);

  const hasChanges = name !== user?.name;

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await settingsApi.updateProfile({ name });
      toast.success("Profile updated successfully");
      // Ideally update auth context user here, reloading page for now is simple or just assume success
      window.location.reload();
    } catch (error: any) {
      toast.error(error.message || "Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-xl animate-in fade-in duration-300">
      <div>
        <h3 className="text-lg font-medium text-foreground mb-4">Profile Information</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Update your account&apos;s profile information.
        </p>
      </div>
      <div className="grid gap-6">
        <div className="grid gap-2">
          <Label htmlFor="name">Full Name</Label>
          <Input 
            id="name" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
            className="bg-background" 
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="email">Email Address</Label>
          <Input 
            id="email" 
            type="email" 
            value={user?.email || ""} 
            disabled 
            className="bg-background opacity-70" 
          />
          <p className="text-xs text-muted-foreground">
            {user?.auth_provider === "google" 
              ? "Your email is managed by Google."
              : "Email cannot be changed currently."}
          </p>
        </div>
        
        <div className="grid gap-2">
          <Label>Account Creation</Label>
          <p className="text-sm text-muted-foreground">
            {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Unknown"}
          </p>
        </div>
      </div>
      
      <Button 
        onClick={handleSave} 
        disabled={isSaving || !hasChanges} 
        className="bg-primary text-primary-foreground hover:bg-primary/90 mt-4"
      >
        {isSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
        Save Changes
      </Button>
    </div>
  );
}
