import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

export default function TermsOfService() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 sm:px-8 py-24 max-w-4xl">
        <h1 className="text-4xl font-bold text-foreground mb-8">Terms of Service</h1>
        
        <div className="prose prose-slate max-w-none space-y-6 text-muted-foreground">
          <p>Last updated: {new Date().toLocaleDateString()}</p>
          
          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">1. Acceptance of Terms</h2>
          <p>
            By accessing or using InboxPilot, you agree to be bound by these Terms of Service. If you do not agree 
            to these terms, please do not use our services.
          </p>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">2. Description of Service</h2>
          <p>
            InboxPilot is an AI-powered email automation platform that categorizes emails, extracts information, 
            and assists with email management and calendar scheduling. The service connects to your Gmail account 
            via OAuth to perform these actions.
          </p>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">3. User Responsibilities</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>You must provide accurate information when creating an account.</li>
            <li>You are responsible for safeguarding your account credentials.</li>
            <li>You agree to review and approve/reject high and medium risk automated actions.</li>
            <li>You must not use the service for any illegal or unauthorized purpose.</li>
          </ul>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">4. Privacy & Data Security</h2>
          <p>
            Your privacy is important to us. We encrypt your email data at rest using AES-256-GCM. 
            For more details, please review our Privacy Policy. By using InboxPilot, you consent to our data 
            practices as outlined in the Privacy Policy.
          </p>

          <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">5. Limitation of Liability</h2>
          <p>
            InboxPilot is provided "as is" without warranties of any kind. We shall not be liable for any indirect, 
            incidental, special, consequential, or punitive damages resulting from your use of the service.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
