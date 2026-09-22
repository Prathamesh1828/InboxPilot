import { Skeleton } from "@/components/ui/skeleton";

export default function ApprovalsLoading() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <Skeleton className="h-9 w-48 mb-2" />
        <Skeleton className="h-5 w-96" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-card border border-border rounded-xl shadow-sm overflow-hidden flex flex-col">
            <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Skeleton className="w-5 h-5 rounded-md shrink-0" />
                  <Skeleton className="h-5 w-48" />
                </div>
                <Skeleton className="h-4 w-3/4" />
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Skeleton className="h-5 w-20 rounded-full" />
                <Skeleton className="h-4 w-24" />
              </div>
            </div>

            <div className="p-5 flex-1 bg-secondary/10">
              <Skeleton className="h-4 w-32 mb-4" />
              <div className="space-y-3">
                {[...Array(3)].map((_, j) => (
                  <div key={j} className="flex flex-col sm:flex-row sm:items-center gap-2">
                    <Skeleton className="h-4 w-24 shrink-0" />
                    <Skeleton className="h-8 w-full rounded" />
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 border-t border-border bg-background flex items-center justify-between gap-4">
              <Skeleton className="h-9 w-32 rounded-md" />
              <div className="flex items-center gap-2">
                <Skeleton className="h-9 w-24 rounded-md" />
                <Skeleton className="h-9 w-36 rounded-md" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
