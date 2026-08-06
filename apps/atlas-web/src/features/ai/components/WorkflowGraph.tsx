"use client";

import React, { useEffect, useState } from "react";
import { aiApi } from "@/features/ai/api";

interface NodeState {
  status: string;
  result?: any;
  error?: string;
}

interface DAGState {
  status: string;
  nodes: Record<string, NodeState>;
}

export function WorkflowGraph({ executionId }: { executionId: string }) {
  const [state, setState] = useState<DAGState | null>(null);

  useEffect(() => {
    const fetchState = async () => {
      try {
        const res = await aiApi.getExecutionState(executionId);
        setState(res as unknown as DAGState);
      } catch (err) {
        console.error("Failed to fetch execution state:", err);
      }
    };

    fetchState();
    const interval = setInterval(fetchState, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [executionId]);

  if (!state) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border border-dashed text-muted-foreground animate-pulse">
        Initializing Organization Workflow Graph...
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "RUNNING":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse";
      case "FAILED":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      case "WAITING_APPROVAL":
        return "bg-amber-500/10 text-amber-500 border-amber-500/20 animate-pulse";
      default:
        return "bg-secondary text-secondary-foreground border-border";
    }
  };

  return (
    <div className="w-full bg-background border border-border shadow-sm rounded-lg overflow-hidden">
      <div className="border-b bg-muted/30 p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium tracking-tight">Active Execution Graph</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Status:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(state.status)}`}>
              {state.status}
            </span>
          </div>
        </div>
      </div>
      <div className="p-6">
        <div className="flex flex-wrap gap-4">
          {Object.entries(state.nodes).map(([nodeId, nodeState]) => (
            <div
              key={nodeId}
              className={`flex flex-col items-start p-4 rounded-xl border ${getStatusColor(nodeState.status)} transition-all duration-300 min-w-[200px] shadow-sm`}
            >
              <div className="flex justify-between w-full mb-2">
                <span className="font-mono text-sm font-bold tracking-wide">{nodeId}</span>
                <span className="text-[10px] uppercase tracking-wider font-bold opacity-70">
                  {nodeState.status}
                </span>
              </div>
              {nodeState.error && (
                <div className="text-xs text-red-400 mt-2 bg-red-500/10 p-2 rounded w-full">
                  {nodeState.error}
                </div>
              )}
            </div>
          ))}
          {Object.keys(state.nodes).length === 0 && (
            <div className="text-sm text-muted-foreground w-full text-center p-8">
              No nodes have started executing yet...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
