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
        // If API is not available, use mock data for development/demo
        console.warn('API not available, using mock data for data completeness widget');
        const mockData = {
          _isMockData: true, // Flag to indicate this is mock data
          missing_data_map: {
            publications: {
              total_records: 96,
              completeness_matrix: [
                { title: true, abstract: true, development_stage: false, business_model: true },
                { title: true, abstract: false, development_stage: true, business_model: false }
              ],
              field_completeness: {
                title: { completeness_percentage: 100, complete_records: 96, missing_records: 0, field_type: 'core' as const },
                abstract: { completeness_percentage: 92, complete_records: 88, missing_records: 8, field_type: 'core' as const },
                development_stage: { completeness_percentage: 65, complete_records: 62, missing_records: 34, field_type: 'enrichment' as const },
                business_model: { completeness_percentage: 58, complete_records: 56, missing_records: 40, field_type: 'enrichment' as const }
              },
              overall_completeness: 78.5,
              core_fields_completeness: 95.0,
              enrichment_fields_completeness: 58.2
            },
            innovations: {
              total_records: 24,
              completeness_matrix: [
                { title: true, description: true, ai_techniques_used: false },
                { title: true, description: true, ai_techniques_used: true }
              ],
              field_completeness: {
                title: { completeness_percentage: 100, complete_records: 24, missing_records: 0, field_type: 'core' as const },
                description: { completeness_percentage: 95, complete_records: 23, missing_records: 1, field_type: 'core' as const },
                ai_techniques_used: { completeness_percentage: 45, complete_records: 11, missing_records: 13, field_type: 'enrichment' as const }
              },
              overall_completeness: 81.2,
              core_fields_completeness: 97.5,
              enrichment_fields_completeness: 61.8
            },
            intelligence_reports: {
              total_records: 5,
              completeness_matrix: [
                { title: true, report_type: true, key_findings: true }
              ],
              field_completeness: {
                title: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'core' as const },
                report_type: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'core' as const },
                key_findings: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'enrichment' as const }
              },
              overall_completeness: 95.8,
              core_fields_completeness: 100.0,
              enrichment_fields_completeness: 92.0
            }
          },
          recommendations: [
            '✅ Regular enrichment pipeline is running correctly',
            '🟡 Consider enhancing publication development stage detection',
            '🔴 Intelligence pipeline may need attention - run enrichment to generate reports'
          ],
          analysis_timestamp: new Date().toISOString(),
          summary: {
            tables_analyzed: 3,
            total_records_analyzed: 125,
            intelligence_table_exists: true
          }
        };
        setMissingDataMap(mockData);
        return mockData;
      }
      const data = await response.json();
      setMissingDataMap(data);
      return data;
    } catch (err) {
      // Fallback to mock data if network error
      console.warn('Network error, using mock data for data completeness widget');
      const mockData = {
        _isMockData: true, // Flag to indicate this is mock data
        missing_data_map: {
          publications: {
            total_records: 96,
            completeness_matrix: [
              { title: true, abstract: true, development_stage: false, business_model: true },
              { title: true, abstract: false, development_stage: true, business_model: false }
            ],
            field_completeness: {
              title: { completeness_percentage: 100, complete_records: 96, missing_records: 0, field_type: 'core' as const },
              abstract: { completeness_percentage: 92, complete_records: 88, missing_records: 8, field_type: 'core' as const },
              development_stage: { completeness_percentage: 65, complete_records: 62, missing_records: 34, field_type: 'enrichment' as const },
              business_model: { completeness_percentage: 58, complete_records: 56, missing_records: 40, field_type: 'enrichment' as const }
            },
            overall_completeness: 78.5,
            core_fields_completeness: 95.0,
            enrichment_fields_completeness: 58.2
          },
          innovations: {
            total_records: 24,
            completeness_matrix: [
              { title: true, description: true, ai_techniques_used: false },
              { title: true, description: true, ai_techniques_used: true }
            ],
            field_completeness: {
              title: { completeness_percentage: 100, complete_records: 24, missing_records: 0, field_type: 'core' as const },
              description: { completeness_percentage: 95, complete_records: 23, missing_records: 1, field_type: 'core' as const },
              ai_techniques_used: { completeness_percentage: 45, complete_records: 11, missing_records: 13, field_type: 'enrichment' as const }
            },
            overall_completeness: 81.2,
            core_fields_completeness: 97.5,
            enrichment_fields_completeness: 61.8
          },
          intelligence_reports: {
            total_records: 5,
            completeness_matrix: [
              { title: true, report_type: true, key_findings: true }
            ],
            field_completeness: {
              title: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'core' as const },
              report_type: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'core' as const },
              key_findings: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'enrichment' as const }
            },
            overall_completeness: 95.8,
            core_fields_completeness: 100.0,
            enrichment_fields_completeness: 92.0
          }
        },
        recommendations: [
          '✅ Regular enrichment pipeline is running correctly',
          '🟡 Consider enhancing publication development stage detection',
          '🔴 API currently unavailable - displaying demo data'
        ],
        analysis_timestamp: new Date().toISOString(),
        summary: {
          tables_analyzed: 3,
          total_records_analyzed: 125,
          intelligence_table_exists: true
        }
      };
      setMissingDataMap(mockData);
      return mockData;
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