import React, { useEffect, useState } from "react";
import { aiApi } from "@/features/ai/api";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export function ApprovalsList() {
  const [approvals, setApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState<string | null>(null);

  const fetchApprovals = async () => {
    try {
      const res = await aiApi.listApprovals() as { approvals: any[] };
      setApprovals(res.approvals || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleResolve = async (id: string, status: string) => {
    setResolving(id);
    const reason = status === "REJECTED" ? prompt("Please provide a reason for rejection:") : "Approved by human";
    
    if (status === "REJECTED" && !reason) {
      setResolving(null);
      return;
    }

    try {
      await aiApi.resolveApproval(id, status, "current_user", reason || undefined);
      await fetchApprovals();
    } finally {
      setResolving(null);
    }
  };

  if (loading) return <div className="text-slate-400">Loading approvals...</div>;
  if (approvals.length === 0) return <div className="text-slate-400">No pending approvals.</div>;

  return (
    <div className="space-y-4">
      {approvals.map(approval => (
        <div key={approval.id} className="card p-4 flex items-center justify-between border-l-4 border-l-amber-500">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-slate-200">Execution: {approval.execution_id.substring(0,8)}</span>
              <Badge variant={approval.status === "PENDING" ? "warning" : approval.status === "APPROVED" ? "success" : "error"}>
                {approval.status}
              </Badge>
              <Badge variant="outline">{approval.risk_level}</Badge>
            </div>
            <p className="text-slate-400 text-sm">Action requested: <span className="font-mono text-blue-400">{approval.action}</span></p>
          </div>
          
          {approval.status === "PENDING" && (
            <div className="flex gap-2">
              <Button 
                variant="secondary" 
                className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                onClick={() => handleResolve(approval.id, "REJECTED")}
                disabled={resolving === approval.id}
              >
                Reject
              </Button>
              <Button 
                variant="primary"
                onClick={() => handleResolve(approval.id, "APPROVED")}
                disabled={resolving === approval.id}
              >
                Approve
              </Button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
