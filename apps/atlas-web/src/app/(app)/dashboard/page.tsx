"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { MetricCard } from "@/components/ui/MetricCard";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Button } from "@/components/ui/Button";
import { Folder, GitBranch, Rocket, Bot, AlertCircle, UploadCloud, FileCode2, BookText, ScrollText, Database as DatabaseIcon, Zap, Network, Box } from "lucide-react";

// ─── STATIC DATA ─────────────────────────────────────────────────────────────
// Moved outside components to prevent recreation on every render

const RECENT_ACTIVITY = [
  { title: "Deployment to Production", sub: "atlas-backend", time: "2m ago", status: "success", icon: <Box className="w-3.5 h-3.5" /> },
  { title: "Push to main", sub: "atlas-frontend", time: "15m ago", status: "success", icon: <GitBranch className="w-3.5 h-3.5" /> },
  { title: "New issue created", sub: "atlas-backend", time: "1h ago", status: "error", icon: <AlertCircle className="w-3.5 h-3.5" /> },
  { title: "AI Agent completed task", sub: "Code Review", time: "2h ago", status: "success", icon: <Bot className="w-3.5 h-3.5" /> }
];

const DEPLOYMENT_TIMELINE = [
  { name: "Production", time: "2m ago", status: "Success", color: "var(--color-accent-green)" },
  { name: "Staging", time: "15m ago", status: "Success", color: "var(--color-accent-green)" },
  { name: "Preview", sub: "v2.4.0", status: "Success", color: "var(--color-primary-light)" },
  { name: "Development", time: "2h ago", status: "Success", color: "var(--color-primary-light)" }
];

const REPO_HEALTH = [
  { label: "Code Quality", value: 96, color: "var(--color-accent-green)" },
  { label: "Test Coverage", value: 92, color: "var(--color-accent-green)" },
  { label: "Security", value: 99, color: "var(--color-accent-green)" },
  { label: "Performance", value: 97, color: "var(--color-accent-green)" }
];

// ─── ISOLATED COMPONENTS ─────────────────────────────────────────────────────

// 1. AI Command Input
// Isolating state here ensures typing only re-renders this tiny input box, not the huge dashboard DOM.
const AiCommandInput = React.memo(() => {
  const [prompt, setPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const [isAsking, setIsAsking] = useState(false);

  const handleAskAtlas = async () => {
    if (!prompt.trim()) return;
    setIsAsking(true);
    try {
      const { aiApi } = await import("@/features/ai");
      const res = await aiApi.chat(prompt);
      setAiResponse(res.response);
      setPrompt("");
    } catch (err) {
      console.error("AI Error:", err);
      setAiResponse("Sorry, Atlas encountered an error.");
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <GlassPanel className="p-1 mb-8" glow>
      <div className="p-4 border-b border-[var(--color-border-subtle)] flex items-center gap-2">
        <span className="text-[var(--color-primary-base)]">✦</span>
        <span className="text-sm font-semibold text-[var(--color-text-primary)]">Ask Atlas anything</span>
      </div>
      <div className="p-4">
        <textarea 
          className="w-full bg-transparent border-none outline-none text-base text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] resize-none h-16"
          placeholder="What do you want to build, fix, or analyze?"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleAskAtlas();
            }
          }}
        />
        {aiResponse && (
          <div className="mt-4 p-4 rounded bg-[rgba(124,58,237,0.1)] border border-[rgba(124,58,237,0.2)] text-sm">
            <div className="font-semibold text-[var(--color-primary-light)] mb-1">Atlas says:</div>
            <div className="whitespace-pre-wrap">{aiResponse}</div>
          </div>
        )}
        <div className="flex items-center justify-between mt-2">
          <div className="flex gap-2 flex-wrap">
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(255,255,255,0.05)] text-xs font-medium text-[var(--color-text-secondary)] transition-colors">
              <UploadCloud className="w-3.5 h-3.5" /> Upload files
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(255,255,255,0.05)] text-xs font-medium text-[var(--color-text-secondary)] transition-colors">
              <FileCode2 className="w-3.5 h-3.5" /> Attach repo
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(255,255,255,0.05)] text-xs font-medium text-[var(--color-text-secondary)] transition-colors">
              <BookText className="w-3.5 h-3.5" /> Add docs
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(255,255,255,0.05)] text-xs font-medium text-[var(--color-text-secondary)] transition-colors">
              <ScrollText className="w-3.5 h-3.5" /> Add logs
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(255,255,255,0.05)] text-xs font-medium text-[var(--color-text-secondary)] transition-colors">
              <DatabaseIcon className="w-3.5 h-3.5" /> Connect DB
            </button>
          </div>
          <Button variant="primary" size="icon" className="h-9 w-9" onClick={handleAskAtlas} disabled={isAsking}>
            {isAsking ? <span className="spinner-ring" /> : <span className="text-lg leading-none transform -rotate-45 block relative -top-0.5 -right-0.5">➤</span>}
          </Button>
        </div>
      </div>
      <div className="bg-[rgba(0,0,0,0.2)] px-4 py-3 border-t border-[var(--color-border-subtle)] flex gap-4 overflow-x-auto">
        <button className="flex items-center gap-1.5 text-[11px] font-medium text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors whitespace-nowrap">
          <Zap className="w-3 h-3" /> Analyze codebase
        </button>
        <button className="flex items-center gap-1.5 text-[11px] font-medium text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors whitespace-nowrap">
          <Network className="w-3 h-3" /> Explain architecture
        </button>
        <button className="flex items-center gap-1.5 text-[11px] font-medium text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors whitespace-nowrap">
          <AlertCircle className="w-3 h-3" /> Find bugs
        </button>
      </div>
    </GlassPanel>
  );
});
AiCommandInput.displayName = "AiCommandInput";

