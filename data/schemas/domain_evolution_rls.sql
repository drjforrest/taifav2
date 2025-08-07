-- Enable RLS on domain_evolution table
ALTER TABLE domain_evolution ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for domain_evolution table
CREATE POLICY "Public read access for domain evolution" ON domain_evolution 
    FOR SELECT USING (true);

CREATE POLICY "Service role full access on domain_evolution" ON domain_evolution
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated read access on domain_evolution" ON domain_evolution
    FOR SELECT TO authenticated USING (true);