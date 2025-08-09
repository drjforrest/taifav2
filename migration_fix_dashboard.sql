-- =====================================================
-- TAIFA-FIALA Dashboard Fix Migration
-- Add missing duplicate_metadata column and intelligence_reports table
-- =====================================================

-- 1. Add duplicate_metadata column to publications table
ALTER TABLE publications 
ADD COLUMN IF NOT EXISTS duplicate_metadata JSONB;

-- 2. Add duplicate_metadata column to innovations table  
ALTER TABLE innovations 
ADD COLUMN IF NOT EXISTS duplicate_metadata JSONB;

-- 3. Add duplicate_metadata column to articles table (if it exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'articles') THEN
        ALTER TABLE articles ADD COLUMN IF NOT EXISTS duplicate_metadata JSONB;
    END IF;
END $$;

-- 4. Create intelligence_reports table
CREATE TABLE IF NOT EXISTS intelligence_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    report_type TEXT NOT NULL CHECK (report_type IN (
        'innovation_discovery', 
        'funding_landscape', 
        'market_analysis', 
        'technology_trends',
        'ecosystem_update',
        'competitive_analysis'
    )),
    summary TEXT,
    key_findings JSONB,
    innovations_mentioned UUID[] DEFAULT '{}',
    funding_updates JSONB,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    sources JSONB,
    geographic_focus TEXT[],
    follow_up_actions TEXT[],
    validation_flags JSONB,
    generation_timestamp TIMESTAMPTZ DEFAULT NOW(),
    intelligence_type TEXT DEFAULT 'automated',
    time_period TEXT,
    data_sources TEXT[],
    methodology TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    duplicate_metadata JSONB
);

-- 5. Add indexes for intelligence_reports
CREATE INDEX IF NOT EXISTS intelligence_reports_report_type_idx ON intelligence_reports(report_type);
CREATE INDEX IF NOT EXISTS intelligence_reports_generation_timestamp_idx ON intelligence_reports(generation_timestamp DESC);
CREATE INDEX IF NOT EXISTS intelligence_reports_geographic_focus_idx ON intelligence_reports USING GIN(geographic_focus);
CREATE INDEX IF NOT EXISTS intelligence_reports_innovations_mentioned_idx ON intelligence_reports USING GIN(innovations_mentioned);
CREATE INDEX IF NOT EXISTS intelligence_reports_confidence_score_idx ON intelligence_reports(confidence_score);

-- 6. Add indexes for duplicate_metadata columns
CREATE INDEX IF NOT EXISTS publications_duplicate_metadata_idx ON publications USING GIN(duplicate_metadata);
CREATE INDEX IF NOT EXISTS innovations_duplicate_metadata_idx ON innovations USING GIN(duplicate_metadata);

-- Check if articles table exists before adding index
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'articles') THEN
        CREATE INDEX IF NOT EXISTS articles_duplicate_metadata_idx ON articles USING GIN(duplicate_metadata);
    END IF;
END $$;

-- 7. Enable RLS on intelligence_reports
ALTER TABLE intelligence_reports ENABLE ROW LEVEL SECURITY;

-- 8. RLS Policies for intelligence_reports

-- Allow public read access to intelligence reports
CREATE POLICY IF NOT EXISTS "intelligence_reports_public_read" ON intelligence_reports
    FOR SELECT USING (true);

-- Allow authenticated users to insert intelligence reports
CREATE POLICY IF NOT EXISTS "intelligence_reports_authenticated_insert" ON intelligence_reports
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Allow users to update their own intelligence reports
CREATE POLICY IF NOT EXISTS "intelligence_reports_user_update" ON intelligence_reports
    FOR UPDATE USING (auth.uid() = created_by);

-- Allow users to delete their own intelligence reports
CREATE POLICY IF NOT EXISTS "intelligence_reports_user_delete" ON intelligence_reports
    FOR DELETE USING (auth.uid() = created_by);

-- Allow service role full access (for API operations)
CREATE POLICY IF NOT EXISTS "intelligence_reports_service_role_all" ON intelligence_reports
    FOR ALL USING (auth.role() = 'service_role');

