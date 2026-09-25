"use client";

import { motion } from "framer-motion";
import { ShieldAlert, ShieldCheck, Shield, Lock } from "lucide-react";

export function Safety() {
  return (
    <section id="security" className="container mx-auto px-4 sm:px-8 py-24">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6">
            Automation without <br /> giving up control.
          </h2>
          <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
            AI proposes. InboxPilot&apos;s safety layer decides. 
            We categorize actions by risk level, ensuring you always 
            have the final say on anything that matters.
          </p>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center text-green-600 mt-1 flex-shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-foreground">Low Risk</h4>
                <p className="text-sm text-muted-foreground">Automatically executed (e.g., categorizing newsletters)</p>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary mt-1 flex-shrink-0">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-foreground">Medium Risk</h4>
                <p className="text-sm text-muted-foreground">Requires Telegram or Dashboard approval (e.g., adding meetings)</p>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-destructive/10 flex items-center justify-center text-destructive mt-1 flex-shrink-0">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-foreground">High Risk</h4>
                <p className="text-sm text-muted-foreground">Blocked or manually reviewed (e.g., deleting important threads)</p>
              </div>
            </div>
          </div>

          {/* Encryption Badge */}
          <div className="mt-8 flex items-center gap-3 px-4 py-3 rounded-xl bg-green-500/5 border border-green-500/20 w-fit">
            <Lock className="w-4 h-4 text-green-600 flex-shrink-0" />
            <p className="text-sm text-green-700 font-medium">
              All email contents encrypted at rest using <span className="font-bold">AES-256-GCM</span>
            </p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="relative"
        >
          {/* Mockup of a Telegram Notification */}
          <div className="w-full max-w-sm mx-auto bg-card border border-border shadow-2xl rounded-3xl overflow-hidden p-6 space-y-4">
            <div className="flex items-center gap-3 border-b border-border pb-4">
              <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                T
              </div>
              <div>
                <p className="font-medium text-foreground leading-none">InboxPilot Bot</p>
                <p className="text-xs text-muted-foreground mt-1">bot</p>
              </div>
            </div>
            
            <div className="bg-secondary/50 rounded-2xl rounded-tl-sm p-4 space-y-3">
              <p className="font-medium text-foreground">Calendar event detected 📅</p>
              <div className="bg-background rounded-lg p-3 border border-border text-sm space-y-1">
                <p><span className="text-muted-foreground">Meeting:</span> Client discussion</p>
                <p><span className="text-muted-foreground">Time:</span> Tomorrow · 11:00 AM</p>
              </div>
              <p className="text-sm text-muted-foreground">Do you want me to add this to your Google Calendar?</p>
              
              <div className="flex gap-2 pt-2">
                <button className="flex-1 bg-green-500/10 text-green-600 font-medium py-2 rounded-lg text-sm transition-colors hover:bg-green-500/20">
                  Approve
                </button>
                <button className="flex-1 bg-destructive/10 text-destructive font-medium py-2 rounded-lg text-sm transition-colors hover:bg-destructive/20">
                  Reject
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
