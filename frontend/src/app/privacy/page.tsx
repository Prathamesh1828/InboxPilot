import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function PrivacyPolicy() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 sm:px-8 py-24 max-w-4xl">
        <h1 className="text-4xl font-bold text-foreground mb-8">Privacy Policy</h1>
        
        <div className="prose prose-slate max-w-none space-y-6 text-muted-foreground">
          <p>Last updated: {new Date().toLocaleDateString()}</p>
          
          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">1. Introduction</h2>
          <p>
            Welcome to InboxPilot. We respect your privacy and are committed to protecting your personal data. 
            This privacy policy explains how we collect, use, and safeguard your information when you use our 
            AI-powered email automation platform.
          </p>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">2. Data We Collect</h2>
          <p>
            When you use InboxPilot, we collect information necessary to provide our services:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Account Information:</strong> Your name, email address, and Google OAuth credentials.</li>
            <li><strong>Email Content:</strong> We securely ingest and process your emails using AI to provide automation. All email contents are encrypted at rest using AES-256-GCM.</li>
            <li><strong>Usage Data:</strong> Information about how you interact with our platform and automation workflows.</li>
          </ul>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">3. How We Use Your Data</h2>
          <p>We use the collected data exclusively to:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Provide, maintain, and improve the InboxPilot service.</li>
            <li>Classify emails and generate automation plans using AI.</li>
            <li>Notify you via Telegram or the Dashboard for required approvals.</li>
            <li>Maintain audit logs for transparency and security.</li>
          </ul>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">4. Data Security</h2>
          <p>
            Security is our top priority. We implement robust security measures, including:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>AES-256-GCM Encryption:</strong> All sensitive email data is encrypted at rest in our database.</li>
            <li><strong>No Plaintext Logs:</strong> We strictly redact sensitive information from our application logs.</li>
            <li><strong>OAuth Scopes:</strong> We only request the minimum permissions necessary to function.</li>
          </ul>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">5. Contact Us</h2>
          <p>
            If you have any questions about this Privacy Policy, please contact us at privacy@inboxpilot.example.com.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
