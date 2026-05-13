-- Repair knowledge base table for vector similarity search (Repair Assistant module)
-- Requires the pgvector extension available on Supabase Pro/paid plans.
-- Run this migration in your Supabase SQL editor or via supabase db push.

-- Enable pgvector if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Repair knowledge table: stores embedded repair knowledge for RAG
CREATE TABLE IF NOT EXISTS public.repair_knowledge (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type text NOT NULL,            -- 'obd_code' | 'vehicle_issue' | 'procedure' | 'manual'
  vehicle_make  text,
  vehicle_model text,
  vehicle_year  text,
  obd_code      text,
  content       text NOT NULL,          -- the text that was embedded
  metadata      jsonb DEFAULT '{}',
  embedding     vector(768),            -- text-embedding-004 output dimension
  created_at    timestamptz DEFAULT now()
);

-- Index for fast cosine similarity search
CREATE INDEX IF NOT EXISTS repair_knowledge_embedding_idx
  ON public.repair_knowledge
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- RPC function for similarity search (called from Python via supabase.rpc)
CREATE OR REPLACE FUNCTION match_repair_knowledge(
  query_embedding vector(768),
  match_count     int DEFAULT 5
)
RETURNS TABLE (
  id          uuid,
  source_type text,
  vehicle_make  text,
  vehicle_model text,
  obd_code      text,
  content       text,
  metadata      jsonb,
  similarity    float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    rk.id,
    rk.source_type,
    rk.vehicle_make,
    rk.vehicle_model,
    rk.obd_code,
    rk.content,
    rk.metadata,
    1 - (rk.embedding <=> query_embedding) AS similarity
  FROM public.repair_knowledge rk
  ORDER BY rk.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Row-level security: allow authenticated users to read
ALTER TABLE public.repair_knowledge ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated read"
  ON public.repair_knowledge
  FOR SELECT
  TO authenticated
  USING (true);

-- Service role can insert (used by seed script)
CREATE POLICY "Allow service role insert"
  ON public.repair_knowledge
  FOR INSERT
  TO service_role
  WITH CHECK (true);
