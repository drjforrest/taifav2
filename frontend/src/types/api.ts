// API-only type definitions (no database dependencies)

export interface EnrichmentCitation {
  id: string;
  title: string;
  url?: string;
  confidence_score: number;
  citation_text: string;
  discovered_at: string;
  processed: boolean;
}

export interface Publication {
  id: string;
  title: string;
  abstract?: string;
  publication_type: string;
  publication_date?: string;
  year?: number;
  doi?: string;
  url?: string;
  pdf_url?: string;
  journal?: string;
  venue?: string;
  citation_count: number;
  project_domain?: string;
  ai_techniques?: string;
  geographic_scope?: string;
  funding_source?: string;
  key_outcomes?: string;
  african_relevance_score: number;
  ai_relevance_score: number;
  african_entities?: string[];
  keywords?: string[];
  source: string;
  source_id?: string;
  data_type: string;
  processed_at: string;
  verification_status: string;
  created_at: string;
  updated_at: string;
  // Data Provenance Fields
  data_source?: 'primary' | 'enriched' | 'systematic_review';
  enrichment_confidence?: number;
  enrichment_citations?: EnrichmentCitation[];
  original_discovery_method?: string;
}

export interface Innovation {
  id: string;
  title: string;
  description: string;
  innovation_type: string;
  domain: string;
  ai_techniques_used?: string[];
  target_beneficiaries?: string;
  problem_addressed?: string;
  solution_approach?: string;
  development_stage: string;
  technology_stack?: string[];
  programming_languages?: string[];
  datasets_used?: string[];
  countries_deployed?: string[];
  target_countries?: string[];
  users_reached: number;
  impact_metrics?: any;
  verification_status: string;
  visibility: string;
  demo_url?: string;
  github_url?: string;
  documentation_url?: string;
  video_url?: string;
  image_urls?: string[];
  creation_date?: string;
  last_updated_date?: string;
  created_at: string;
  updated_at: string;
  // Data Provenance Fields
  data_source?: 'primary' | 'enriched' | 'systematic_review';
  enrichment_confidence?: number;
  enrichment_citations?: EnrichmentCitation[];
  original_discovery_method?: string;
}

export interface Organization {
  id: string;
  name: string;
  organization_type: string;
  country: string;
  website?: string;
  description?: string;
  founded_date?: string;
  contact_email?: string;
  logo_url?: string;
  verification_status: string;
  created_at: string;
  updated_at: string;
}

export interface Individual {
  id: string;
  name: string;
  email?: string;
  role?: string;
  bio?: string;
  country?: string;
  organization_id?: string;
  linkedin_url?: string;
  twitter_url?: string;
  website_url?: string;
  orcid_id?: string;
  profile_image_url?: string;
  expertise_areas?: string[];
  verification_status: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_publications: number;
  total_innovations: number;
  total_organizations: number;
  verified_individuals: number;
  african_countries_covered: number;
  unique_keywords: number;
  avg_african_relevance: number;
  avg_ai_relevance: number;
  last_updated: string;
}

export interface RecentActivity {
  recentPublications: Publication[];
  recentInnovations: Innovation[];
}

export interface ETLMetrics {
  batch_size: number;
  duplicates_removed: number;
  processing_time_ms: number;
  success_rate: number;
  items_processed: number;
  items_failed: number;
  memory_usage_mb: number;
  cpu_usage_percent: number;
}

export interface ETLStatus {
  academic_pipeline_active: boolean;
  news_pipeline_active: boolean;
  serper_pipeline_active: boolean;
  enrichment_pipeline_active: boolean;
  last_academic_run: string | null;
  last_news_run: string | null;
  last_serper_run: string | null;
  last_enrichment_run: string | null;
  total_processed_today: number;
  errors_today: number;
  metrics?: ETLMetrics;
  pipeline_metrics?: {
    academic_pipeline?: ETLMetrics;
    news_pipeline?: ETLMetrics;
    discovery_pipeline?: ETLMetrics;
    enrichment_pipeline?: ETLMetrics;
  };
  _isMockData?: boolean;
}

export interface ETLHealth {
  status: "healthy" | "degraded" | "down";
  last_check: string;
  response_time: number;
}

export interface PublicationFilters {
  search?: string;
  domain?: string;
  source?: string;
  year?: number;
  minAfricanScore?: number;
  minAiScore?: number;
  limit?: number;
  offset?: number;
}

export interface PublicationStats {
  totalPublications: number;
  bySource: Record<string, number>;
  byYear: Record<string, number>;
  byDomain: Record<string, number>;
  avgAfricanScore: number;
  avgAiScore: number;
}
