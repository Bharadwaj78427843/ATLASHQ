export interface KnowledgeSource {
  id: string;
  workspace_id: string;
  project_id: string | null;
  name: string;
  source_type: string;
  storage_path: string | null;
  status: string;
  size_bytes: number | null;
  metadata_json: Record<string, unknown> | null;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface IndexJob {
  id: string;
  source_id: string;
  status: string;
  progress: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface SearchResultSnippet {
  source_id: string;
  source_name: string;
  document_id: string;
  filename: string;
  content: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultSnippet[];
}
