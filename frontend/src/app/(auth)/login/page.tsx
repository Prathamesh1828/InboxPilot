"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { authApi } from "@/lib/auth-api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, CheckCircle2, ShieldAlert, ListChecks } from "lucide-react";

// Separated into its own component so it can be wrapped in Suspense
// (required by Next.js when using useSearchParams in a static page)
function OAuthErrorListener({ onError }: { onError: (msg: string) => void }) {
  const searchParams = useSearchParams();
  useEffect(() => {
    const err = searchParams.get("error");
    if (err === "oauth_failed") {
      onError("Google authentication failed. Please try again.");
    }
  }, [searchParams, onError]);
  return null;
}

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    
    try {
      const user = await authApi.login({ email, password });
      login(user);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-background">
      {/* Listen for OAuth errors in URL without blocking prerender */}
      <Suspense fallback={null}>
        <OAuthErrorListener onError={setError} />
      </Suspense>

      {/* Left Column: Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12 order-2 lg:order-1">
        <div className="w-full max-w-md bg-card border border-border rounded-2xl p-6 sm:p-8 shadow-sm">
          <div className="text-center mb-8">
            <Link href="/">
              <img src="/InboxPilot%20Logo.png" alt="InboxPilot" className="h-12 w-auto mx-auto object-contain lg:hidden mb-6" />
            </Link>
            <h2 className="text-2xl font-semibold text-foreground">Welcome back</h2>
            <p className="mt-2 text-sm text-muted-foreground">Sign in to your account</p>
          </div>
          
          {error && (
            <div className="mb-6 p-3 bg-destructive/10 border border-destructive/20 text-destructive text-sm rounded-lg">
              {error}
            </div>
          )}

          <Button 
            variant="outline" 
            className="w-full h-11 relative" 
            type="button"
            onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/gmail/login?intent=login`}
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            Continue with Google
          </Button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">Or</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                required 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-background/50 focus:bg-background"
                placeholder="name@example.com"
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link href="#" className="text-xs text-primary hover:text-primary/80 transition-colors">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input 
                  id="password" 
                  type={showPassword ? "text" : "password"}
                  required 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-background/50 focus:bg-background pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 px-3 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            
            <div className="pt-2">
              <Button type="submit" className="w-full h-11" disabled={isLoading}>
                {isLoading ? "Signing in..." : "Sign In"}
              </Button>
            </div>
          </form>

          <div className="mt-6 pt-6 border-t border-border text-center">
            <p className="text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Link href="/signup" className="text-primary hover:text-primary/80 font-medium transition-colors">
                Create one
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Right Column: Branding */}
      <div className="w-full lg:w-1/2 bg-secondary/20 hidden lg:flex flex-col items-center justify-center p-6 lg:p-8 xl:p-12 order-1 lg:order-2 border-l border-border relative overflow-hidden h-screen max-h-screen">
        {/* Subtle decorative glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] xl:w-[500px] h-[300px] xl:h-[500px] bg-primary/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-[200px] xl:w-[400px] h-[200px] xl:h-[400px] bg-[#FC6C26]/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col items-center w-full max-w-[480px] gap-6 xl:gap-8">
          <img src="/InboxPilot%20Logo.png" alt="InboxPilot" className="h-12 xl:h-16 w-auto object-contain shrink-0" />
          
          {/* Compact Workflow Indicator in place of Headline */}
          <div className="flex items-center justify-center gap-1.5 sm:gap-3 text-[10px] sm:text-xs font-semibold uppercase tracking-wider text-muted-foreground/80 bg-background/50 backdrop-blur-md px-4 py-2 rounded-xl border border-border/50 shadow-sm">
            <span className="text-foreground">Classify</span>
            <span>→</span>
            <span className="text-foreground">Plan</span>
            <span>→</span>
            <span className="text-foreground">Approve</span>
            <span>→</span>
            <span className="text-foreground">Execute</span>
          </div>

          {/* Feature Highlights */}
          <div className="flex flex-wrap justify-center gap-2 xl:gap-3">
            <div className="flex items-center gap-2 bg-background/60 backdrop-blur-sm border border-border/50 px-3 py-1.5 xl:px-4 xl:py-2 rounded-full shadow-sm">
              <div className="w-1.5 h-1.5 xl:w-2 xl:h-2 rounded-full bg-primary" />
              <span className="text-xs xl:text-sm font-medium text-foreground">AI-powered workflows</span>
            </div>
            <div className="flex items-center gap-2 bg-background/60 backdrop-blur-sm border border-border/50 px-3 py-1.5 xl:px-4 xl:py-2 rounded-full shadow-sm">
              <div className="w-1.5 h-1.5 xl:w-2 xl:h-2 rounded-full bg-[#FC6C26]" />
              <span className="text-xs xl:text-sm font-medium text-foreground">Human approval when it matters</span>
            </div>
            <div className="flex items-center gap-2 bg-background/60 backdrop-blur-sm border border-border/50 px-3 py-1.5 xl:px-4 xl:py-2 rounded-full shadow-sm">
              <div className="w-1.5 h-1.5 xl:w-2 xl:h-2 rounded-full bg-success" />
              <span className="text-xs xl:text-sm font-medium text-foreground">Complete audit trail</span>
            </div>
          </div>

          {/* Product Preview Card */}
          <div className="w-full bg-background/70 backdrop-blur-md border border-border/60 rounded-2xl p-4 xl:p-6 shadow-xl relative mt-2">
            <div className="space-y-3 xl:space-y-4">
              {/* Activity Item 1 */}
              <div className="flex gap-3 xl:gap-4 items-start p-3 xl:p-3.5 bg-background rounded-xl border border-border/50 shadow-sm transition-transform hover:-translate-y-0.5">
                <div className="w-7 h-7 xl:w-8 xl:h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-3.5 h-3.5 xl:w-4 xl:h-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs xl:text-sm font-semibold text-foreground truncate">Email classified</p>
                  <p className="text-[10px] xl:text-xs text-muted-foreground mt-0.5 truncate">Categorized as "Invoice" with 98% confidence.</p>
                </div>
              </div>
              
              {/* Activity Item 2 */}
              <div className="flex gap-3 xl:gap-4 items-center p-3 xl:p-3.5 bg-background rounded-xl border border-border/50 shadow-sm transition-transform hover:-translate-y-0.5">
                <div className="w-7 h-7 xl:w-8 xl:h-8 rounded-full bg-warning/10 flex items-center justify-center shrink-0">
                  <ShieldAlert className="w-3.5 h-3.5 xl:w-4 xl:h-4 text-warning" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs xl:text-sm font-semibold text-foreground truncate">Approval required</p>
                  <p className="text-[10px] xl:text-xs text-muted-foreground mt-0.5 truncate">Drafted reply to client needs review.</p>
                </div>
                <div className="px-2 py-1 xl:px-3 xl:py-1.5 bg-[#FC6C26] text-white text-[9px] xl:text-[10px] font-semibold rounded-md shadow-sm shrink-0">
                  Review
                </div>
              </div>

              {/* Activity Item 3 */}
              <div className="flex gap-3 xl:gap-4 items-start p-3 xl:p-3.5 bg-background rounded-xl border border-border/50 shadow-sm transition-transform hover:-translate-y-0.5">
                <div className="w-7 h-7 xl:w-8 xl:h-8 rounded-full bg-success/10 flex items-center justify-center shrink-0">
                  <ListChecks className="w-3.5 h-3.5 xl:w-4 xl:h-4 text-success" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs xl:text-sm font-semibold text-foreground truncate">Workflow completed</p>
                  <p className="text-[10px] xl:text-xs text-muted-foreground mt-0.5 truncate">Receipt successfully saved to Google Drive.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
