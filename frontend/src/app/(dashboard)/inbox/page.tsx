"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Search, Filter, RefreshCw, X, ChevronLeft, ChevronRight, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmailRow, EmailData } from "@/components/inbox/EmailRow";
import { Skeleton } from "@/components/ui/skeleton";
import { emailsApi, EmailQueryParams } from "@/lib/api/emails";
import { useInboxSSE } from "@/hooks/useInboxEvents";

export default function InboxPage() {
  const [emails, setEmails] = useState<EmailData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [total, setTotal] = useState(0);

  // States for query
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  
  // Active applied filters
  const [category, setCategory] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [confidence, setConfidence] = useState<string>(""); // "high", "medium", "low"
  const [dateRange, setDateRange] = useState<string>(""); // "today", "7d", "30d"

  // Draft filters for the popover
  const [draftCategory, setDraftCategory] = useState<string>("");
  const [draftStatus, setDraftStatus] = useState<string>("");
  const [draftConfidence, setDraftConfidence] = useState<string>("");
  const [draftDateRange, setDraftDateRange] = useState<string>("");
  
  const [sortBy, setSortBy] = useState<string>("received_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  
  const [page, setPage] = useState(1);
  const limit = 50;
  
  const [showFilters, setShowFilters] = useState(false);
  
  const filterRef = useRef<HTMLDivElement>(null);

  // Close filters when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as HTMLElement;
      if (target && target.tagName && target.tagName.toLowerCase() === 'option') {
        return;
      }
      if (filterRef.current && !filterRef.current.contains(target as Node)) {
        setShowFilters(false);
      }
    }
    document.addEventListener("pointerdown", handleClickOutside);
    return () => document.removeEventListener("pointerdown", handleClickOutside);
  }, []);

  // Sync drafts when opening filters
  useEffect(() => {
    if (showFilters) {
      setDraftCategory(category);
      setDraftStatus(status);
      setDraftConfidence(confidence);
      setDraftDateRange(dateRange);
    }
  }, [showFilters, category, status, confidence, dateRange]);

  // Debounce search
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1); // Reset page on new search
    }, 500);
    return () => clearTimeout(handler);
  }, [search]);

  const fetchEmails = useCallback((isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    let confMin: number | undefined;
    let confMax: number | undefined;
    if (confidence === "high") { confMin = 90; }
    else if (confidence === "medium") { confMin = 70; confMax = 89; }
    else if (confidence === "low") { confMax = 69; }

    let dateFrom: string | undefined;
    if (dateRange) {
      const now = new Date();
      if (dateRange === "today") {
        now.setHours(0, 0, 0, 0);
      } else if (dateRange === "7d") {
        now.setDate(now.getDate() - 7);
      } else if (dateRange === "30d") {
        now.setDate(now.getDate() - 30);
      }
      dateFrom = now.toISOString();
    }

    const params: EmailQueryParams = {
      search: debouncedSearch,
      category: category || undefined,
      status: status || undefined,
      confidence_min: confMin,
      confidence_max: confMax,
      date_from: dateFrom,
      sort_by: sortBy,
      sort_order: sortOrder,
      page,
      limit,
    };

    emailsApi.getMany(params)
      .then((data: any) => {
        const items = data.items || [];
        const mappedEmails: EmailData[] = items.map((email: any) => ({
          id: String(email.id),
          sender: email.sender,
          subject: email.subject || "(No Subject)",
          preview: email.body ? email.body.substring(0, 100) : "",
          category: email.category || ("" as any), // Passed as empty string for Unclassified
          confidence: email.status === "PENDING" ? null : Math.round((email.classification_confidence || 0) * 100),
          status: email.status,
          timestamp: email.received_at,
          isUnread: false
        }));
        setEmails(mappedEmails);
        setTotal(data.total || 0);
        setLoading(false);
        setRefreshing(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
        setRefreshing(false);
      });
  }, [debouncedSearch, category, status, confidence, dateRange, sortBy, sortOrder, page]);

  useEffect(() => {
    fetchEmails();
  }, [fetchEmails]);

  // Listen for real-time SSE updates
  useInboxSSE(fetchEmails);

  const totalPages = Math.ceil(total / limit) || 1;

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("desc");
    }
  };

  const SortIcon = ({ column }: { column: string }) => {
    if (sortBy !== column) return null;
    return sortOrder === "asc" ? <ChevronUp className="w-3 h-3 inline-block ml-1" /> : <ChevronDown className="w-3 h-3 inline-block ml-1" />;
  };

  const hasFilters = category || status || confidence || dateRange;

  const clearFilters = (e?: React.MouseEvent) => {
    if (e) e.preventDefault();
    setCategory("");
    setStatus("");
    setConfidence("");
    setDateRange("");
    setDraftCategory("");
    setDraftStatus("");
    setDraftConfidence("");
    setDraftDateRange("");
    setPage(1);
    setShowFilters(false);
  };

  const applyFilters = (e?: React.MouseEvent) => {
    if (e) e.preventDefault();
    setCategory(draftCategory);
    setStatus(draftStatus);
    setConfidence(draftConfidence);
    setDateRange(draftDateRange);
    setPage(1);
    setShowFilters(false);
  };

  return (
    <div className="space-y-4 relative">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Inbox</h1>
          <p className="text-muted-foreground mt-1">Manage and monitor AI processing.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search emails..."
              className="pl-8 pr-8 w-full sm:w-[300px] bg-card border-border"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button 
                onClick={() => setSearch("")}
                className="absolute right-2.5 top-2.5 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          
          <div className="relative" ref={filterRef}>
            <Button 
              variant="outline" 
              className={`shrink-0 border-border ${hasFilters ? 'bg-primary/10 text-primary border-primary/20' : ''}`}
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
              {hasFilters && <span className="ml-1 w-2 h-2 rounded-full bg-primary" />}
            </Button>
            
            {showFilters && (
              <div className="absolute right-0 top-full mt-2 w-72 bg-card border border-border shadow-lg rounded-xl p-4 z-50 flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm">Filters</h3>
                  {hasFilters && (
                    <button onClick={clearFilters} className="text-xs text-muted-foreground hover:text-foreground">Clear all</button>
                  )}
                </div>
                
                <div className="space-y-3">
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground">Category</label>
                    <select 
                      className="w-full text-sm rounded-md border border-border bg-background p-2"
                      value={draftCategory}
                      onChange={(e) => setDraftCategory(e.target.value)}
                    >
                      <option value="">All Categories</option>
                      <option value="BILL">Bill</option>
                      <option value="MEETING">Meeting</option>
                      <option value="SPAM">Spam</option>
                      <option value="FORM">Form</option>
                      <option value="REMINDER">Reminder</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>
                  
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground">Status</label>
                    <select 
                      className="w-full text-sm rounded-md border border-border bg-background p-2"
                      value={draftStatus}
                      onChange={(e) => setDraftStatus(e.target.value)}
                    >
                      <option value="">All Statuses</option>
                      <option value="PENDING">Pending</option>
                      <option value="PROCESSING">Processing</option>
                      <option value="COMPLETED">Completed</option>
                      <option value="FAILED">Failed</option>
                      <option value="APPROVAL_PENDING">Approval Pending</option>
                      <option value="EXECUTED">Executed</option>
                      <option value="IMPORTED">Imported</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground">Confidence</label>
                    <select 
                      className="w-full text-sm rounded-md border border-border bg-background p-2"
                      value={draftConfidence}
                      onChange={(e) => setDraftConfidence(e.target.value)}
                    >
                      <option value="">All</option>
                      <option value="high">High (&ge; 90%)</option>
                      <option value="medium">Medium (70-89%)</option>
                      <option value="low">Low (&lt; 70%)</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground">Received Date</label>
                    <select 
                      className="w-full text-sm rounded-md border border-border bg-background p-2"
                      value={draftDateRange}
                      onChange={(e) => setDraftDateRange(e.target.value)}
                    >
                      <option value="">All time</option>
                      <option value="today">Today</option>
                      <option value="7d">Last 7 days</option>
                      <option value="30d">Last 30 days</option>
                    </select>
                  </div>
                  
                  <div className="pt-2 flex items-center justify-between gap-2 border-t border-border mt-2">
                    <Button type="button" variant="ghost" size="sm" onClick={clearFilters} className="text-muted-foreground">
                      Clear Filters
                    </Button>
                    <Button type="button" size="sm" onClick={applyFilters}>
                      Apply Filters
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <Button variant="outline" size="icon" className="shrink-0 border-border" onClick={() => fetchEmails(true)} disabled={refreshing}>
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {hasFilters && (
        <div className="flex flex-wrap gap-2 shrink-0">
          {category && (
            <span className="inline-flex items-center gap-1 bg-secondary px-2 py-1 rounded-full text-xs font-medium border border-border">
              Category: {category}
              <button onClick={() => { setCategory(""); setPage(1); }} className="hover:text-foreground text-muted-foreground"><X className="w-3 h-3" /></button>
            </span>
          )}
          {status && (
            <span className="inline-flex items-center gap-1 bg-secondary px-2 py-1 rounded-full text-xs font-medium border border-border">
              Status: {status}
              <button onClick={() => { setStatus(""); setPage(1); }} className="hover:text-foreground text-muted-foreground"><X className="w-3 h-3" /></button>
            </span>
          )}
          {confidence && (
            <span className="inline-flex items-center gap-1 bg-secondary px-2 py-1 rounded-full text-xs font-medium border border-border">
              Conf: {confidence}
              <button onClick={() => { setConfidence(""); setPage(1); }} className="hover:text-foreground text-muted-foreground"><X className="w-3 h-3" /></button>
            </span>
          )}
          {dateRange && (
            <span className="inline-flex items-center gap-1 bg-secondary px-2 py-1 rounded-full text-xs font-medium border border-border">
              Date: {dateRange}
              <button onClick={() => { setDateRange(""); setPage(1); }} className="hover:text-foreground text-muted-foreground"><X className="w-3 h-3" /></button>
            </span>
          )}
        </div>
      )}

      <div className="bg-card border border-border rounded-xl shadow-sm flex flex-col">
        <div className="px-4 py-3 border-b border-border bg-secondary/10 flex flex-col lg:flex-row lg:items-center gap-2 lg:gap-4 text-xs font-medium text-muted-foreground uppercase tracking-wider shrink-0">
          <div className="flex items-center gap-4 flex-1 min-w-0">
            <div className="w-2 shrink-0 hidden lg:block" />
            <div 
              className="w-1/4 min-w-[120px] max-w-[200px] cursor-pointer hover:text-foreground select-none flex items-center shrink-0"
              onClick={() => handleSort("sender")}
            >
              Sender <SortIcon column="sender" />
            </div>
            <div className="flex-1 min-w-0 truncate">Subject</div>
          </div>
          
          <div className="hidden lg:flex items-center justify-end gap-4 w-[380px] shrink-0">
            <div className="flex items-center gap-2 w-[260px] shrink-0">
              <div 
                className="w-[70px] cursor-pointer hover:text-foreground select-none flex items-center justify-center shrink-0"
                onClick={() => handleSort("category")}
              >
                Category <SortIcon column="category" />
              </div>
              <div 
                className="w-[60px] cursor-pointer hover:text-foreground select-none flex items-center justify-center shrink-0"
                onClick={() => handleSort("classification_confidence")}
              >
                Conf <SortIcon column="classification_confidence" />
              </div>
              <div 
                className="w-[100px] cursor-pointer hover:text-foreground select-none flex items-center justify-center shrink-0"
                onClick={() => handleSort("status")}
              >
                Status <SortIcon column="status" />
              </div>
            </div>
            <div 
              className="w-[100px] text-center cursor-pointer hover:text-foreground select-none flex items-center justify-center shrink-0"
              onClick={() => handleSort("received_at")}
            >
              Received <SortIcon column="received_at" />
            </div>
          </div>
        </div>
        
        <div>
          {loading ? (
            <div className="divide-y divide-border">
              {[...Array(10)].map((_, i) => (
                <div key={i} className="px-4 py-4 flex flex-col lg:flex-row lg:items-center gap-2 lg:gap-4 animate-in fade-in duration-500">
                  <div className="flex items-center gap-4 flex-1 min-w-0 w-full lg:w-auto">
                    <div className="w-2 shrink-0 hidden lg:block" />
                    <div className="w-1/4 min-w-[120px] max-w-[200px] shrink-0">
                      <Skeleton className="h-5 w-3/4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <Skeleton className="h-5 w-1/2" />
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between lg:justify-end gap-2 lg:gap-4 w-full lg:w-[380px] shrink-0 mt-2 lg:mt-0">
                    <div className="flex items-center gap-2 lg:w-[260px] lg:justify-start shrink-0">
                      <div className="lg:w-[70px] flex lg:justify-center"><Skeleton className="h-6 w-[60px] rounded-full" /></div>
                      <div className="lg:w-[60px] flex lg:justify-center"><Skeleton className="h-5 w-[40px]" /></div>
                      <div className="lg:w-[100px] flex lg:justify-center"><Skeleton className="h-6 w-[80px] rounded-full" /></div>
                    </div>
                    <div className="lg:w-[100px] flex lg:justify-center shrink-0 text-center">
                      <Skeleton className="h-5 w-[60px]" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : emails.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
              <p className="text-lg font-medium text-foreground">
                {debouncedSearch || hasFilters ? "No matches found." : "Your inbox is clear."}
              </p>
              <p>{debouncedSearch || hasFilters ? "Try adjusting your filters or search." : "All emails have been processed."}</p>
              {(debouncedSearch || hasFilters) && (
                <Button variant="outline" className="mt-4" onClick={() => {setSearch(""); clearFilters();}}>
                  Clear all filters
                </Button>
              )}
            </div>
          ) : (
            emails.map((email) => (
              <EmailRow key={email.id} email={email} />
            ))
          )}
        </div>
        
        {!loading && emails.length > 0 && (
          <div className="px-4 py-3 border-t border-border bg-card flex items-center justify-between text-sm shrink-0">
            <div className="text-muted-foreground">
              Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, total)} of {total} results
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page <= 1}
              >
                <ChevronLeft className="w-4 h-4 mr-1" /> Prev
              </Button>
              <span className="text-sm px-2 text-muted-foreground">Page {page} of {totalPages}</span>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page >= totalPages}
              >
                Next <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
