"use client";

import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Search, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmailRow, EmailData } from "@/components/inbox/EmailRow";
import { emailsApi } from "@/lib/api/emails";

export default function InboxPage() {
  const [emails, setEmails] = useState<EmailData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    emailsApi.getMany()
      .then((data: any) => {
        const mappedEmails: EmailData[] = data.map((email: any) => ({
          id: String(email.id),
          sender: email.sender,
          subject: email.subject || "(No Subject)",
          preview: email.body ? email.body.substring(0, 100) : "",
          category: email.category || "OTHER",
          confidence: Math.round((email.classification_confidence || 0) * 100),
          status: email.status,
          timestamp: email.received_at, // will be parsed by EmailRow
          isUnread: false
        }));
        setEmails(mappedEmails);
        setLoading(false);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-6 h-full flex flex-col max-h-[calc(100vh-4rem)]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Inbox</h1>
          <p className="text-muted-foreground mt-1">Manage and monitor AI processing.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search emails..."
              className="pl-8 w-full sm:w-[300px] bg-card border-border"
            />
          </div>
          <Button variant="outline" size="icon" className="shrink-0 border-border">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl shadow-sm flex-1 overflow-hidden flex flex-col">
        <div className="px-4 py-3 border-b border-border bg-secondary/10 flex items-center justify-between text-xs font-medium text-muted-foreground uppercase tracking-wider">
          <div className="flex items-center gap-4">
            <div className="w-2" />
            <div className="w-1/4 min-w-[150px]">Sender</div>
            <div>Subject</div>
          </div>
          <div className="hidden lg:flex items-center gap-2 w-[220px]">
            <div className="w-[60px]">Category</div>
            <div className="w-[48px] text-right">Conf</div>
            <div className="w-[60px] pl-2">Status</div>
          </div>
          <div className="w-20 text-right">Received</div>
        </div>
        
        <div className="overflow-y-auto flex-1">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
              <p>Loading emails...</p>
            </div>
          ) : emails.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
              <p className="text-lg font-medium text-foreground">Your inbox is clear.</p>
              <p>All emails have been processed.</p>
            </div>
          ) : (
            emails.map((email) => (
              <EmailRow key={email.id} email={email} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
