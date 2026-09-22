"use client";

import { motion } from "framer-motion";
import { Mail, Brain, ListTodo, ShieldCheck } from "lucide-react";

export function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Connect Gmail",
      description: "Securely link your Gmail account in one click. We never read your emails for training data.",
      icon: Mail,
    },
    {
      number: "02",
      title: "InboxPilot understands",
      description: "Incoming emails are instantly analyzed by advanced LLMs to extract intent, context, and entities.",
      icon: Brain,
    },
    {
      number: "03",
      title: "AI plans the action",
      description: "The system formulates a precise action plan, such as creating a calendar event or drafting a reply.",
      icon: ListTodo,
    },
    {
      number: "04",
      title: "You approve or automate",
      description: "Low-risk actions execute silently. For important actions, you get a quick Telegram ping to approve.",
      icon: ShieldCheck,
    },
  ];

  return (
    <section id="how-it-works" className="container mx-auto px-4 sm:px-8 py-24">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
          How it works
        </h2>
        <p className="text-lg text-muted-foreground">
          A seamless flow from chaotic inbox to structured automation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="relative flex flex-col items-center text-center p-6 rounded-2xl bg-card border border-border shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="absolute -top-4 -left-4 w-12 h-12 bg-primary/10 text-primary font-bold text-xl rounded-full flex items-center justify-center">
              {step.number}
            </div>
            <div className="w-16 h-16 bg-secondary rounded-2xl flex items-center justify-center mb-6 text-primary">
              <step.icon className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-foreground">{step.title}</h3>
            <p className="text-muted-foreground leading-relaxed">
              {step.description}
            </p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
