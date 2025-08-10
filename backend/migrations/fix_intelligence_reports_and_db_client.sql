-- Migration: Fix Intelligence Reports Schema and Database Client Issues
-- Date: 2025-01-10

-- Add missing policy_developments column to intelligence_reports table
ALTER TABLE intelligence_reports 
ADD COLUMN IF NOT EXISTS policy_developments JSONB DEFAULT '[]'::jsonb;

-- Add missing provider column to intelligence_reports table
ALTER TABLE intelligence_reports 
ADD COLUMN IF NOT EXISTS provider TEXT DEFAULT 'perplexity';

-- Add comments to describe the columns
COMMENT ON COLUMN intelligence_reports.policy_developments IS 'Array of policy developments mentioned in intelligence reports';
COMMENT ON COLUMN intelligence_reports.provider IS 'Intelligence provider (e.g., perplexity, openai, anthropic)';

-- Create index for policy_developments queries
CREATE INDEX IF NOT EXISTS idx_intelligence_reports_policy_developments 
ON intelligence_reports USING GIN (policy_developments);

-- Ensure RLS is enabled on intelligence_reports
ALTER TABLE intelligence_reports ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Enable read access for all users" ON intelligence_reports;
DROP POLICY IF EXISTS "Enable insert access for service role" ON intelligence_reports;
DROP POLICY IF EXISTS "Enable update access for service role" ON intelligence_reports;
DROP POLICY IF EXISTS "Enable delete access for service role" ON intelligence_reports;

-- Create comprehensive RLS policies for intelligence_reports
CREATE POLICY "Enable read access for all users"
ON intelligence_reports FOR SELECT
USING (true);

CREATE POLICY "Enable insert access for service role"
ON intelligence_reports FOR INSERT
WITH CHECK (true);

CREATE POLICY "Enable update access for service role"
ON intelligence_reports FOR UPDATE
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable delete access for service role"
ON intelligence_reports FOR DELETE
USING (true);

-- Also add missing columns for enrichment_citations table if it doesn't exist
CREATE TABLE IF NOT EXISTS enrichment_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
    innovation_id UUID REFERENCES innovations(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT,
    confidence_score FLOAT NOT NULL DEFAULT 0.0,
    citation_text TEXT,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    citation_type TEXT NOT NULL DEFAULT 'unknown',
    african_relevance_indicators JSONB DEFAULT '[]'::jsonb,
    ai_relevance_indicators JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on enrichment_citations
ALTER TABLE enrichment_citations ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Enable read access for enrichment citations" ON enrichment_citations;
DROP POLICY IF EXISTS "Enable insert access for enrichment citations" ON enrichment_citations;
DROP POLICY IF EXISTS "Enable update access for enrichment citations" ON enrichment_citations;
DROP POLICY IF EXISTS "Enable delete access for enrichment citations" ON enrichment_citations;

-- Create comprehensive RLS policies for enrichment_citations
CREATE POLICY "Enable read access for enrichment citations"
ON enrichment_citations FOR SELECT
USING (true);

CREATE POLICY "Enable insert access for enrichment citations"
ON enrichment_citations FOR INSERT
WITH CHECK (true);

CREATE POLICY "Enable update access for enrichment citations"
ON enrichment_citations FOR UPDATE
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable delete access for enrichment citations"
ON enrichment_citations FOR DELETE
USING (true);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_enrichment_citations_publication_id ON enrichment_citations(publication_id);
CREATE INDEX IF NOT EXISTS idx_enrichment_citations_innovation_id ON enrichment_citations(innovation_id);
CREATE INDEX IF NOT EXISTS idx_enrichment_citations_processed ON enrichment_citations(processed);
CREATE INDEX IF NOT EXISTS idx_enrichment_citations_confidence ON enrichment_citations(confidence_score);
CREATE INDEX IF NOT EXISTS idx_enrichment_citations_discovered_at ON enrichment_citations(discovered_at);

-- Create snowball_sessions table if it doesn't exist
CREATE TABLE IF NOT EXISTS snowball_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT DEFAULT 0.0,
    citations_processed INTEGER DEFAULT 0,
    new_discoveries INTEGER DEFAULT 0,
    failed_extractions INTEGER DEFAULT 0,
    depth_reached INTEGER DEFAULT 0,
    session_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on snowball_sessions
ALTER TABLE snowball_sessions ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Enable read access for snowball sessions" ON snowball_sessions;
DROP POLICY IF EXISTS "Enable insert access for snowball sessions" ON snowball_sessions;
DROP POLICY IF EXISTS "Enable update access for snowball sessions" ON snowball_sessions;
DROP POLICY IF EXISTS "Enable delete access for snowball sessions" ON snowball_sessions;

-- Create comprehensive RLS policies for snowball_sessions
CREATE POLICY "Enable read access for snowball sessions"
ON snowball_sessions FOR SELECT
USING (true);

CREATE POLICY "Enable insert access for snowball sessions"
ON snowball_sessions FOR INSERT
WITH CHECK (true);

CREATE POLICY "Enable update access for snowball sessions"
ON snowball_sessions FOR UPDATE
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable delete access for snowball sessions"
ON snowball_sessions FOR DELETE
USING (true);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_snowball_sessions_session_id ON snowball_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_snowball_sessions_start_time ON snowball_sessions(start_time);

-- Add trigger for updated_at on enrichment_citations
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_enrichment_citations_updated_at ON enrichment_citations;
CREATE TRIGGER update_enrichment_citations_updated_at
    BEFORE UPDATE ON enrichment_citations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
