-- Manual Documents Table Schema
-- ================================
-- 
-- This table stores manually processed documents (PDFs, reports)
-- with their extraction results and metadata.

CREATE TABLE IF NOT EXISTS manual_documents (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- File information
    file_name TEXT NOT NULL,
    file_hash TEXT UNIQUE NOT NULL, -- SHA-256 hash to prevent duplicates
    file_size INTEGER NOT NULL,
    
    -- Document classification
    document_type TEXT NOT NULL CHECK (document_type IN (
        'pdf_report',
        'news_article', 
        'research_paper',
        'startup_list',
        'funding_announcement',
        'market_report',
        'unknown'
    )),
    
    -- Processing information
    processing_status TEXT NOT NULL DEFAULT 'pending' CHECK (processing_status IN (
        'pending',
        'processing', 
        'completed',
        'failed',
        'skipped'
    )),
    
    processing_instructions TEXT, -- Custom instructions for extraction
    custom_extraction_prompt TEXT, -- Custom LLM prompt if provided
    
    -- Extraction results
    extracted_text_preview TEXT, -- First 5000 characters of extracted text
    structured_data JSONB, -- LLM-extracted structured data
    
    -- Processing metadata
    processing_duration_seconds REAL,
    llm_provider TEXT, -- 'openai', 'anthropic', etc.
    confidence_score REAL DEFAULT 0.0,
    error_message TEXT,
    
    -- Timestamps
    added_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_manual_documents_file_hash ON manual_documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_manual_documents_document_type ON manual_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_manual_documents_processing_status ON manual_documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_manual_documents_created_at ON manual_documents(created_at);
CREATE INDEX IF NOT EXISTS idx_manual_documents_confidence_score ON manual_documents(confidence_score);

-- GIN index for structured data JSONB queries
CREATE INDEX IF NOT EXISTS idx_manual_documents_structured_data ON manual_documents USING GIN (structured_data);

-- Full-text search index on extracted text
CREATE INDEX IF NOT EXISTS idx_manual_documents_text_search ON manual_documents USING GIN (to_tsvector('english', extracted_text_preview));

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_manual_documents_updated_at 
    BEFORE UPDATE ON manual_documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add foreign key relationship to innovations table
ALTER TABLE innovations 
ADD COLUMN IF NOT EXISTS source_document_id UUID REFERENCES manual_documents(id);

-- Index for the relationship
CREATE INDEX IF NOT EXISTS idx_innovations_source_document ON innovations(source_document_id);

-- Comments for documentation
COMMENT ON TABLE manual_documents IS 'Stores manually processed documents with LLM-assisted extraction results';
COMMENT ON COLUMN manual_documents.file_hash IS 'SHA-256 hash to prevent duplicate processing';
COMMENT ON COLUMN manual_documents.structured_data IS 'JSON data extracted by LLM, varies by document type';
COMMENT ON COLUMN manual_documents.confidence_score IS 'LLM confidence score (0.0-1.0) for extraction quality';
COMMENT ON COLUMN manual_documents.processing_instructions IS 'Custom instructions provided for extraction';
COMMENT ON COLUMN manual_documents.custom_extraction_prompt IS 'Custom LLM prompt for specialized extraction';

-- Sample queries for common operations:

-- Find all successfully processed startup lists
-- SELECT * FROM manual_documents 
-- WHERE document_type = 'startup_list' 
-- AND processing_status = 'completed' 
-- ORDER BY confidence_score DESC;

-- Search for documents containing specific companies
-- SELECT * FROM manual_documents 
-- WHERE structured_data ? 'startups' 
-- AND structured_data #> '{startups}' @> '[{"name": "Flutterwave"}]';

-- Get processing statistics
-- SELECT 
--     document_type,
--     processing_status,
--     COUNT(*) as count,
--     AVG(confidence_score) as avg_confidence,
--     AVG(processing_duration_seconds) as avg_duration
-- FROM manual_documents 
-- GROUP BY document_type, processing_status
-- ORDER BY document_type, processing_status;
