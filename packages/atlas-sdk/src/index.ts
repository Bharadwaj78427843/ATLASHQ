import { HealthResponse } from "@atlas/types";

export class AtlasClient {
  constructor(private baseUrl: string) {}

  async checkHealth(): Promise<HealthResponse> {
    const res = await fetch(`${this.baseUrl}/health`);
    return res.json();
  }
}
