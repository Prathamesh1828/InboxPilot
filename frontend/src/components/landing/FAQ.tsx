"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, X, Shield, Lock, FileText } from "lucide-react";

const faqs = [
  {
    question: "What is InboxPilot?",
    answer: "InboxPilot is an AI-powered email workflow agent that understands incoming emails, plans actions, and automates routine tasks while requiring your approval for sensitive actions."
  },
  {
    question: "Can InboxPilot read my emails?",
    answer: "Yes. Gmail access is used to process incoming emails and perform the workflow capabilities you enable. Your connected account is accessed through Google's OAuth authorization."
  },
  {
    question: "Can InboxPilot send emails or modify my calendar without my approval?",
    answer: "Sensitive or external-facing actions are routed through the approval workflow before execution. Low-risk actions can be automated according to the configured workflow."
  },
  {
    question: "What happens to my email data?",
    answer: "Emails are processed by InboxPilot to classify them, determine relevant actions, and maintain workflow history. Access is limited to the integrations and capabilities required by the application."
  },
  {
    question: "Can anyone see my email data?",
    answer: "Email data stored by InboxPilot is encrypted using AES-256-GCM to protect sensitive information at rest. Your connected data is used by InboxPilot to perform the workflow capabilities you authorize."
  },
  {
    question: "Why does InboxPilot need Google Calendar access?",
    answer: "Calendar access allows InboxPilot to create or manage calendar-related actions when an email requires scheduling."
  },
  {
    question: "Why do I need Telegram?",
    answer: "Telegram can be used to receive real-time notifications and review or respond to pending approval requests without opening the InboxPilot dashboard."
  },
  {
    question: "Can I disconnect my accounts?",
    answer: "Yes. Connected integrations can be disconnected from the Integrations section of InboxPilot."
  }
];

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const id = React.useId();

  return (
    <div className="border-b border-border last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls={`faq-answer-${id}`}
        id={`faq-button-${id}`}
        className="w-full flex items-center justify-between py-5 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-lg px-2 -mx-2 transition-colors hover:bg-secondary/20"
      >
        <span className="text-base font-medium text-foreground">{question}</span>
        <div className="ml-4 flex-shrink-0 text-muted-foreground transition-transform duration-200">
          {isOpen ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
        </div>
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            id={`faq-answer-${id}`}
            role="region"
            aria-labelledby={`faq-button-${id}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="pb-5 px-2 -mx-2">
              <p className="text-muted-foreground text-sm leading-relaxed">
                {answer}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function FAQ() {
  return (
    <section id="faq" className="container mx-auto px-4 sm:px-8 py-24">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-muted-foreground">
            Everything you need to know about InboxPilot.
          </p>
        </div>

        <div className="bg-card border border-border rounded-2xl p-6 md:p-8 shadow-sm">
          {faqs.map((faq, i) => (
            <FAQItem key={i} question={faq.question} answer={faq.answer} />
          ))}
        </div>

        {/* Trust Block */}
        <div className="mt-16 text-center max-w-2xl mx-auto">
          <h3 className="text-xl font-semibold text-foreground mb-3">
            Your inbox. Your control.
          </h3>
          <p className="text-sm text-muted-foreground mb-8">
            Connected services are used only for the capabilities you authorize. Sensitive actions go through human approval, and workflow activity is recorded in an audit trail.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-foreground/80 font-medium">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-primary" />
              <span>OAuth-secured connections</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary" />
              <span>Human approval for sensitive actions</span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-primary" />
              <span>Complete audit trail</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
