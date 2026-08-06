"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { aiApi, SkillSummary } from "@/features/ai/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ApprovalsList } from "@/features/ai/components/ApprovalsList";
import { WorkflowGraph } from "@/features/ai/components/WorkflowGraph";

export default function AIOrganizationDashboard() {
  const [skills, setSkills] = useState<SkillSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeExecutionId, setActiveExecutionId] = useState<string | null>(null);
  const [launching, setLaunching] = useState(false);

  useEffect(() => {
    aiApi.listSkills().then((res) => {
      setSkills(res.skills);
      setLoading(false);
    });
  }, []);

  const handleLaunchWorkflow = async () => {
    setLaunching(true);
    try {
      // The Engineering Manager evaluates this dynamically.
      const res = await aiApi.executeGraph({ nodes: [
        { id: "EM", type: "SKILL", skill_id: "engineering_manager" }
      ]}, { 
        prompt: "Plan and execute the next feature increment.", 
        correlation_id: `exec-${Date.now()}` 
      });
      setActiveExecutionId(res.execution_id);
    } catch (e) {
      console.error(e);
    } finally {
      setLaunching(false);
    }
  };

  return (
    <PageLayout>
      <PageHeader 
        title="AI Engineering Organization" 
        subtitle="Manage autonomous AI engineers, view live workflows, and approve actions."
      >
        <Button variant="primary" onClick={handleLaunchWorkflow} disabled={launching}>
          {launching ? "Launching..." : "Launch Workflow"}
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 gap-8 mt-6">
        {/* Skills Catalog */}
        <section>
          <h2 className="text-xl font-semibold mb-4 text-slate-100">Organization Roster</h2>
          {loading ? (
            <div className="flex justify-center p-8"><span className="spinner-ring" /></div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {skills.filter(s => s.valid).map((skill) => (
                <div key={skill.skill_id} className="card p-4 hover:border-blue-500/50 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-slate-200">{skill.skill?.display_name}</h3>
                    <Badge variant="success">Active</Badge>
                  </div>
                  <p className="text-sm text-slate-400 h-10 overflow-hidden">{skill.skill?.description}</p>
                  <div className="mt-4 text-xs text-slate-500 font-mono">
                    {skill.skill_id} v{skill.skill?.version}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Approvals */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold mb-4 text-slate-100">Human Approval Gates</h2>
          <ApprovalsList />
        </section>

        {/* Execution Dashboard */}
        <section className="mt-8">
          <h2 className="text-xl font-semibold mb-4 text-slate-100">Live Execution Dashboard</h2>
          {activeExecutionId ? (
            <WorkflowGraph executionId={activeExecutionId} />
          ) : (
            <div className="card p-8 text-center text-slate-400">
              No active workflows. Launch a workflow to see DAG visualization.
            </div>
          )}
        </section>
      </div>
    </PageLayout>
  );
}
