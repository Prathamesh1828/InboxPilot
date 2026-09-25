"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Inbox, Mail, Calendar, Smartphone, CheckCircle, ArrowRight, Loader2 } from "lucide-react";

const steps = [
  { id: "welcome", title: "Welcome to InboxPilot" },
  { id: "gmail", title: "Connect Gmail" },
  { id: "calendar", title: "Connect Calendar" },
  { id: "telegram", title: "Connect Telegram" },
  { id: "preferences", title: "Automation Preferences" },
  { id: "ready", title: "You're ready" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isConnecting, setIsConnecting] = useState(false);

  const nextStep = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex(c => c + 1);
    } else {
      router.push("/dashboard");
    }
  };

  const handleConnect = () => {
    setIsConnecting(true);
    setTimeout(() => {
      setIsConnecting(false);
      nextStep();
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="h-24 border-b border-border flex items-center px-8 overflow-hidden">
        <Link href="/" className="flex items-center space-x-2">
          <img src="/InboxPilot%20Logo%20without%20text.png" alt="InboxPilot" className="h-24 w-auto object-contain shrink-0 scale-125 origin-left" />
        </Link>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          {/* Progress Indicator */}
          <div className="flex items-center justify-between mb-12">
            {steps.map((step, index) => (
              <div key={step.id} className="flex flex-col items-center gap-2">
                <div 
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors
                    ${index < currentStepIndex ? "bg-primary text-primary-foreground" : 
                      index === currentStepIndex ? "bg-primary text-primary-foreground ring-4 ring-primary/20" : 
                      "bg-secondary text-muted-foreground border border-border"}`}
                >
                  {index < currentStepIndex ? <CheckCircle className="w-4 h-4" /> : index + 1}
                </div>
                <span className={`text-xs hidden sm:block ${index <= currentStepIndex ? "text-foreground font-medium" : "text-muted-foreground"}`}>
                  {step.title}
                </span>
              </div>
            ))}
          </div>

          {/* Content Area */}
          <div className="bg-card border border-border rounded-2xl p-8 md:p-12 shadow-xl relative overflow-hidden min-h-[400px] flex flex-col justify-center">
            <AnimatePresence mode="wait">
              {currentStepIndex === 0 && (
                <motion.div
                  key="welcome"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="text-center space-y-6"
                >
                  <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto text-primary">
                    <Inbox className="w-10 h-10" />
                  </div>
                  <h1 className="text-3xl font-bold text-foreground">Welcome to InboxPilot</h1>
                  <p className="text-muted-foreground text-lg max-w-md mx-auto">
                    Let&apos;s get your autonomous inbox set up. We&apos;ll connect your tools so our AI can start handling the routine tasks.
                  </p>
                  <Button onClick={nextStep} size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 mt-4">
                    Get Started <ArrowRight className="ml-2 w-4 h-4" />
                  </Button>
                </motion.div>
              )}

              {currentStepIndex === 1 && (
                <motion.div
                  key="gmail"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="text-center space-y-6"
                >
                  <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mx-auto text-red-500">
                    <Mail className="w-10 h-10" />
                  </div>
                  <h1 className="text-3xl font-bold text-foreground">Connect Gmail</h1>
                  <p className="text-muted-foreground text-lg max-w-md mx-auto">
                    InboxPilot needs access to your Gmail to read incoming messages and perform actions on your behalf.
                  </p>
                  <div className="flex gap-4 justify-center mt-4">
                    <Button onClick={handleConnect} size="lg" disabled={isConnecting} className="bg-red-500 text-white hover:bg-red-600">
                      {isConnecting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Connect Gmail"}
                    </Button>
                  </div>
                </motion.div>
              )}

              {currentStepIndex === 2 && (
                <motion.div
                  key="calendar"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="text-center space-y-6"
                >
                  <div className="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto text-blue-500">
                    <Calendar className="w-10 h-10" />
                  </div>
                  <h1 className="text-3xl font-bold text-foreground">Connect Calendar</h1>
                  <p className="text-muted-foreground text-lg max-w-md mx-auto">
                    Allow InboxPilot to automatically draft calendar invites when it detects meetings in your emails.
                  </p>
                  <div className="flex gap-4 justify-center mt-4">
                    <Button onClick={nextStep} variant="outline" size="lg" className="border-border text-foreground hover:bg-secondary">
                      Skip for now
                    </Button>
                    <Button onClick={handleConnect} size="lg" disabled={isConnecting} className="bg-blue-500 text-white hover:bg-blue-600">
                      {isConnecting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Connect Calendar"}
                    </Button>
                  </div>
                </motion.div>
              )}

              {currentStepIndex === 3 && (
                <motion.div
                  key="telegram"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="text-center space-y-6"
                >
                  <div className="w-20 h-20 bg-[#229ED9]/10 rounded-full flex items-center justify-center mx-auto text-[#229ED9]">
                    <Smartphone className="w-10 h-10" />
                  </div>
                  <h1 className="text-3xl font-bold text-foreground">Connect Telegram</h1>
                  <p className="text-muted-foreground text-lg max-w-md mx-auto">
                    Get instant push notifications on your phone when an important action requires your approval.
                  </p>
                  <div className="flex gap-4 justify-center mt-4">
                    <Button onClick={nextStep} variant="outline" size="lg" className="border-border text-foreground hover:bg-secondary">
                      Skip for now
                    </Button>
                    <Button onClick={handleConnect} size="lg" disabled={isConnecting} className="bg-[#229ED9] text-white hover:bg-[#229ED9]/90">
                      {isConnecting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Connect Telegram"}
                    </Button>
                  </div>
                </motion.div>
              )}

              {currentStepIndex === 4 && (
                <motion.div
                  key="preferences"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="text-center space-y-6"
                >
                  <h1 className="text-3xl font-bold text-foreground">Automation Preferences</h1>
                  <p className="text-muted-foreground text-lg max-w-md mx-auto">
                    How aggressive do you want the automation to be? You can change this later.
                  </p>
                  <div className="space-y-4 max-w-md mx-auto text-left mt-6">
                    <div className="border border-border p-4 rounded-xl cursor-pointer hover:border-primary transition-colors bg-secondary/30" onClick={nextStep}>
                      <h3 className="font-bold text-foreground">Cautious (Recommended)</h3>
                      <p className="text-sm text-muted-foreground">Only automate trivial tasks. Ask for approval for everything else.</p>
                    </div>
                    <div className="border border-border p-4 rounded-xl cursor-pointer hover:border-primary transition-colors" onClick={nextStep}>
                      <h3 className="font-bold text-foreground">Balanced</h3>
                      <p className="text-sm text-muted-foreground">Automate obvious tasks. Ask for approval on medium-risk items.</p>
                    </div>
                    <div className="border border-border p-4 rounded-xl cursor-pointer hover:border-primary transition-colors" onClick={nextStep}>
                      <h3 className="font-bold text-foreground">Aggressive</h3>
                      <p className="text-sm text-muted-foreground">Automate everything possible. Only ask for approval on destructive actions.</p>
                    </div>
                  </div>
                </motion.div>
              )}

              {currentStepIndex === 5 && (
                <motion.div
                  key="ready"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center space-y-6"
                >
                  <div className="w-24 h-24 bg-green-500/10 rounded-full flex items-center justify-center mx-auto text-green-500 mb-4">
                    <CheckCircle className="w-12 h-12" />
                  </div>
                  <h1 className="text-3xl font-bold text-foreground">You&apos;re all set!</h1>
                  <p className="text-muted-foreground text-lg max-w-md mx-auto">
                    InboxPilot is now monitoring your inbox and ready to help.
                  </p>
                  <Button onClick={nextStep} size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 mt-8 w-full max-w-xs">
                    Go to Dashboard
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  );
}
