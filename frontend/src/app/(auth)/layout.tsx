import Link from "next/link";
import { Inbox } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen grid md:grid-cols-2">
      {/* Left panel - Form */}
      <div className="flex flex-col justify-center px-8 sm:px-16 lg:px-24 py-12">
          <Link href="/" className="flex items-center space-x-2 mb-12">
            <img src="/InboxPilot%20Logo.png" alt="InboxPilot" className="h-24 w-auto object-contain scale-125 origin-left" />
          </Link>
        <div className="w-full max-w-sm mx-auto md:mx-0">
          {children}
        </div>
      </div>
      
      {/* Right panel - Visual */}
      <div className="hidden md:flex flex-col justify-center items-center bg-secondary/30 border-l border-border p-12">
        <div className="max-w-md text-center space-y-6">
          <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center text-primary mx-auto">
            <Inbox className="h-10 w-10" />
          </div>
          <h2 className="text-3xl font-bold text-foreground">
            Your inbox, on autopilot.
          </h2>
          <p className="text-muted-foreground text-lg">
            Join the professionals who save hours every week by letting InboxPilot handle the routine.
          </p>
        </div>
      </div>
    </div>
  );
}
