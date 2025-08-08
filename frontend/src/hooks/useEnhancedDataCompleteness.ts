'use client';

import { useCallback, useEffect, useState } from 'react';

export interface FieldAnalysis {
  present: boolean;
  value_type: string | null;
  value_length: number;
}

export interface RecordAnalysis {
  record_id: string;
  missing_fields: string[];
  missing_fields_count: number;
  missing_percentage: number;
  missing_core_fields: string[];
  missing_enrichment_fields: string[];
  present_fields: string[];
  completeness_score: number;
  temporal_info?: {
    date: string;
    days_ago: number;
  };
  field_analysis: Record<string, FieldAnalysis>;
}

export interface FieldCorrelation {
  field1: string;
  field2: string;
  co_missing_count: number;
  correlation_strength: number;
  likely_systematic: boolean;
}

export interface MissingCluster {
  missing_fields: string[];
  record_count: number;
  percentage: number;
  likely_systematic: boolean;
}

export interface SystematicIssue {
  type: string;
  field: string;
  missing_percentage: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  likely_cause: string;
}

export interface PatternAnalysis {
  field_correlations: {
    strong_correlations: FieldCorrelation[];
    total_pairs_analyzed: number;
    systematic_threshold: number;
  };
  missing_clusters: {
    common_patterns: MissingCluster[];
    unique_patterns: number;
    most_common_pattern_count: number;
  };
  temporal_patterns: {
    has_temporal_data: boolean;
    patterns: Array<{
      period: string;
      total_records: number;
      avg_missing_fields: number;
      most_missing_field: string | null;
    }>;
  };
  systematic_issues: {
    issues: SystematicIssue[];
    total_issues: number;
    critical_issues: number;
    high_issues: number;
  };
}

export interface RecordLevelResponse {
  table_name: string;
  total_records: number;
  record_analysis: RecordAnalysis[];
  pattern_analysis: PatternAnalysis;
  analysis_timestamp: string;
  schema_info: {
    core_fields: string[];
    enrichment_fields: string[];
    total_fields: number;
  };
}

export interface ProblematicRecordsResponse {
  table_name: string;
  total_records_analyzed: number;
  problematic_records: RecordAnalysis[];
  summary: {
    total_problematic: number;
    percentage_problematic: number;
    avg_missing_fields: number;
  };
  analysis_timestamp: string;
}

export interface PatternDetectionResponse {
  table_name: string;
  patterns: PatternAnalysis;
  analysis_timestamp: string;
  recommendations: string[];
}

export interface UseEnhancedDataCompletenessOptions {
  autoFetch?: boolean;
  defaultTable?: string;
}

export interface UseEnhancedDataCompletenessReturn {
  // Data
  recordAnalysis: RecordLevelResponse | null;
  problematicRecords: ProblematicRecordsResponse | null;
  patternDetection: PatternDetectionResponse | null;
  
  // State
  loading: boolean;
  error: string | null;
  selectedTable: string;
  
  // Actions
  setSelectedTable: (table: string) => void;
  fetchRecordAnalysis: (table?: string, options?: { limit?: number; includePatterns?: boolean }) => Promise<void>;
  fetchProblematicRecords: (table?: string, options?: { minMissingFields?: number; sortBy?: string }) => Promise<void>;
  fetchPatternDetection: (table?: string, patternType?: string) => Promise<void>;
  refresh: () => Promise<void>;
  
  // Utilities
  getFieldCompleteness: (field: string) => number;
  getRecordsByMissingField: (field: string) => RecordAnalysis[];
  getSystematicIssues: (severity?: string) => SystematicIssue[];
}

import { apiClient } from '@/lib/api-client';

const API_BASE_URL = '/api/enhanced-data-completeness';

