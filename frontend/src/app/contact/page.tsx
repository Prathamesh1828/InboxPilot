"use client";

import { MinimalHeader } from "@/components/landing/MinimalHeader";
import { MinimalFooter } from "@/components/landing/MinimalFooter";
import { Mail, MessageSquare, Shield, Lock, Users } from "lucide-react";

export default function Contact() {
  return (
    <div className="flex flex-col min-h-screen">
      <MinimalHeader />
      <main className="flex-1">
        
        {/* Hero Section */}
        <section className="pt-24 pb-16 px-4 sm:px-8 max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
            Let's talk about InboxPilot.
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground mb-6 max-w-2xl mx-auto">
            Have a question, found an issue, or want to learn more about how InboxPilot can simplify your inbox? We'd love to hear from you.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/50 text-sm text-foreground/80 font-medium">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            We typically respond within 1–2 business days.
          </div>
        </section>

        {/* Contact Content */}
        <section className="px-4 sm:px-8 pb-20 max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20">
            
            {/* Left Column */}
            <div>
              <h2 className="text-2xl font-semibold text-foreground mb-8">Get in touch</h2>
              
              <div className="space-y-8 mb-12">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
                    <Mail className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">Email</h3>
                    <p className="text-sm text-muted-foreground mb-1">For general inquiries and partnerships.</p>
                    <a href="mailto:hello@inboxpilot.example.com" className="text-sm font-medium text-primary hover:underline transition-colors">
                      hello@inboxpilot.example.com
                    </a>
                  </div>
                </div>
                
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
                    <MessageSquare className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">Support</h3>
                    <p className="text-sm text-muted-foreground mb-1">For help with your account or workflows.</p>
                    <a href="mailto:support@inboxpilot.example.com" className="text-sm font-medium text-primary hover:underline transition-colors">
                      support@inboxpilot.example.com
                    </a>
                  </div>
                </div>
              </div>

              {/* Privacy Notice Card */}
              <div className="bg-secondary/30 border border-border rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-3">
                  <Shield className="w-5 h-5 text-primary" />
                  <h4 className="font-semibold text-foreground">Your privacy matters</h4>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Never include passwords, access tokens, or sensitive email content in a support request.
                </p>
              </div>
            </div>
            
            {/* Right Column */}
            <div>
              <div className="bg-card border border-border rounded-3xl p-6 md:p-8 shadow-sm">
                <h2 className="text-2xl font-semibold text-foreground mb-6">Send us a message</h2>
                {/* Form is ready for backend integration. Currently prevents default behavior. */}
                <form 
                  className="space-y-5" 
                  onSubmit={(e) => {
                    e.preventDefault();
                    // Backend integration endpoint goes here.
                  }}
                >
                  <div className="space-y-1.5">
                    <label htmlFor="name" className="block text-sm font-medium text-foreground">Name</label>
                    <input 
                      type="text" 
                      id="name"
                      name="name"
                      required
                      className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow" 
                      placeholder="Your name" 
                    />
                  </div>
                  
                  <div className="space-y-1.5">
                    <label htmlFor="email" className="block text-sm font-medium text-foreground">Email</label>
                    <input 
                      type="email" 
                      id="email"
                      name="email"
                      required
                      className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow" 
                      placeholder="you@example.com" 
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label htmlFor="subject" className="block text-sm font-medium text-foreground">Subject</label>
                    <input 
                      type="text" 
                      id="subject"
                      name="subject"
                      required
                      className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow" 
                      placeholder="How can we help?" 
                    />
                  </div>
                  
                  <div className="space-y-1.5">
                    <label htmlFor="message" className="block text-sm font-medium text-foreground">Message</label>
                    <textarea 
                      id="message"
                      name="message"
                      required
                      rows={5} 
                      className="w-full rounded-xl border border-border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow resize-y" 
                      placeholder="Tell us how we can help..."
                    ></textarea>
                  </div>
                  
                  <button 
                    type="submit" 
                    className="w-full bg-primary text-primary-foreground font-medium py-3 rounded-xl text-sm transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background mt-2"
                  >
                    Send Message
                  </button>
                </form>
              </div>
            </div>

          </div>
        </section>

        {/* Trust Section */}
        <section className="bg-secondary/20 border-t border-border py-16">
          <div className="container mx-auto px-4 sm:px-8 max-w-5xl text-center">
            <h2 className="text-2xl font-semibold text-foreground mb-12">Built with privacy in mind.</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-background border border-border flex items-center justify-center text-primary mb-4 shadow-sm">
                  <Shield className="w-5 h-5" />
                </div>
                <h3 className="font-medium text-foreground mb-2">Your data stays protected</h3>
                <p className="text-sm text-muted-foreground max-w-xs">
                  Sensitive information should never be included in support requests.
                </p>
              </div>

              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-background border border-border flex items-center justify-center text-primary mb-4 shadow-sm">
                  <Lock className="w-5 h-5" />
                </div>
                <h3 className="font-medium text-foreground mb-2">Secure by design</h3>
                <p className="text-sm text-muted-foreground max-w-xs">
                  Use the same security principles throughout the InboxPilot platform.
                </p>
              </div>

              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-background border border-border flex items-center justify-center text-primary mb-4 shadow-sm">
                  <Users className="w-5 h-5" />
                </div>
                <h3 className="font-medium text-foreground mb-2">Human support</h3>
                <p className="text-sm text-muted-foreground max-w-xs">
                  Contact us when you need help with the product.
                </p>
              </div>
            </div>
          </div>
        </section>

      </main>
      <MinimalFooter />
    </div>
  );
}
