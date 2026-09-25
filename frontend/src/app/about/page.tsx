import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function About() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 sm:px-8 py-24 max-w-4xl">
        <h1 className="text-4xl font-bold text-foreground mb-8">About InboxPilot</h1>
        
        <div className="prose prose-slate max-w-none space-y-6 text-muted-foreground">
          <p className="text-lg">
            InboxPilot was built with a singular mission: to eliminate the time spent managing emails 
            so you can focus on what truly matters.
          </p>
          
          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">Our Approach</h2>
          <p>
            We believe that AI shouldn't just be a black box that does things behind your back. That's why 
            we designed InboxPilot around a core philosophy: <strong>Automation without giving up control.</strong>
          </p>
          <p>
            Every action our AI proposes is categorized by risk. Low-risk tasks like categorizing newsletters 
            happen automatically, while high-risk tasks require your explicit approval via Telegram or the Dashboard.
          </p>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">Security First</h2>
          <p>
            We treat your data with the utmost respect. From AES-256-GCM encryption at rest to strict OAuth 
            scopes, we've built InboxPilot from the ground up to be a secure, enterprise-grade platform.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