export const useEnhancedDataCompleteness = (
  options: UseEnhancedDataCompletenessOptions = {}
): UseEnhancedDataCompletenessReturn => {
  const { autoFetch = true, defaultTable = 'publications' } = options;

  // State
  const [recordAnalysis, setRecordAnalysis] = useState<RecordLevelResponse | null>(null);
  const [problematicRecords, setProblematicRecords] = useState<ProblematicRecordsResponse | null>(null);
  const [patternDetection, setPatternDetection] = useState<PatternDetectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<string>(defaultTable);

  // Fetch record-level analysis
  const fetchRecordAnalysis = useCallback(async (
    table?: string, 
    options: { limit?: number; includePatterns?: boolean } = {}
  ) => {
    const targetTable = table || selectedTable;
    const { limit = 200, includePatterns = true } = options;
    
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        table_name: targetTable,
        limit: limit.toString(),
        include_patterns: includePatterns.toString()
      });
      
      const data = await apiClient.get(`${API_BASE_URL}/record-level-analysis?${params}`) as RecordLevelResponse;
      setRecordAnalysis(data);
      
      // If this is an error response, handle it
      if ((data as any).error) {
        setError((data as any).error);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch record analysis';
      setError(errorMessage);
      console.error('Record analysis fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedTable]);

  // Fetch problematic records
  const fetchProblematicRecords = useCallback(async (
    table?: string,
    options: { minMissingFields?: number; sortBy?: string } = {}
  ) => {
    const targetTable = table || selectedTable;
    const { minMissingFields = 3, sortBy = 'missing_percentage' } = options;
    
    try {
      const params = new URLSearchParams({
        table_name: targetTable,
        min_missing_fields: minMissingFields.toString(),
        sort_by: sortBy
      });
      
      const data = await apiClient.get(`${API_BASE_URL}/problematic-records?${params}`) as ProblematicRecordsResponse;
      setProblematicRecords(data);
      
    } catch (err) {
      console.error('Problematic records fetch error:', err);
      // Don't set main error state for this secondary data
    }
  }, [selectedTable]);

  // Fetch pattern detection
  const fetchPatternDetection = useCallback(async (
    table?: string,
    patternType: string = 'all'
  ) => {
    const targetTable = table || selectedTable;
    
    try {
      const params = new URLSearchParams({
        table_name: targetTable,
        pattern_type: patternType
      });
      
      const data = await apiClient.get(`${API_BASE_URL}/pattern-detection?${params}`) as PatternDetectionResponse;
      setPatternDetection(data);
      
    } catch (err) {
      console.error('Pattern detection fetch error:', err);
      // Don't set main error state for this secondary data
    }
  }, [selectedTable]);

  // Refresh all data
  const refresh = useCallback(async () => {
    await Promise.all([
      fetchRecordAnalysis(),
      fetchProblematicRecords(),
      fetchPatternDetection()
    ]);
  }, [fetchRecordAnalysis, fetchProblematicRecords, fetchPatternDetection]);

  // Utility functions
  const getFieldCompleteness = useCallback((field: string): number => {
    if (!recordAnalysis?.record_analysis) return 0;
    
    const totalRecords = recordAnalysis.record_analysis.length;
    const recordsWithField = recordAnalysis.record_analysis.filter(
      record => record.present_fields.includes(field)
    ).length;
    
    return totalRecords > 0 ? (recordsWithField / totalRecords) * 100 : 0;
  }, [recordAnalysis]);

  const getRecordsByMissingField = useCallback((field: string): RecordAnalysis[] => {
    if (!recordAnalysis?.record_analysis) return [];
    
    return recordAnalysis.record_analysis.filter(
      record => record.missing_fields.includes(field)
    );
  }, [recordAnalysis]);

  const getSystematicIssues = useCallback((severity?: string): SystematicIssue[] => {
    if (!recordAnalysis?.pattern_analysis?.systematic_issues?.issues) return [];
    
    const issues = recordAnalysis.pattern_analysis.systematic_issues.issues;
    
    if (severity) {
      return issues.filter(issue => issue.severity === severity);
    }
    
    return issues;
  }, [recordAnalysis]);

  // Auto-fetch on mount and table change
  useEffect(() => {
    if (autoFetch) {
      fetchRecordAnalysis();
    }
  }, [autoFetch, selectedTable, fetchRecordAnalysis]);

  // Update selected table handler
  const handleSetSelectedTable = useCallback((table: string) => {
    setSelectedTable(table);
    // Clear existing data when changing tables
    setRecordAnalysis(null);
    setProblematicRecords(null);
    setPatternDetection(null);
    setError(null);
  }, []);

  return {
    // Data
    recordAnalysis,
    problematicRecords,
    patternDetection,
    
    // State
    loading,
    error,
    selectedTable,
    
    // Actions
    setSelectedTable: handleSetSelectedTable,
    fetchRecordAnalysis,
    fetchProblematicRecords,
    fetchPatternDetection,
    refresh,
    
    // Utilities
    getFieldCompleteness,
    getRecordsByMissingField,
    getSystematicIssues
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

export const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'critical': return 'text-red-600 bg-red-100 border-red-200';
    case 'high': return 'text-orange-600 bg-orange-100 border-orange-200';
    case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
    default: return 'text-green-600 bg-green-100 border-green-200';
  }
};

export const formatMissingDataInsight = (
  recordAnalysis: RecordLevelResponse | null
): string => {
  if (!recordAnalysis) return 'No analysis available';
  
  const { record_analysis, pattern_analysis } = recordAnalysis;
  const totalRecords = record_analysis.length;
  
  if (totalRecords === 0) return 'No records to analyze';
  
  const avgMissing = record_analysis.reduce((sum, r) => sum + r.missing_fields_count, 0) / totalRecords;
  const criticalIssues = pattern_analysis.systematic_issues.critical_issues;
  const highIssues = pattern_analysis.systematic_issues.high_issues;
  
  if (criticalIssues > 0) {
    return `Critical data quality issues detected: ${criticalIssues} critical, ${highIssues} high priority issues. Average ${avgMissing.toFixed(1)} missing fields per record.`;
  } else if (highIssues > 0) {
    return `Data quality concerns: ${highIssues} high priority issues. Average ${avgMissing.toFixed(1)} missing fields per record.`;
  } else if (avgMissing > 5) {
    return `Moderate data completeness: Average ${avgMissing.toFixed(1)} missing fields per record. Consider running enrichment processes.`;
  } else {
    return `Good data completeness: Average ${avgMissing.toFixed(1)} missing fields per record. Data quality appears healthy.`;
  }
};