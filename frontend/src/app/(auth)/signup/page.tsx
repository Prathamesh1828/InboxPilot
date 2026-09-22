import { Metadata } from "next";
import { SignupForm } from "@/components/auth/SignupForm";

export const metadata: Metadata = {
  title: "Sign up | InboxPilot",
  description: "Create a new account.",
};

export default function SignupPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Create an account</h1>
        <p className="text-muted-foreground">
          Enter your details below to create your account
        </p>
      </div>
      <SignupForm />
    </div>
  );
}
