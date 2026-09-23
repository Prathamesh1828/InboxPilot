"use client";

import { useAuth } from "@/contexts/AuthContext";

export function Greeting() {
  const { user } = useAuth();
  
  return (
    <h1 className="text-3xl font-bold tracking-tight text-foreground">
      Good morning{user?.name ? `, ${user.name.split(" ")[0]}` : ""}
    </h1>
  );
}
