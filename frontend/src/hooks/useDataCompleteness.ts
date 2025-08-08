'use client';

import { useCallback, useEffect, useState } from 'react';

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

const API_BASE_URL = '/api/data-completeness';

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
      const response = await fetch(`${API_BASE_URL}/intelligence-enrichment/missing-data-map`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setMissingDataMap(data);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch missing data map';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const fetchEnrichmentGaps = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/enrichment-gaps/analysis`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setEnrichmentGaps(data);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch enrichment gaps';
      console.error('Failed to fetch enrichment gaps:', err);
      // Don't set error for enrichment gaps as it's secondary data
      throw err;
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

// Utility functions for data processing
export const getCompletenessColor = (percentage: number): string => {
  if (percentage >= 80) return 'bg-green-500';
  if (percentage >= 60) return 'bg-yellow-500';
  if (percentage >= 40) return 'bg-orange-500';
  return 'bg-red-500';
};

export const getCompletenessColorClass = (percentage: number): string => {
  if (percentage >= 80) return 'text-green-700 bg-green-100';
  if (percentage >= 60) return 'text-yellow-700 bg-yellow-100';
  if (percentage >= 40) return 'text-orange-700 bg-orange-100';
  return 'text-red-700 bg-red-100';
};

export const getCompletenessTextColor = (percentage: number): string => {
  if (percentage >= 80) return 'text-green-600';
  if (percentage >= 60) return 'text-yellow-600';
  if (percentage >= 40) return 'text-orange-600';
  return 'text-red-600';
};

export const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'critical': return 'text-red-600 bg-red-100';
    case 'high': return 'text-orange-600 bg-orange-100';
    case 'medium': return 'text-yellow-600 bg-yellow-100';
    default: return 'text-green-600 bg-green-100';
  }
};

export const getSeverityIcon = (severity: string) => {
  // Note: Icons should be imported in the component using this function
  switch (severity) {
    case 'critical': return 'XCircle';
    case 'high': return 'AlertCircle';
    case 'medium': return 'AlertCircle';
    default: return 'CheckCircle';
  }
};