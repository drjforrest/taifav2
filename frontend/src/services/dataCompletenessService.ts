/**
 * Data Completeness Service
 * Centralized service for data completeness API calls with fallback handling
 */

import { apiClient } from '@/lib/api-client';
import { MissingDataMap, EnrichmentGaps } from '@/hooks/useDataCompleteness';
import { MockDataService } from './mockDataService';

const API_BASE_URL = '/api/data-completeness';

export class DataCompletenessService {
  /**
   * Fetch missing data map with fallback to mock data
   */
  static async getMissingDataMap(): Promise<MissingDataMap> {
    try {
      const data = await apiClient.get(`${API_BASE_URL}/intelligence-enrichment/missing-data-map`) as MissingDataMap;
      return data;
    } catch (error) {
      console.warn('API not available, using mock data for data completeness widget', error);
      return MockDataService.getMissingDataMap();
    }
  }

  /**
   * Fetch enrichment gaps analysis with fallback handling
   */
  static async getEnrichmentGaps(): Promise<EnrichmentGaps> {
    try {
      const data = await apiClient.get(`${API_BASE_URL}/enrichment-gaps/analysis`) as EnrichmentGaps;
      return data;
    } catch (error) {
      console.warn('Enrichment gaps API not available, using mock data', error);
      return MockDataService.getEnrichmentGaps();
    }
  }

  /**
   * Health check for data completeness API endpoints
   */
  static async healthCheck(): Promise<{
    missingDataMapAvailable: boolean;
    enrichmentGapsAvailable: boolean;
  }> {
    const results = await Promise.allSettled([
      apiClient.get(`${API_BASE_URL}/intelligence-enrichment/missing-data-map`),
      apiClient.get(`${API_BASE_URL}/enrichment-gaps/analysis`)
    ]);

    return {
      missingDataMapAvailable: results[0].status === 'fulfilled',
      enrichmentGapsAvailable: results[1].status === 'fulfilled'
    };
  }
}