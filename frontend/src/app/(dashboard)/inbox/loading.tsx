import { Skeleton } from "@/components/ui/skeleton";

export default function InboxLoading() {
  return (
    <div className="space-y-6 h-full flex flex-col max-h-[calc(100vh-4rem)] animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Skeleton className="h-9 w-32 mb-2" />
          <Skeleton className="h-5 w-64" />
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="h-10 w-full sm:w-[300px] rounded-md" />
          <Skeleton className="h-10 w-10 rounded-md" />
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl shadow-sm flex-1 overflow-hidden flex flex-col">
        <div className="px-4 py-3 border-b border-border bg-secondary/10 flex items-center justify-between">
          <Skeleton className="h-4 w-full max-w-sm" />
        </div>
        
        <div className="overflow-hidden flex-1 divide-y divide-border">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="flex items-center gap-4 px-4 py-3">
              <Skeleton className="w-2 h-2 rounded-full shrink-0" />
              <div className="w-1/4 min-w-[150px] shrink-0">
                <Skeleton className="h-4 w-3/4" />
              </div>
              <div className="flex-1 min-w-0">
                <Skeleton className="h-4 w-1/2 mb-1" />
                <Skeleton className="h-3 w-5/6" />
              </div>
              <div className="hidden lg:flex shrink-0 items-center gap-2 w-[220px]">
                <Skeleton className="h-5 w-16 rounded-full" />
                <Skeleton className="h-4 w-8" />
                <Skeleton className="h-5 w-16 rounded-full" />
              </div>
              <Skeleton className="w-20 h-4 shrink-0" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
