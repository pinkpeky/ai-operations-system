import { conversationClient, defaultConversationSettings, type ConversationSettings } from "./conversationClient";

export type KnowledgeDocument = {
  id?: string;
  source_id?: string;
  source_name?: string;
  source_type?: string;
  filename?: string;
  collection_name?: string;
  status?: string;
  ingest_status?: string;
  error_message?: string | null;
  metadata?: Record<string, unknown>;
  chunk_count?: number;
  created_at?: string;
  updated_at?: string;
};

export type KnowledgeUploadPayload = {
  file: File;
  collectionName?: string;
  duplicateStrategy?: "skip" | "force_reingest";
};

export type KnowledgeUploadResponse = {
  filename: string;
  file_type: string;
  file_size: number;
  file_hash: string;
  collection_name: string;
  source_id: string;
  document_id?: string | null;
  version?: number | null;
  chunk_count: number;
  chunk_ids: string[];
  ingest_status: string;
  ingest_error?: string | null;
  skipped_duplicate: boolean;
  metadata?: Record<string, unknown>;
};

export type KnowledgeSearchMode = "dense" | "keyword" | "hybrid";

export type KnowledgeSearchResult = {
  id: string;
  text: string;
  similarity_score?: number;
  rerank_score?: number | null;
  dense_score?: number | null;
  keyword_score?: number | null;
  hybrid_score?: number | null;
  metadata?: Record<string, unknown>;
  chunk_index?: number | null;
};

export type KnowledgeSearchResponse = {
  collection_name: string;
  query: string;
  search_mode: KnowledgeSearchMode;
  items: KnowledgeSearchResult[];
};

async function requestJson<T>(
  path: string,
  init?: RequestInit,
  settings: ConversationSettings = defaultConversationSettings,
): Promise<T> {
  const response = await fetch(`${conversationClient.normalizeApiBase(settings.aiServerUrl)}${path}`, {
    ...init,
    headers: {
      "X-Workspace-Id": settings.workspaceId,
      "X-User-Id": settings.userId,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Knowledge base request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export const knowledgeBaseClient = {
  documents: (settings?: ConversationSettings) =>
    requestJson<{ items: KnowledgeDocument[] }>("/documents", {}, settings),
  uploadFile: (payload: KnowledgeUploadPayload, settings?: ConversationSettings) => {
    const form = new FormData();
    form.set("file", payload.file);
    form.set("duplicate_strategy", payload.duplicateStrategy ?? "skip");
    form.set("chunk_size", "500");
    form.set("chunk_overlap", "50");
    if (payload.collectionName) {
      form.set("collection_name", payload.collectionName);
    }
    return requestJson<KnowledgeUploadResponse>("/files/upload", { method: "POST", body: form }, settings);
  },
  ingestText: (
    payload: {
      text: string;
      sourceName?: string;
      sourceId?: string;
      collectionName?: string;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<Record<string, unknown>>(
      "/rag/ingest",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: payload.text,
          source_name: payload.sourceName || undefined,
          source_id: payload.sourceId || undefined,
          source_type: "text",
          collection_name: payload.collectionName || undefined,
          metadata: { source: "worker_console_knowledge_page" },
          chunk_size: 500,
          chunk_overlap: 50,
        }),
      },
      settings,
    ),
  reingestText: (
    payload: {
      text: string;
      sourceName?: string;
      sourceId: string;
      collectionName?: string;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<Record<string, unknown>>(
      "/documents/reingest",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: payload.text,
          source_name: payload.sourceName || undefined,
          source_id: payload.sourceId,
          source_type: "text",
          collection_name: payload.collectionName || undefined,
          metadata: { source: "worker_console_knowledge_page" },
          chunk_size: 500,
          chunk_overlap: 50,
        }),
      },
      settings,
    ),
  search: (
    payload: {
      query: string;
      collectionName?: string;
      searchMode?: KnowledgeSearchMode;
      topK?: number;
      sourceId?: string;
    },
    settings?: ConversationSettings,
  ) =>
    requestJson<KnowledgeSearchResponse>(
      "/rag/search",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: payload.query,
          collection_name: payload.collectionName || undefined,
          search_mode: payload.searchMode || "hybrid",
          top_k: payload.topK ?? 5,
          source_id: payload.sourceId || undefined,
        }),
      },
      settings,
    ),
};
