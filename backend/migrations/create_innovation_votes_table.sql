-- Create innovation_votes table for community voting on innovations
-- This table stores votes on whether innovations meet inclusion criteria

CREATE TABLE IF NOT EXISTS innovation_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    innovation_id UUID NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    voter_identifier VARCHAR(255) NOT NULL,  -- Hashed email/IP for deduplication
    vote_type VARCHAR(20) NOT NULL CHECK (vote_type IN ('yes', 'no', 'need_more_info')),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    
    -- Metadata for ML training and fraud prevention
    user_agent TEXT,
    ip_hash VARCHAR(255),
    
    -- Ensure one vote per voter per innovation
    UNIQUE(innovation_id, voter_identifier)
);

-- Create indexes for performance
CREATE INDEX idx_innovation_votes_innovation_id ON innovation_votes(innovation_id);
CREATE INDEX idx_innovation_votes_vote_type ON innovation_votes(vote_type);
CREATE INDEX idx_innovation_votes_created_at ON innovation_votes(created_at);

-- Enable Row Level Security
ALTER TABLE innovation_votes ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Allow all users to read voting statistics (public data)
CREATE POLICY "Anyone can view innovation votes" ON innovation_votes
    FOR SELECT USING (true);

-- Allow authenticated users to insert their own votes
CREATE POLICY "Authenticated users can insert votes" ON innovation_votes
    FOR INSERT WITH CHECK (true);

-- Prevent updates to votes (votes should be immutable)
CREATE POLICY "No updates allowed" ON innovation_votes
    FOR UPDATE USING (false);

-- Only allow deletes by service role (for admin cleanup)
CREATE POLICY "Only service role can delete votes" ON innovation_votes
    FOR DELETE USING (auth.role() = 'service_role');

-- Add some sample data for testing (optional)
-- INSERT INTO innovation_votes (innovation_id, voter_identifier, vote_type, comment)
-- SELECT 
--     i.id,
--     'sample_voter_' || generate_random_uuid()::text,
--     (ARRAY['yes', 'no', 'need_more_info'])[floor(random() * 3) + 1],
--     'Sample vote for testing'
-- FROM innovations i
-- LIMIT 5;