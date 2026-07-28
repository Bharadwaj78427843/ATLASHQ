"use client";

/**
 * src/app/page.tsx
 *
 * Root page — redirects authenticated users to /dashboard,
 * and unauthenticated users to /login.
 */
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function RootPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      router.replace(user ? "/dashboard" : "/login");
    }
  }, [isLoading, user, router]);

  return (
    <div className="dashboard-loading">
      <span className="spinner-ring" />
    </div>
  );
}
