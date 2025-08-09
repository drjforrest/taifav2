-- Create duplicate_records table for tracking cross-table duplicates
-- This table tracks when records are identified as duplicates across different tables

CREATE TABLE IF NOT EXISTS duplicate_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_table VARCHAR(50) NOT NULL, -- Table where the duplicate was found
    source_id UUID NOT NULL,           -- ID of the duplicate record
    target_table VARCHAR(50) NOT NULL, -- Table containing the original record
    target_id UUID NOT NULL,           -- ID of the original record
    match_type VARCHAR(20) NOT NULL,   -- Type of match: 'exact', 'metadata', 'semantic', 'fuzzy'
    confidence_score DECIMAL(5,3) NOT NULL, -- Confidence score (0.0-1.0)
    matching_fields JSONB,             -- Array of fields that matched
    status VARCHAR(20) DEFAULT 'active', -- Status: 'active', 'resolved', 'false_positive'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_confidence_score CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    CONSTRAINT valid_match_type CHECK (match_type IN ('exact', 'metadata', 'semantic', 'fuzzy')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'resolved', 'false_positive')),
    CONSTRAINT valid_table_names CHECK (
        source_table IN ('publications', 'articles', 'innovations') AND
        target_table IN ('publications', 'articles', 'innovations')
    ),
    
    -- Prevent self-referencing duplicates and duplicate entries
    CONSTRAINT no_self_reference CHECK (NOT (source_table = target_table AND source_id = target_id)),
    UNIQUE(source_table, source_id, target_table, target_id)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_duplicate_records_source ON duplicate_records(source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_duplicate_records_target ON duplicate_records(target_table, target_id);
CREATE INDEX IF NOT EXISTS idx_duplicate_records_match_type ON duplicate_records(match_type);
CREATE INDEX IF NOT EXISTS idx_duplicate_records_confidence ON duplicate_records(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_duplicate_records_status ON duplicate_records(status);
CREATE INDEX IF NOT EXISTS idx_duplicate_records_created_at ON duplicate_records(created_at DESC);

-- Add columns to existing tables to track duplicate status
-- These columns will be added if they don't exist

-- Add duplicate_metadata column to publications table
ALTER TABLE publications ADD COLUMN IF NOT EXISTS duplicate_metadata JSONB;

-- Add duplicate_metadata column to articles table  
ALTER TABLE articles ADD COLUMN IF NOT EXISTS duplicate_metadata JSONB;

-- Add duplicate_metadata column to innovations table
ALTER TABLE innovations ADD COLUMN IF NOT EXISTS duplicate_metadata JSONB;

-- Add indexes on duplicate_metadata columns for filtering
CREATE INDEX IF NOT EXISTS idx_publications_duplicate_metadata ON publications USING GIN (duplicate_metadata) WHERE duplicate_metadata IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_articles_duplicate_metadata ON articles USING GIN (duplicate_metadata) WHERE duplicate_metadata IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_innovations_duplicate_metadata ON innovations USING GIN (duplicate_metadata) WHERE duplicate_metadata IS NOT NULL;

-- Add indexes for filtering non-duplicates (null values)
CREATE INDEX IF NOT EXISTS idx_publications_non_duplicates ON publications(id) WHERE duplicate_metadata IS NULL;
CREATE INDEX IF NOT EXISTS idx_articles_non_duplicates ON articles(id) WHERE duplicate_metadata IS NULL;
CREATE INDEX IF NOT EXISTS idx_innovations_non_duplicates ON innovations(id) WHERE duplicate_metadata IS NULL;

-- Create a view for easy duplicate analysis
CREATE OR REPLACE VIEW duplicate_analysis AS
SELECT 
    dr.source_table,
    dr.target_table,
    dr.match_type,
    dr.confidence_score,
    COUNT(*) as duplicate_count,
    AVG(dr.confidence_score) as avg_confidence,
    MIN(dr.created_at) as first_detected,
    MAX(dr.created_at) as last_detected
FROM duplicate_records dr
WHERE dr.status = 'active'
GROUP BY dr.source_table, dr.target_table, dr.match_type, dr.confidence_score
ORDER BY duplicate_count DESC, avg_confidence DESC;

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_duplicate_records_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_duplicate_records_updated_at
    BEFORE UPDATE ON duplicate_records
    FOR EACH ROW
    EXECUTE FUNCTION update_duplicate_records_updated_at();

-- Add comments for documentation
COMMENT ON TABLE duplicate_records IS 'Tracks duplicate records found across publications, articles, and innovations tables';
COMMENT ON COLUMN duplicate_records.source_table IS 'Table containing the duplicate record';
COMMENT ON COLUMN duplicate_records.source_id IS 'ID of the duplicate record';
COMMENT ON COLUMN duplicate_records.target_table IS 'Table containing the original record';
COMMENT ON COLUMN duplicate_records.target_id IS 'ID of the original record';
COMMENT ON COLUMN duplicate_records.match_type IS 'Type of duplicate detection: exact, metadata, semantic, or fuzzy';
COMMENT ON COLUMN duplicate_records.confidence_score IS 'Confidence score from 0.0 to 1.0 indicating match certainty';
COMMENT ON COLUMN duplicate_records.matching_fields IS 'JSON array of field names that matched during detection';
COMMENT ON COLUMN duplicate_records.status IS 'Current status: active, resolved, or false_positive';

COMMENT ON VIEW duplicate_analysis IS 'Aggregated view of duplicate patterns for analysis and reporting';
