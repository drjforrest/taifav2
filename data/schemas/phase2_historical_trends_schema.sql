-- Phase 2 Historical Trend Analysis Schema
-- Part of the Citations Expansion Strategy Implementation

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

-- Allow authenticated users read access
CREATE POLICY "Allow authenticated read access on innovation_lifecycles" ON innovation_lifecycles
    FOR SELECT TO authenticated USING (true);

-- Create domain_evolution table
CREATE TABLE IF NOT EXISTS domain_evolution (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_name TEXT NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  innovation_count INTEGER DEFAULT 0,
  publication_count INTEGER DEFAULT 0,
  funding_amount DECIMAL(15,2) DEFAULT 0,
  key_players JSONB, -- Leading researchers/institutions
  maturity_level TEXT, -- emerging, growing, mature, declining
  growth_rate DECIMAL(5,2), -- Percentage growth per period
  collaboration_index DECIMAL(5,2), -- Cross-institution collaboration measure
  technology_mix JSONB, -- Dominant technologies in this domain
  geographic_distribution JSONB, -- Regional distribution of activity
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for domain_evolution table
CREATE INDEX IF NOT EXISTS idx_domain_evolution_domain_name ON domain_evolution(domain_name);
CREATE INDEX IF NOT EXISTS idx_domain_evolution_period ON domain_evolution(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_domain_evolution_maturity ON domain_evolution(maturity_level);

-- Enable RLS on domain_evolution table
ALTER TABLE domain_evolution ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for domain_evolution table
CREATE POLICY "Public read access for domain evolution" ON domain_evolution 
    FOR SELECT USING (true);

CREATE POLICY "Service role full access on domain_evolution" ON domain_evolution
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated read access on domain_evolution" ON domain_evolution
    FOR SELECT TO authenticated USING (true);

-- Create success_patterns table
CREATE TABLE IF NOT EXISTS success_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pattern_name TEXT NOT NULL,
  pattern_description TEXT,
  pattern_type TEXT, -- technical, organizational, funding, market
  associated_features JSONB, -- Key features that define this pattern
  success_rate DECIMAL(5,2), -- Percentage of innovations with this pattern that succeed
  domain_specific BOOLEAN DEFAULT FALSE,
  geographic_scope TEXT, -- Global or specific regions
  temporal_scope TEXT, -- Time periods where this pattern is most effective
  supporting_evidence JSONB, -- Case studies, research papers, statistics
  confidence_score DECIMAL(3,2), -- Algorithm confidence in this pattern
  last_validated DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for success_patterns table
CREATE INDEX IF NOT EXISTS idx_success_patterns_pattern_type ON success_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_success_patterns_domain_specific ON success_patterns(domain_specific);
CREATE INDEX IF NOT EXISTS idx_success_patterns_confidence ON success_patterns(confidence_score);

-- Enable RLS on success_patterns table
ALTER TABLE success_patterns ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for success_patterns table
CREATE POLICY "Public read access for success patterns" ON success_patterns 
    FOR SELECT USING (true);

CREATE POLICY "Service role full access on success_patterns" ON success_patterns
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated read access on success_patterns" ON success_patterns
    FOR SELECT TO authenticated USING (true);

-- Create failure_patterns table
CREATE TABLE IF NOT EXISTS failure_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pattern_name TEXT NOT NULL,
  pattern_description TEXT,
  failure_category TEXT, -- technical, market, funding, organizational
  root_causes JSONB, -- Primary causes of failure
  early_indicators JSONB, -- Warning signs that appear before failure
  mitigation_strategies JSONB, -- Recommended approaches to avoid this failure
  associated_domains TEXT[], -- Domains where this failure pattern is common
  geographic_prevalence JSONB, -- Regional occurrence rates
  temporal_patterns JSONB, -- When in the lifecycle this failure typically occurs
  supporting_evidence JSONB, -- Case studies, research papers, statistics
  confidence_score DECIMAL(3,2), -- Algorithm confidence in this pattern
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for failure_patterns table
CREATE INDEX IF NOT EXISTS idx_failure_patterns_failure_category ON failure_patterns(failure_category);
CREATE INDEX IF NOT EXISTS idx_failure_patterns_confidence ON failure_patterns(confidence_score);

-- Enable RLS on failure_patterns table
ALTER TABLE failure_patterns ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for failure_patterns table
CREATE POLICY "Public read access for failure patterns" ON failure_patterns 
    FOR SELECT USING (true);

CREATE POLICY "Service role full access on failure_patterns" ON failure_patterns
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated read access on failure_patterns" ON failure_patterns
    FOR SELECT TO authenticated USING (true);

-- Create function to update updated_at timestamp for innovation_lifecycles
CREATE OR REPLACE FUNCTION update_innovation_lifecycles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at for innovation_lifecycles
DROP TRIGGER IF EXISTS trigger_update_innovation_lifecycles_updated_at ON innovation_lifecycles;
CREATE TRIGGER trigger_update_innovation_lifecycles_updated_at
    BEFORE UPDATE ON innovation_lifecycles
    FOR EACH ROW
    EXECUTE FUNCTION update_innovation_lifecycles_updated_at();

-- Create function to update updated_at timestamp for domain_evolution
CREATE OR REPLACE FUNCTION update_domain_evolution_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at for domain_evolution
DROP TRIGGER IF EXISTS trigger_update_domain_evolution_updated_at ON domain_evolution;
CREATE TRIGGER trigger_update_domain_evolution_updated_at
    BEFORE UPDATE ON domain_evolution
    FOR EACH ROW
    EXECUTE FUNCTION update_domain_evolution_updated_at();

-- Create function to update updated_at timestamp for success_patterns
CREATE OR REPLACE FUNCTION update_success_patterns_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at for success_patterns
DROP TRIGGER IF EXISTS trigger_update_success_patterns_updated_at ON success_patterns;
CREATE TRIGGER trigger_update_success_patterns_updated_at
    BEFORE UPDATE ON success_patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_success_patterns_updated_at();

-- Create function to update updated_at timestamp for failure_patterns
CREATE OR REPLACE FUNCTION update_failure_patterns_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at for failure_patterns
DROP TRIGGER IF EXISTS trigger_update_failure_patterns_updated_at ON failure_patterns;
CREATE TRIGGER trigger_update_failure_patterns_updated_at
    BEFORE UPDATE ON failure_patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_failure_patterns_updated_at();