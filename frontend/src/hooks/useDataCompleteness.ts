'use client';

import { useCallback, useEffect, useState } from 'react';
import { DataCompletenessService } from '@/services';

export interface FieldCompleteness {
  completeness_percentage: number;
  complete_records: number;
  missing_records: number;
  field_type: 'core' | 'enrichment';
}

export interface TableAnalysis {
  total_records: number;
  completeness_matrix: Record<string, boolean>[];
  field_completeness: Record<string, FieldCompleteness>;
  overall_completeness: number;
  core_fields_completeness: number;
  enrichment_fields_completeness: number;
  error?: string;
}

export interface MissingDataMap {
  missing_data_map: Record<string, TableAnalysis>;
  recommendations: string[];
  analysis_timestamp: string;
  summary: {
    tables_analyzed: number;
    total_records_analyzed: number;
    intelligence_table_exists: boolean;
  };
}

export interface CriticalGap {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  impact: string;
  affected_records: number;
  recommended_action: string;
}

export interface EnrichmentGaps {
  gaps_analysis: {
    publications_gaps: Record<string, number>;
    innovations_gaps: Record<string, number>;
    intelligence_gaps: {
      reports_exist: boolean;
      total_reports: number;
      intelligence_gap_severity: string;
    };
    critical_missing_data: CriticalGap[];
    enrichment_priority: Array<{
      task: string;
      priority_score: number;
      justification: string;
      estimated_effort: string;
      expected_impact: string;
    }>;
  };
  actionable_insights: string[];
}

export interface UseDataCompletenessOptions {
  autoFetch?: boolean;
  fetchInterval?: number;
}

export interface UseDataCompletenessReturn {
  missingDataMap: MissingDataMap | null;
  enrichmentGaps: EnrichmentGaps | null;
  loading: boolean;
  error: string | null;
  fetchMissingDataMap: () => Promise<void>;
  fetchEnrichmentGaps: () => Promise<void>;
  fetchAll: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const useDataCompleteness = (
  options: UseDataCompletenessOptions = {}
): UseDataCompletenessReturn => {
  const { autoFetch = true, fetchInterval } = options;

  const [missingDataMap, setMissingDataMap] = useState<MissingDataMap | null>(null);
  const [enrichmentGaps, setEnrichmentGaps] = useState<EnrichmentGaps | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMissingDataMap = useCallback(async () => {
    try {
      const data = await DataCompletenessService.getMissingDataMap();
      setMissingDataMap(data);
    } catch (err) {
      console.error('Failed to fetch missing data map:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch missing data map');
    }
  }, []);

  const fetchEnrichmentGaps = useCallback(async () => {
    try {
      const data = await DataCompletenessService.getEnrichmentGaps();
      setEnrichmentGaps(data);
    } catch (err) {
      console.error('Failed to fetch enrichment gaps:', err);
      // Don't set error for enrichment gaps as it's secondary data
    }
  }, []);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        fetchMissingDataMap(),
        fetchEnrichmentGaps().catch(() => {
          // Enrichment gaps is optional, don't fail the whole operation
          console.warn('Enrichment gaps fetch failed, continuing...');
        })
      ]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data completeness';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [fetchMissingDataMap, fetchEnrichmentGaps]);

  const refresh = useCallback(async () => {
    await fetchAll();
  }, [fetchAll]);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      fetchAll();
    }
  }, [autoFetch, fetchAll]);

  // Set up interval fetching if specified
  useEffect(() => {
    if (fetchInterval && fetchInterval > 0) {
      const interval = setInterval(() => {
        fetchAll();
      }, fetchInterval);

      return () => clearInterval(interval);
    }
  }, [fetchInterval, fetchAll]);

  return {
    missingDataMap,
    enrichmentGaps,
    loading,
    error,
    fetchMissingDataMap,
    fetchEnrichmentGaps,
    fetchAll,
    refresh,
  };
};

// Re-export utility functions for backward compatibility
export {
  getCompletenessColor,
  getCompletenessColorClass,
  getCompletenessTextColor,
  getSeverityColor,
  getSeverityIcon,
  formatCompleteness,
  calculateOverallCompleteness,
  categorizeFieldsByCompleteness,
  generateRecommendations
} from '@/utils';