-- 9. Update trigger for intelligence_reports
CREATE OR REPLACE FUNCTION update_intelligence_reports_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if exists and recreate (PostgreSQL doesn't support IF NOT EXISTS for triggers)
DROP TRIGGER IF EXISTS update_intelligence_reports_updated_at ON intelligence_reports;

CREATE TRIGGER update_intelligence_reports_updated_at
    BEFORE UPDATE ON intelligence_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_intelligence_reports_updated_at();

-- 10. Add comments for documentation
COMMENT ON TABLE intelligence_reports IS 'AI-generated intelligence reports for ecosystem monitoring';
COMMENT ON COLUMN intelligence_reports.report_type IS 'Type of intelligence report generated';
COMMENT ON COLUMN intelligence_reports.key_findings IS 'JSON object containing structured key findings';
COMMENT ON COLUMN intelligence_reports.innovations_mentioned IS 'Array of innovation UUIDs referenced in this report';
COMMENT ON COLUMN intelligence_reports.funding_updates IS 'JSON object containing funding landscape updates';
COMMENT ON COLUMN intelligence_reports.confidence_score IS 'AI confidence score for report accuracy (0.0-1.0)';
COMMENT ON COLUMN intelligence_reports.sources IS 'JSON array of data sources used for report generation';
COMMENT ON COLUMN intelligence_reports.validation_flags IS 'JSON object containing validation status and flags';
COMMENT ON COLUMN intelligence_reports.duplicate_metadata IS 'Metadata for deduplication tracking';

COMMENT ON COLUMN publications.duplicate_metadata IS 'Metadata for tracking duplicate detection and resolution';
COMMENT ON COLUMN innovations.duplicate_metadata IS 'Metadata for tracking duplicate detection and resolution';

-- 11. Grant permissions
GRANT SELECT ON intelligence_reports TO anon;
GRANT ALL ON intelligence_reports TO authenticated;
GRANT ALL ON intelligence_reports TO service_role;

-- 12. Update materialized view to include new data (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.views WHERE table_name = 'dashboard_stats') THEN
        DROP MATERIALIZED VIEW IF EXISTS dashboard_stats;
        
        CREATE MATERIALIZED VIEW dashboard_stats AS
        SELECT 
            (SELECT COUNT(*) FROM publications WHERE duplicate_metadata IS NULL OR duplicate_metadata = '{}') as total_publications,
            (SELECT COUNT(*) FROM innovations WHERE duplicate_metadata IS NULL OR duplicate_metadata = '{}') as total_innovations,
            (SELECT COUNT(*) FROM organizations) as total_organizations,
            (SELECT COUNT(*) FROM individuals WHERE verification_status = 'verified') as verified_individuals,
            (SELECT COUNT(*) FROM intelligence_reports) as total_intelligence_reports,
            (SELECT COUNT(DISTINCT entity) FROM publications, unnest(african_entities) as entity WHERE (duplicate_metadata IS NULL OR duplicate_metadata = '{}')) as african_countries_covered,
            (SELECT COUNT(DISTINCT keyword) FROM publications, unnest(keywords) as keyword WHERE (duplicate_metadata IS NULL OR duplicate_metadata = '{}')) as unique_keywords,
            (SELECT AVG(african_relevance_score) FROM publications WHERE african_relevance_score > 0 AND (duplicate_metadata IS NULL OR duplicate_metadata = '{}')) as avg_african_relevance,
            (SELECT AVG(ai_relevance_score) FROM publications WHERE ai_relevance_score > 0 AND (duplicate_metadata IS NULL OR duplicate_metadata = '{}')) as avg_ai_relevance,
            NOW() as last_updated;

        CREATE UNIQUE INDEX ON dashboard_stats (last_updated);
    END IF;
END $$;

-- =====================================================
-- Migration completed successfully!
-- 
-- What was added:
-- 1. duplicate_metadata columns to publications, innovations, and articles tables
-- 2. intelligence_reports table with full schema
-- 3. Proper indexes for performance
-- 4. RLS policies for security
-- 5. Update triggers
-- 6. Documentation comments
-- 7. Updated materialized view (if exists)
-- =====================================================
