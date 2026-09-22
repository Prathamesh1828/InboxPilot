"use client";

import { useEffect, useState } from "react";

export type SSEEvent = 
  | "EMAIL_RECEIVED" 
  | "CLASSIFICATION_COMPLETED" 
  | "PLAN_CREATED" 
  | "APPROVAL_CREATED" 
  | "APPROVAL_APPROVED" 
  | "EXECUTION_STARTED" 
  | "EXECUTION_COMPLETED" 
  | "EXECUTION_FAILED";

export interface InboxEvent {
  type: SSEEvent;
  data: unknown;
  timestamp: Date;
}

export function useInboxEvents() {
  const [lastEvent, setLastEvent] = useState<InboxEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Determine the SSE URL based on environment
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const sseUrl = `${baseUrl}/events`;
    
    let eventSource: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const connect = () => {
      try {
        eventSource = new EventSource(sseUrl);

        eventSource.onopen = () => {
          setIsConnected(true);
        };

        eventSource.onmessage = (event) => {
          try {
            const parsedData = JSON.parse(event.data);
            setLastEvent({
              type: parsedData.type as SSEEvent,
              data: parsedData.payload,
              timestamp: new Date(),
            });
          } catch (e) {
            console.error("Failed to parse SSE message", e);
          }
        };

        eventSource.onerror = () => {
          setIsConnected(false);
          eventSource?.close();
          // Attempt to reconnect after 3 seconds
          reconnectTimeout = setTimeout(connect, 3000);
        };
      } catch (_error) {
        setIsConnected(false);
      }
    };

    // In a real scenario, uncomment the connect() call.
    // For now, since backend might not exist/support SSE yet, we won't connect on mount to avoid infinite errors.
    // connect();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
      clearTimeout(reconnectTimeout);
    };
  }, []);

  return { lastEvent, isConnected };
}
