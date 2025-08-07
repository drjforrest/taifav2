-- Enable RLS on success_patterns table
ALTER TABLE success_patterns ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for success_patterns table
CREATE POLICY "Public read access for success patterns" ON success_patterns 
    FOR SELECT USING (true);

CREATE POLICY "Service role full access on success_patterns" ON success_patterns
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated read access on success_patterns" ON success_patterns
    FOR SELECT TO authenticated USING (true);

-- Enable RLS on failure_patterns table
ALTER TABLE failure_patterns ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for failure_patterns table
CREATE POLICY "Public read access for failure patterns" ON failure_patterns 
    FOR SELECT USING (true);

CREATE POLICY "Service role full access on failure_patterns" ON failure_patterns
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated read access on failure_patterns" ON failure_patterns
    FOR SELECT TO authenticated USING (true);