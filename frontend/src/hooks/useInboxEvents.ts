"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { API_BASE_URL } from "@/lib/api/client";

export interface InboxEvent {
  type: string;
  email_id?: number;
  status?: string;
  timestamp: Date;
}

/**
 * Hook that listens to the /integrations/inbox/stream SSE endpoint.
 * When a new email is ingested by the backend, this fires `onNewEmail`
 * so the inbox page can auto-refresh without a manual reload.
 */
export function useInboxSSE(onNewEmail?: () => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<InboxEvent | null>(null);
  const callbackRef = useRef(onNewEmail);
  callbackRef.current = onNewEmail;

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("inboxpilot_token")
        : null;

    if (!token) return;

    // The SSE endpoint requires auth — pass token as query param
    // since EventSource doesn't support custom headers.
    const sseUrl = `${API_BASE_URL}/integrations/inbox/stream?token=${encodeURIComponent(token)}`;

    let eventSource: EventSource | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout>;
    let destroyed = false;

    const connect = () => {
      if (destroyed) return;

      try {
        eventSource = new EventSource(sseUrl);

        eventSource.addEventListener("connected", () => {
          setIsConnected(true);
        });

        eventSource.addEventListener("inbox_update", (event) => {
          try {
            const data = JSON.parse(event.data);
            const inboxEvent: InboxEvent = {
              type: data.type,
              email_id: data.email_id,
              status: data.status,
              timestamp: new Date(),
            };
            setLastEvent(inboxEvent);

            // Trigger the refresh callback
            if (callbackRef.current) {
              callbackRef.current();
            }
          } catch (e) {
            console.error("Failed to parse inbox SSE message", e);
          }
        });

        eventSource.addEventListener("ping", () => {
          // Keep-alive, nothing to do
        });

        eventSource.onerror = () => {
          setIsConnected(false);
          eventSource?.close();
          // Reconnect after 5 seconds
          if (!destroyed) {
            reconnectTimeout = setTimeout(connect, 5000);
          }
        };
      } catch {
        setIsConnected(false);
        if (!destroyed) {
          reconnectTimeout = setTimeout(connect, 5000);
        }
      }
    };

    connect();

    return () => {
      destroyed = true;
      if (eventSource) {
        eventSource.close();
      }
      clearTimeout(reconnectTimeout);
    };
  }, []);

  return { lastEvent, isConnected };
}
