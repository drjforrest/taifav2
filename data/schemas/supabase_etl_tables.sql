-- Create ETL status table for pipeline monitoring
-- This table stores the current status of all ETL pipelines

CREATE TABLE IF NOT EXISTS etl_status (
    id SERIAL PRIMARY KEY,
    academic_pipeline_active BOOLEAN DEFAULT FALSE,
    news_pipeline_active BOOLEAN DEFAULT FALSE,
    serper_pipeline_active BOOLEAN DEFAULT FALSE,
    enrichment_pipeline_active BOOLEAN DEFAULT FALSE,
    last_academic_run TIMESTAMPTZ DEFAULT NULL,
    last_news_run TIMESTAMPTZ DEFAULT NULL,
    last_serper_run TIMESTAMPTZ DEFAULT NULL,
    last_enrichment_run TIMESTAMPTZ DEFAULT NULL,
    total_processed_today INTEGER DEFAULT 0,
    errors_today INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert initial inactive state
INSERT INTO etl_status (
    academic_pipeline_active,
    news_pipeline_active, 
    serper_pipeline_active,
    enrichment_pipeline_active,
    total_processed_today,
    errors_today
) VALUES (
    FALSE,
    FALSE,
    FALSE, 
    FALSE,
    0,
    0
) ON CONFLICT (id) DO NOTHING;

-- Create dashboard_stats materialized view for better performance
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_stats AS
WITH stats AS (
    SELECT 
        (SELECT COUNT(*) FROM innovations) as total_innovations,
        (SELECT COUNT(*) FROM publications) as total_publications,
        (SELECT COUNT(*) FROM organizations) as total_organizations,
        (SELECT COUNT(*) FROM individuals WHERE verification_status = 'verified') as verified_individuals,
        (SELECT COUNT(DISTINCT entity) 
         FROM publications p,
         LATERAL unnest(COALESCE(p.african_entities, ARRAY[]::text[])) AS entity
        ) as african_countries_covered,
        (SELECT COUNT(DISTINCT keyword) 
         FROM publications p,
         LATERAL unnest(COALESCE(p.keywords, ARRAY[]::text[])) AS keyword
        ) as unique_keywords,
        (SELECT ROUND(AVG(african_relevance_score), 4) 
         FROM publications 
         WHERE african_relevance_score IS NOT NULL
        ) as avg_african_relevance,
        (SELECT ROUND(AVG(ai_relevance_score), 4) 
         FROM publications 
         WHERE ai_relevance_score IS NOT NULL
        ) as avg_ai_relevance
)
SELECT 
    total_innovations,
    total_publications,
    total_organizations,
    verified_individuals,
    african_countries_covered,
    unique_keywords,
    avg_african_relevance,
    avg_ai_relevance,
    NOW() as last_updated
FROM stats;

-- Create index on etl_status for faster queries
CREATE INDEX IF NOT EXISTS idx_etl_status_updated_at ON etl_status(updated_at DESC);

-- Enable RLS on etl_status table
ALTER TABLE etl_status ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for etl_status table
-- Allow public read access (for dashboard display)
CREATE POLICY "Allow public read access on etl_status" ON etl_status
    FOR SELECT USING (true);

-- Allow service role full access (for backend updates)
CREATE POLICY "Allow service role full access on etl_status" ON etl_status
    FOR ALL USING (auth.role() = 'service_role');

-- Allow authenticated users read access
CREATE POLICY "Allow authenticated read access on etl_status" ON etl_status
    FOR SELECT TO authenticated USING (true);

-- Create RLS policies for dashboard_stats view
-- Note: Materialized views inherit RLS from underlying tables, but we ensure public access
GRANT SELECT ON dashboard_stats TO anon;
GRANT SELECT ON dashboard_stats TO authenticated;

-- Create function to update etl_status updated_at timestamp
CREATE OR REPLACE FUNCTION update_etl_status_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_update_etl_status_updated_at ON etl_status;
CREATE TRIGGER trigger_update_etl_status_updated_at
    BEFORE UPDATE ON etl_status
    FOR EACH ROW
    EXECUTE FUNCTION update_etl_status_updated_at();

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW dashboard_stats;