-- Innovation Lifecycle Tracking Schema
-- Part of Phase 2 Historical Trend Analysis Implementation

-- Create innovation_lifecycles table
CREATE TABLE IF NOT EXISTS innovation_lifecycles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  innovation_id UUID REFERENCES innovations(id),
  stage TEXT NOT NULL, -- research, prototype, pilot, production, scaling
  stage_start_date DATE,
  stage_end_date DATE,
  duration_days INTEGER,
  key_milestones JSONB, -- Important events during this stage
  resources_invested JSONB, -- Funding, personnel, equipment
  challenges_encountered JSONB,
  success_indicators JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_innovation_lifecycles_innovation_id ON innovation_lifecycles(innovation_id);
CREATE INDEX IF NOT EXISTS idx_innovation_lifecycles_stage ON innovation_lifecycles(stage);
CREATE INDEX IF NOT EXISTS idx_innovation_lifecycles_dates ON innovation_lifecycles(stage_start_date, stage_end_date);

-- Enable RLS on innovation_lifecycles table
ALTER TABLE innovation_lifecycles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for innovation_lifecycles table
-- Allow public read access for public innovations
CREATE POLICY "Public read access for innovation lifecycles" ON innovation_lifecycles 
    FOR SELECT USING (
        innovation_id IN (SELECT id FROM innovations WHERE visibility = 'public')
    );

-- Allow service role full access (for backend updates)
CREATE POLICY "Service role full access on innovation_lifecycles" ON innovation_lifecycles
    FOR ALL USING (auth.role() = 'service_role');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_innovation_lifecycles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_update_innovation_lifecycles_updated_at ON innovation_lifecycles;
CREATE TRIGGER trigger_update_innovation_lifecycles_updated_at
    BEFORE UPDATE ON innovation_lifecycles
    FOR EACH ROW
    EXECUTE FUNCTION update_innovation_lifecycles_updated_at();