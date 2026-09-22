import { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, User, BrainCircuit, ListTodo, ShieldCheck, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { WorkflowTimeline, TimelineStep } from "@/components/inbox/WorkflowTimeline";

export const metadata: Metadata = {
  title: "Email Details | InboxPilot",
};

export default async function EmailDetailPage({ params }: { params: { id: string } }) {
  // Mock data
  const email = {
    id: params.id,
    sender: "Alex from Acme Corp <alex@acme.com>",
    recipients: ["jane@example.com"],
    subject: "Q3 Planning Meeting",
    body: "Hi team,\n\nLet's sync up on the Q3 planning. I was thinking tomorrow at 2 PM. Let me know if that works for you.\n\nBest,\nAlex",
    receivedAt: new Date("2026-09-21T10:00:00Z"),
    category: "MEETING",
    confidence: 98,
    reasoning: "The email explicitly suggests a time for a 'sync up' and 'planning', which indicates a meeting.",
    action: "CREATE_CALENDAR_EVENT",
    actionParameters: {
      title: "Q3 Planning Meeting with Alex",
      time: "Tomorrow at 2:00 PM",
      participants: "alex@acme.com",
    },
    actionReasoning: "A meeting time was proposed. Automatically creating a calendar event saves time.",
    risk: "MEDIUM",
  };

  const workflowSteps: TimelineStep[] = [
    { id: "1", title: "Received", status: "COMPLETED", description: "Email ingested via Gmail API" },
    { id: "2", title: "Classified", status: "COMPLETED", description: "Category: MEETING (98% confidence)" },
    { id: "3", title: "Planned", status: "COMPLETED", description: "Action: CREATE_CALENDAR_EVENT" },
    { id: "4", title: "Grounded", status: "COMPLETED", description: "Parameters extracted: Tomorrow 2 PM" },
    { id: "5", title: "Safety Checked", status: "COMPLETED", description: "Risk assessed as MEDIUM" },
    { id: "6", title: "Approval Requested", status: "IN_PROGRESS", description: "Waiting for user approval" },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Link href="/inbox">
          <Button variant="ghost" size="icon" className="rounded-full">
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Email Details</h1>
          <p className="text-muted-foreground text-sm">ID: {email.id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Email Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
            <div className="space-y-2 border-b border-border pb-4">
              <h2 className="text-xl font-semibold text-foreground">{email.subject}</h2>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <User className="w-4 h-4" />
                <span>From: <span className="font-medium text-foreground">{email.sender}</span></span>
              </div>
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 opacity-0" />
                  <span>To: {email.recipients.join(", ")}</span>
                </div>
                <span>{email.receivedAt.toLocaleString()}</span>
              </div>
            </div>
            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap text-foreground">
              {email.body}
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-primary" />
              AI Analysis
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-secondary/30 p-4 rounded-lg border border-border space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Classification</div>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-blue-500 border-blue-500/20 bg-blue-500/10">
                    {email.category}
                  </Badge>
                  <span className="text-sm font-bold text-foreground">{email.confidence}%</span>
                </div>
                <p className="text-sm text-muted-foreground mt-2">{email.reasoning}</p>
              </div>

              <div className="bg-secondary/30 p-4 rounded-lg border border-border space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Action Plan</div>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-primary border-primary/20 bg-primary/10">
                    {email.action}
                  </Badge>
                  <div className="flex items-center gap-1 text-sm font-bold text-orange-500">
                    <ShieldCheck className="w-4 h-4" /> {email.risk}
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-2">{email.actionReasoning}</p>
              </div>
            </div>

            <div className="bg-secondary/30 p-4 rounded-lg border border-border space-y-3">
              <div className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <ListTodo className="w-4 h-4" /> Grounded Parameters
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {Object.entries(email.actionParameters).map(([key, value]) => (
                  <div key={key} className="bg-background rounded px-3 py-2 text-sm border border-border">
                    <span className="font-semibold text-foreground mr-2">{key}:</span>
                    <span className="text-muted-foreground">{value as string}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Workflow Timeline & Actions */}
        <div className="space-y-6">
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold flex items-center gap-2 mb-6">
              <FileText className="w-5 h-5 text-primary" />
              Workflow Timeline
            </h3>
            <WorkflowTimeline steps={workflowSteps} />
          </div>

          <div className="flex flex-col gap-3">
            <Button className="w-full bg-green-500 hover:bg-green-600 text-white">
              Approve Action
            </Button>
            <Button variant="outline" className="w-full text-destructive border-border hover:bg-destructive/10">
              Reject Action
            </Button>
            <Link href="/audit" className="w-full">
              <Button variant="ghost" className="w-full">View Audit Logs</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
