"use client";

import { motion } from "framer-motion";
import { Sparkles, Calendar, Smartphone, Activity, Lock, ShieldCheck, Database } from "lucide-react";

export function Features() {
  const features = [
    {
      title: "AI Email Classification",
      description: "Automatically categorizes incoming emails into Bills, Meetings, Forms, and more with high precision.",
      icon: Sparkles,
    },
    {
      title: "Google Calendar Sync",
      description: "Extracts dates, times, and participants to automatically draft meeting invites and reminders.",
      icon: Calendar,
    },
    {
      title: "Telegram Notifications",
      description: "Get instant, actionable push notifications on Telegram when an email needs your approval.",
      icon: Smartphone,
    },
    {
      title: "Audit Logs",
      description: "Complete transparency. See exactly why the AI made a decision, what parameters it extracted, and when.",
      icon: Activity,
    },
  ];

  return (
    <section id="features" className="bg-secondary/30 py-24">
      <div className="container mx-auto px-4 sm:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Everything you need for zero-inbox
          </h2>
          <p className="text-lg text-muted-foreground">
            Powerful features built around a robust, scalable backend architecture.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              className="flex gap-4 p-6 rounded-2xl bg-background border border-border shadow-sm"
            >
              <div className="flex-shrink-0 mt-1">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  <feature.icon className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-foreground">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Encryption Trust Strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-12 max-w-5xl mx-auto"
        >
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-6 px-6 py-4 rounded-2xl bg-background border border-border shadow-sm">
            <div className="flex items-center gap-2 text-green-600">
              <Lock className="w-4 h-4" />
              <span className="text-sm font-semibold">AES-256-GCM Encrypted</span>
            </div>
            <div className="hidden sm:block w-px h-4 bg-border" />
            <div className="flex items-center gap-2 text-primary">
              <Database className="w-4 h-4" />
              <span className="text-sm text-muted-foreground">Email contents encrypted at rest in database</span>
            </div>
            <div className="hidden sm:block w-px h-4 bg-border" />
            <div className="flex items-center gap-2 text-green-600">
              <ShieldCheck className="w-4 h-4" />
              <span className="text-sm text-muted-foreground">Authenticated encryption — tamper-proof</span>
            </div>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