// 2. Metrics Grid (Memoized)
const MetricsGrid = React.memo(() => (
  <div className="grid grid-cols-5 gap-4 mb-8">
    <MetricCard title="Projects" value="8" trend="2 this week" trendDirection="up" icon={<Folder className="w-4 h-4" />} />
    <MetricCard title="Repositories" value="16" trend="3 this week" trendDirection="up" icon={<GitBranch className="w-4 h-4 text-blue-500" />} />
    <MetricCard title="Deployments" value="24" trend="6 this week" trendDirection="up" icon={<Rocket className="w-4 h-4 text-green-500" />} />
    <MetricCard title="AI Agents" value="7" trend="1 this week" trendDirection="up" icon={<Bot className="w-4 h-4 text-purple-500" />} />
    <MetricCard title="Open Issues" value="12" trend="4 this week" trendDirection="down" icon={<AlertCircle className="w-4 h-4 text-red-500" />} />
  </div>
));
MetricsGrid.displayName = "MetricsGrid";

// 3. Information Columns (Memoized)
const InfoColumns = React.memo(() => (
  <div className="grid grid-cols-3 gap-6">
    {/* Recent Activity */}
    <GlassPanel className="p-5">
      <h3 className="text-sm font-semibold mb-4 text-[var(--color-text-primary)]">Recent Activity</h3>
      <div className="space-y-4">
        {RECENT_ACTIVITY.map((act, i) => (
          <div key={i} className="flex gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${act.status === 'success' ? 'bg-[rgba(34,197,94,0.1)] text-[var(--color-accent-green)]' : 'bg-[rgba(239,68,68,0.1)] text-[var(--color-accent-red)]'}`}>
              {act.icon}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-[var(--color-text-primary)] truncate">{act.title}</p>
              <p className="text-[10px] text-[var(--color-text-secondary)]">{act.sub}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-[10px] text-[var(--color-text-muted)] mb-1">{act.time}</p>
              <div className={`w-3 h-3 rounded-full border border-[rgba(255,255,255,0.2)] ml-auto flex items-center justify-center ${act.status === 'success' ? 'text-[var(--color-accent-green)]' : 'text-[var(--color-accent-red)]'}`}>
                <span className="text-[8px]">✓</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <button className="text-xs text-[var(--color-primary-light)] mt-4 hover:underline block">View all activity →</button>
    </GlassPanel>

    {/* Deployment Timeline */}
    <GlassPanel className="p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">Deployment Timeline</h3>
        <button className="text-xs text-[var(--color-primary-light)] hover:underline">View all</button>
      </div>
      <div className="relative pl-3 space-y-6 before:absolute before:inset-0 before:ml-[15px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-[var(--color-border-subtle)]">
        {DEPLOYMENT_TIMELINE.map((dep, i) => (
          <div key={i} className="relative flex items-start gap-4">
            <div className="absolute left-0 w-2.5 h-2.5 rounded-full border-2 border-[var(--color-background)]" style={{ backgroundColor: dep.color, top: '4px' }} />
            <div className="pl-6 w-full">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-medium text-[var(--color-text-primary)]">{dep.name}</p>
                  <p className="text-[10px] text-[var(--color-text-muted)]">{dep.sub || dep.time}</p>
                </div>
                <span className="text-[10px] font-medium text-[var(--color-accent-green)] flex items-center gap-1">
                  ✓ {dep.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </GlassPanel>

    {/* Repository Health */}
    <GlassPanel className="p-5">
      <h3 className="text-sm font-semibold mb-6 text-[var(--color-text-primary)]">Repository Health</h3>
      
      <div className="mb-6">
        <div className="flex justify-between items-end mb-2">
          <span className="text-xs text-[var(--color-text-secondary)]">Overall Health</span>
          <span className="text-xl font-bold text-[var(--color-text-primary)]">98%</span>
        </div>
        <div className="w-full bg-[rgba(255,255,255,0.05)] h-2 rounded-full overflow-hidden">
          <div className="bg-[var(--color-accent-green)] h-full rounded-full" style={{ width: '98%' }} />
        </div>
      </div>

      <div className="space-y-4">
        {REPO_HEALTH.map((stat, i) => (
          <div key={i}>
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-[var(--color-text-secondary)] flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: stat.color }} />
                {stat.label}
              </span>
              <span className="font-medium text-[var(--color-text-primary)]">{stat.value}%</span>
            </div>
            <div className="w-full bg-[rgba(255,255,255,0.05)] h-1 rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${stat.value}%`, backgroundColor: stat.color }} />
            </div>
          </div>
        ))}
      </div>

      <button className="text-xs text-[var(--color-primary-light)] mt-6 hover:underline block">View full report →</button>
    </GlassPanel>
  </div>
));
InfoColumns.displayName = "InfoColumns";


// ─── MAIN PAGE COMPONENT ─────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="h-screen flex items-center justify-center bg-[var(--color-background)]">
        <span className="spinner-ring" />
      </div>
    );
  }

  const displayName = user.first_name || user.username;

  return (
    <div className="p-8">
      {/* Header Greeting */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-3 tracking-tight">
          Good morning, <span className="text-gradient">{displayName}!</span> 👋
        </h1>
        <p className="text-[var(--color-text-secondary)] text-sm mb-4">
          Atlas AI is ready to help you build, deploy, and scale.
        </p>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-[var(--radius-sm)] border border-[rgba(34,197,94,0.3)] bg-[rgba(34,197,94,0.1)] text-[var(--color-accent-green)] text-[10px] font-semibold uppercase tracking-wider">
            <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-accent-green)]" />
            Workspace: Atlas Backend
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-[var(--radius-sm)] border border-[rgba(34,197,94,0.3)] bg-[rgba(34,197,94,0.1)] text-[var(--color-accent-green)] text-[10px] font-semibold uppercase tracking-wider">
            <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-accent-green)]" />
            Environment: Production
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-[var(--radius-sm)] border border-[rgba(124,58,237,0.3)] bg-[rgba(124,58,237,0.1)] text-[var(--color-primary-light)] text-[10px] font-semibold uppercase tracking-wider">
            ✦ AI Context: Ready
          </div>
        </div>
      </div>

      <AiCommandInput />
      <MetricsGrid />
      <InfoColumns />
    </div>
  );
}
