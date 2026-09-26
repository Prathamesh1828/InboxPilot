"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, CheckCircle2, ChevronRight, ChevronLeft, X, Lock } from "lucide-react";

interface Step {
  targetSelector: string | null;
  title: string;
  content: React.ReactNode;
  position?: "left" | "right" | "top" | "bottom" | "center";
}

export function OnboardingWalkthrough() {
  const [isClient, setIsClient] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsClient(true);
    const completed = localStorage.getItem("onboarding_completed");
    if (!completed) {
      // Small delay to ensure rendering is complete
      const timer = setTimeout(() => setIsVisible(true), 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const steps: Step[] = useMemo(() => [
    {
      targetSelector: 'a[href="/integrations"]',
      title: "Connect your Gmail",
      position: "right",
      content: (
        <div className="space-y-4 text-sm">
          <p className="text-foreground/90">
            Connect your Gmail account to let InboxPilot securely read and organize your inbox, classify incoming emails, and trigger automated workflows.
          </p>
          <div className="bg-muted p-3 rounded-md text-foreground/80 border border-border">
            Your Gmail connection uses Google OAuth. InboxPilot only accesses the permissions required for its email automation features.
          </div>
        </div>
      ),
    },
    {
      targetSelector: 'a[href="/inbox"]',
      title: "Your inbox, organized",
      position: "right",
      content: (
        <div className="space-y-4 text-sm">
          <p className="text-foreground/90">
            Once connected, InboxPilot processes your emails and organizes them into categories such as Bill, Meeting, Spam, Form, Reminder, and Other.
          </p>
          <div className="bg-card border border-border p-4 rounded-md shadow-sm">
            <h4 className="font-semibold flex items-center gap-2 mb-2 text-foreground">
              <Shield className="w-4 h-4 text-primary" />
              Your email data is protected
            </h4>
            <p className="text-foreground/80 mb-2">
              Email content stored by InboxPilot is encrypted before being written to the database. Sensitive email fields are stored as encrypted ciphertext rather than readable plaintext. Data is decrypted only when required by authorized application workflows.
            </p>
            <p className="text-foreground/80 text-xs border-t border-border pt-2 mt-2">
              You can still view your own emails normally through the Inbox interface because InboxPilot decrypts the data only when needed for your authenticated session.
            </p>
          </div>
        </div>
      ),
    },
    {
      targetSelector: 'a[href="/approvals"]',
      title: "Stay in control",
      position: "right",
      content: (
        <div className="space-y-4 text-sm">
          <p className="text-foreground/90">
            When InboxPilot wants to perform an action that requires your approval, it creates an approval request instead of executing the action automatically.
          </p>
          <p className="text-foreground/80">
            You can review the proposed action and approve or reject it from the dashboard. Approved actions are then executed by the workflow.
          </p>
        </div>
      ),
    },
    {
      targetSelector: 'a[href="/audit"]',
      title: "Everything is traceable",
      position: "right",
      content: (
        <div className="space-y-4 text-sm">
          <p className="text-foreground/90">
            Audit Logs provide a chronological record of what InboxPilot did with each email and workflow.
          </p>
          <div className="flex flex-wrap gap-2 py-1">
            {["Email received", "Classification completed", "Grounding passed", "Safety evaluated", "Approval created", "Workflow completed"].map(tag => (
              <span key={tag} className="text-xs bg-sidebar-accent text-sidebar-accent-foreground px-2 py-1 rounded-full border border-border">
                {tag}
              </span>
            ))}
          </div>
          <p className="text-foreground/80">
            This gives you visibility into how an email moved through the InboxPilot workflow and helps you understand why an action was taken.
          </p>
        </div>
      ),
    },
    {
      targetSelector: null, // center modal
      title: "You're ready to automate",
      position: "center",
      content: (
        <div className="space-y-6 text-sm text-center">
          <p className="text-foreground/90">
            InboxPilot can now organize your inbox, plan workflows, request approval when needed, and keep a complete audit trail of automated actions.
          </p>
          <div className="flex flex-col gap-3 max-w-sm mx-auto text-left">
            <div className="flex items-center gap-3 bg-card p-3 rounded-lg border border-border shadow-sm">
              <Lock className="w-5 h-5 text-primary" />
              <span className="font-medium">Secure email processing</span>
            </div>
            <div className="flex items-center gap-3 bg-card p-3 rounded-lg border border-border shadow-sm">
              <Shield className="w-5 h-5 text-primary" />
              <span className="font-medium">Human approval when needed</span>
            </div>
            <div className="flex items-center gap-3 bg-card p-3 rounded-lg border border-border shadow-sm">
              <CheckCircle2 className="w-5 h-5 text-primary" />
              <span className="font-medium">Complete audit trail</span>
            </div>
          </div>
        </div>
      ),
    },
  ], []);

  const updateTargetRect = useCallback(() => {
    const selector = steps[currentStep]?.targetSelector;
    if (selector) {
      const el = document.querySelector(selector);
      if (el) {
        setTargetRect(el.getBoundingClientRect());
        el.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" });
      } else {
        setTargetRect(null);
      }
    } else {
      setTargetRect(null);
    }
  }, [currentStep, steps]);

  useEffect(() => {
    if (isVisible) {
      // Add slight delay to allow layout shifts if sidebar expands/collapses
      const timerId = setTimeout(updateTargetRect, 300);
      window.addEventListener("resize", updateTargetRect);
      return () => {
        clearTimeout(timerId);
        window.removeEventListener("resize", updateTargetRect);
      };
    }
  }, [currentStep, isVisible, updateTargetRect]);

  const completeTour = () => {
    localStorage.setItem("onboarding_completed", "true");
    setIsVisible(false);
  };

  if (!isClient || !isVisible) return null;

  const step = steps[currentStep];
  
  // Calculate card position
  let cardStyle: React.CSSProperties = {};
  if (step.position === "center" || !targetRect) {
    cardStyle = {
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
      width: "100%",
      maxWidth: "500px",
    };
  } else {
    // Default to right of the target for the sidebar
    // If mobile, it might be better to position differently, but let's stick to simple logic
    const padding = 20;
    const isMobile = window.innerWidth < 1024;
    
    if (isMobile) {
        cardStyle = {
            top: targetRect.bottom + padding,
            left: "50%",
            transform: "translateX(-50%)",
            width: "calc(100% - 32px)",
            maxWidth: "400px",
        };
    } else {
        cardStyle = {
            top: targetRect.top,
            left: targetRect.right + padding,
            width: "400px",
        };
    }
  }

  return (
    <div className="fixed inset-0 z-[99999] pointer-events-auto">
      {/* Overlay mask */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <defs>
          <mask id="hole-mask">
            <rect width="100%" height="100%" fill="white" />
            {targetRect && step.position !== "center" && (
              <rect 
                x={targetRect.x - 4} 
                y={targetRect.y - 4} 
                width={targetRect.width + 8} 
                height={targetRect.height + 8} 
                rx={8} 
                fill="black" 
              />
            )}
          </mask>
        </defs>
        <rect 
          width="100%" 
          height="100%" 
          fill="rgba(42, 16, 45, 0.6)" 
          mask="url(#hole-mask)" 
          className="transition-all duration-500 ease-in-out"
        />
      </svg>
      
      {/* Click blocker */}
      <div className="absolute inset-0 z-0" onClick={(e) => e.stopPropagation()} />

      {/* Card */}
      <div 
        className="absolute z-10 pointer-events-none" 
        style={cardStyle}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, y: 10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="bg-background border border-border shadow-2xl rounded-xl overflow-hidden flex flex-col max-h-[90vh] pointer-events-auto"
            style={{ width: "100%" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
              <h3 className="font-bold text-lg text-foreground">{step.title}</h3>
              {currentStep < steps.length - 1 && (
                <button 
                  onClick={completeTour}
                  className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors flex items-center gap-1"
                >
                  Skip tour <X className="w-4 h-4" />
                </button>
              )}
            </div>
            
            {/* Content */}
            <div className="p-6 overflow-y-auto bg-background">
              {step.content}
            </div>
            
            {/* Footer Navigation */}
            <div className="px-6 py-4 border-t border-border bg-card flex items-center justify-between">
              <div className="flex gap-1">
                {steps.map((_, i) => (
                  <div 
                    key={i} 
                    className={`w-2 h-2 rounded-full transition-colors ${i === currentStep ? 'bg-primary' : 'bg-muted-foreground/30'}`}
                  />
                ))}
              </div>
              
              <div className="flex gap-3">
                {currentStep > 0 && (
                  <button 
                    onClick={() => setCurrentStep(prev => prev - 1)}
                    className="px-4 py-2 text-sm font-medium text-foreground bg-muted hover:bg-border rounded-lg transition-colors flex items-center gap-1"
                  >
                    <ChevronLeft className="w-4 h-4" /> Back
                  </button>
                )}
                
                {currentStep < steps.length - 1 ? (
                  <button 
                    onClick={() => setCurrentStep(prev => prev + 1)}
                    className="px-4 py-2 text-sm font-medium text-primary-foreground bg-primary hover:bg-primary/90 rounded-lg transition-colors flex items-center gap-1 shadow-sm"
                  >
                    Next <ChevronRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button 
                    onClick={completeTour}
                    className="px-6 py-2 text-sm font-bold text-primary-foreground bg-primary hover:bg-primary/90 rounded-lg transition-colors shadow-sm"
                  >
                    Get Started
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
