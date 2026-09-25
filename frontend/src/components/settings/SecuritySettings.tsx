import { useState } from "react";
import { Loader2, Key, LogOut, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { settingsApi } from "@/lib/api/settings";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useRouter } from "next/navigation";

export function SecuritySettings() {
  const { user, logout } = useAuth();
  const router = useRouter();
  
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isLoggingOutAll, setIsLoggingOutAll] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const isGoogleAccount = user?.auth_provider === "google";

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error("New passwords do not match");
      return;
    }
    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    try {
      setIsChangingPassword(true);
      await settingsApi.changePassword({ current_password: currentPassword, new_password: newPassword });
      toast.success("Password changed successfully");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error: any) {
      toast.error(error.message || "Failed to change password");
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleLogoutAll = async () => {
    try {
      setIsLoggingOutAll(true);
      await settingsApi.logoutAll();
      toast.success("Signed out of all other sessions");
      logout();
    } catch (error: any) {
      toast.error(error.message || "Failed to sign out");
    } finally {
      setIsLoggingOutAll(false);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      setIsDeleting(true);
      await settingsApi.deleteAccount();
      toast.success("Account deleted permanently");
      logout();
    } catch (error: any) {
      toast.error(error.message || "Failed to delete account");
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-10 max-w-xl animate-in fade-in duration-300">
      
      {!isGoogleAccount && (
        <form onSubmit={handleChangePassword} className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-4">Change Password</h3>
            <p className="text-sm text-muted-foreground mb-6">Update your password to keep your account secure.</p>
          </div>
          
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="current-password">Current Password</Label>
              <Input 
                id="current-password" 
                type="password" 
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
                className="bg-background"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="new-password">New Password</Label>
              <Input 
                id="new-password" 
                type="password" 
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                className="bg-background"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input 
                id="confirm-password" 
                type="password" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                className="bg-background"
              />
            </div>
          </div>
          
          <Button 
            type="submit" 
            disabled={isChangingPassword || !currentPassword || !newPassword || !confirmPassword} 
            className="bg-primary text-primary-foreground hover:bg-primary/90 mt-4"
          >
            {isChangingPassword ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Key className="w-4 h-4 mr-2" />}
            Update Password
          </Button>
        </form>
      )}

      {isGoogleAccount && (
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-4">Authentication</h3>
            <p className="text-sm text-muted-foreground mb-6">You are authenticated via Google.</p>
          </div>
          <div className="p-4 bg-secondary/20 border border-border rounded-xl flex items-center justify-between">
            <div>
              <p className="font-medium">Google Account</p>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
            </div>
            <div className="text-sm font-medium text-success bg-success/10 px-3 py-1 rounded-full">Connected</div>
          </div>
        </div>
      )}

      <div className="pt-8 border-t border-border">
        <div>
          <h3 className="text-lg font-medium text-foreground mb-4">Sessions</h3>
          <p className="text-sm text-muted-foreground mb-6">Manage your active sessions.</p>
        </div>
        <Button 
          variant="outline" 
          onClick={handleLogoutAll}
          disabled={isLoggingOutAll}
        >
          {isLoggingOutAll ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <LogOut className="w-4 h-4 mr-2" />}
          Sign out of all sessions
        </Button>
      </div>

      <div className="pt-8 border-t border-border">
        <div>
          <h3 className="text-lg font-medium text-destructive mb-4">Danger Zone</h3>
          <p className="text-sm text-muted-foreground mb-6">
            Permanently delete your account and all associated data. This action cannot be undone.
          </p>
        </div>
        
        <AlertDialog>
          <AlertDialogTrigger>
            <Button variant="destructive">
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Account
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete your account, 
                remove all connected integrations, and delete your email processing history 
                from our servers.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction 
                onClick={handleDeleteAccount}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {isDeleting ? "Deleting..." : "Yes, delete my account"}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
