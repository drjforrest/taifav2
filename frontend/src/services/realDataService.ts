/**
 * Real Data Service - Fetches live data from ETL pipeline
 * Replaces static mock data with real database statistics
 */

export interface RealStats {
  total_innovations: number;
  total_publications: number;
  total_organizations: number;
  verified_individuals: number;
  verified_innovations: number;
  african_countries_covered: number;
  innovations_by_country: Record<string, number>;
  unique_keywords: number;
  innovation_types: Record<string, number>;
  avg_african_relevance: number;
  avg_ai_relevance: number;
  verification_rate: number;
  total_funding: number;
  avg_funding: number;
  funded_innovations: number;
  pipeline_status: string;
  data_freshness: string;
  last_updated: string;
}

export interface RealInnovation {
  id: string;
  title: string;
  description: string;
  innovation_type: string;
  verification_status: string;
  visibility: string;
  country: string | null;
  creation_date: string;
  organizations: any[];
  individuals: any[];
  fundings: any[];
  publications: any[];
  tags: string[];
  impact_metrics: any;
  website_url: string | null;
  github_url: string | null;
  demo_url: string | null;
  source_url: string | null;
}

export interface InnovationsResponse {
  innovations: RealInnovation[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  search_metadata?: any;
}

class RealDataService {
  private baseUrl: string;

  constructor() {
    // Use production API by default, fallback to local development
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.taifa-fiala.net';
  }

  /**
   * Fetch live dashboard statistics
   */
  async getStats(): Promise<RealStats> {
    try {
      const response = await fetch(`${this.baseUrl}/api/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: RealStats = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching real stats:', error);
      throw error;
    }
  }

  /**
   * Fetch recent innovations
   */
  async getInnovations(limit: number = 20, offset: number = 0): Promise<InnovationsResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/innovations?limit=${limit}&offset=${offset}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: InnovationsResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching innovations:', error);
      throw error;
    }
  }

  /**
   * Get ETL pipeline status
   */
  async getETLStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/etl/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.data || data;
    } catch (error) {
      console.error('Error fetching ETL status:', error);
      throw error;
    }
  }

  /**
   * Convert real stats to homepage format
   */
  convertToHomepageData(stats: RealStats) {
    return {
      // Main headline figure - real data
      totalVerifiedInvestment: {
        amount: stats.total_funding || 0, // Will be populated when funding data is available
        currency: "USD",
        period: "2020-2025",
        lastUpdated: stats.last_updated,
        verificationStatus: "live_data_from_etl",
      },

      // ETL Pipeline Data
      realTimeData: {
        totalInnovations: stats.total_innovations,
        totalPublications: stats.total_publications,
        totalOrganizations: stats.total_organizations,
        verifiedInnovations: stats.verified_innovations,
        africanCountriesCovered: stats.african_countries_covered,
        uniqueKeywords: stats.unique_keywords,
        verificationRate: stats.verification_rate,
      },

      // Innovation Type Analysis (Real)
      innovationTypes: stats.innovation_types,

      // Quality Metrics (Real)
      qualityMetrics: {
        avgAfricanRelevance: stats.avg_african_relevance,
        avgAIRelevance: stats.avg_ai_relevance,
        dataFreshness: stats.data_freshness,
        pipelineStatus: stats.pipeline_status,
      },

      // Geographic Distribution (Real)
      geographicData: {
        countriesCovered: stats.african_countries_covered,
        innovationsByCountry: stats.innovations_by_country,
      },

      // Funding Analysis (When available)
      fundingData: {
        totalFunding: stats.total_funding,
        avgFunding: stats.avg_funding,
        fundedInnovations: stats.funded_innovations,
      },

      // Data quality and verification metadata
      dataQuality: {
        verificationLevel: "live_etl_pipeline",
        lastVerified: stats.last_updated,
        confidenceLevel: stats.verification_rate > 80 ? "high" : "medium",
        source: "TAIFA-FIALA ETL Pipeline with integrated Serper, SerpAPI, and Snowball Sampling",
        dataFreshness: stats.data_freshness,
      },
    };
  }

  /**
   * Get comprehensive homepage data
   */
  async getHomepageData() {
    try {
      const [stats, etlStatus] = await Promise.all([
        this.getStats(),
        this.getETLStatus().catch(() => ({ status: 'unknown' })), // Don't fail if ETL status unavailable
      ]);

      const homepageData = this.convertToHomepageData(stats);
      
      return {
        ...homepageData,
        systemStatus: {
          etlPipeline: etlStatus,
          lastUpdated: stats.last_updated,
          isLive: stats.data_freshness === 'live',
        },
      };
    } catch (error) {
      console.error('Error getting homepage data:', error);
      throw error;
    }
  }
}

export const realDataService = new RealDataService();
export default realDataService;