import React from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { RightPanel } from "@/components/layout/RightPanel";
import { OrganizationProvider } from "@/contexts/OrganizationContext";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <OrganizationProvider>
      <div className="flex h-screen w-full overflow-hidden bg-[var(--color-background)] text-[var(--color-text-primary)]">
        <Sidebar />
        <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
          {/* Background glow effects */}
          <div className="absolute top-0 left-1/4 w-[800px] h-[500px] bg-[rgba(124,58,237,0.15)] blur-[120px] rounded-full pointer-events-none" />
          <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-[rgba(59,130,246,0.1)] blur-[150px] rounded-full pointer-events-none" />

          <TopBar />
          
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 overflow-y-auto relative z-10">
              {children}
            </main>
            <RightPanel />
          </div>
        </div>
      </div>
    </OrganizationProvider>
  );
}
