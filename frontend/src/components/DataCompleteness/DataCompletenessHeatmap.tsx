'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, RefreshCw, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

interface FieldCompleteness {
  completeness_percentage: number;
  complete_records: number;
  missing_records: number;
  field_type: 'core' | 'enrichment';
}

interface TableAnalysis {
  total_records: number;
  completeness_matrix: Record<string, boolean>[];
  field_completeness: Record<string, FieldCompleteness>;
  overall_completeness: number;
  core_fields_completeness: number;
  enrichment_fields_completeness: number;
  error?: string;
}

interface MissingDataMap {
  missing_data_map: Record<string, TableAnalysis>;
  recommendations: string[];
  analysis_timestamp: string;
  summary: {
    tables_analyzed: number;
    total_records_analyzed: number;
    intelligence_table_exists: boolean;
  };
}

interface CriticalGap {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  impact: string;
  affected_records: number;
  recommended_action: string;
}

interface EnrichmentGaps {
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

const DataCompletenessHeatmap: React.FC = () => {
  const [missingDataMap, setMissingDataMap] = useState<MissingDataMap | null>(null);
  const [enrichmentGaps, setEnrichmentGaps] = useState<EnrichmentGaps | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<string>('publications');

  const fetchMissingDataMap = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/data-completeness/intelligence-enrichment/missing-data-map');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setMissingDataMap(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch missing data map');
    }
  };

  const fetchEnrichmentGaps = async () => {
    try {
      const response = await fetch('/api/data-completeness/enrichment-gaps/analysis');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      setEnrichmentGaps(data);
    } catch (err) {
      console.error('Failed to fetch enrichment gaps:', err);
    }
  };

  useEffect(() => {
    fetchMissingDataMap();
    fetchEnrichmentGaps();
  }, []);

  const getCompletenessColor = (percentage: number): string => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    if (percentage >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getCompletenessColorClass = (percentage: number): string => {
    if (percentage >= 80) return 'text-green-700 bg-green-100';
    if (percentage >= 60) return 'text-yellow-700 bg-yellow-100';
    if (percentage >= 40) return 'text-orange-700 bg-orange-100';
    return 'text-red-700 bg-red-100';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'high': return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'medium': return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      default: return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  const renderDotMatrix = (tableData: TableAnalysis) => {
    const { completeness_matrix, field_completeness } = tableData;
    const fields = Object.keys(field_completeness);
    const maxRecords = Math.min(completeness_matrix.length, 50); // Limit for performance
    
    return (
      <div className="space-y-2">
        <div className="text-sm font-medium mb-2">
          Data Completeness Matrix (showing {maxRecords} of {completeness_matrix.length} records)
        </div>
        
        {/* Field headers */}
        <div className="flex gap-1 items-end mb-2">
          <div className="w-12 text-xs">Record</div>
          {fields.map((field, idx) => (
            <div
              key={field}
              className="w-3 text-xs transform -rotate-90 origin-bottom-left whitespace-nowrap"
              style={{ height: '60px' }}
              title={field}
            >
              {field.substring(0, 8)}
            </div>
          ))}
        </div>
        
        {/* Data matrix */}
        <div className="space-y-1">
          {completeness_matrix.slice(0, maxRecords).map((record, recordIdx) => (
            <div key={recordIdx} className="flex gap-1 items-center">
              <div className="w-12 text-xs text-gray-500">#{recordIdx + 1}</div>
              {fields.map((field) => (
                <div
                  key={`${recordIdx}-${field}`}
                  className={`w-3 h-3 rounded-sm ${
                    record[field] 
                      ? 'bg-green-400' 
                      : 'bg-red-300'
                  }`}
                  title={`${field}: ${record[field] ? 'Present' : 'Missing'}`}
                />
              ))}
            </div>
          ))}
        </div>
        
        {/* Legend */}
        <div className="flex gap-4 text-xs text-gray-600 mt-2">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-400 rounded-sm" />
            Present
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-300 rounded-sm" />
            Missing
          </div>
        </div>
      </div>
    );
  };

  const renderFieldCompleteness = (tableData: TableAnalysis) => {
    const { field_completeness } = tableData;
    const coreFields = Object.entries(field_completeness).filter(([_, data]) => data.field_type === 'core');
    const enrichmentFields = Object.entries(field_completeness).filter(([_, data]) => data.field_type === 'enrichment');
    
    return (
      <div className="space-y-4">
        {coreFields.length > 0 && (
          <div>
            <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
              Core Fields
              <Badge variant="outline" className="text-xs">Required</Badge>
            </h4>
            <div className="space-y-1">
              {coreFields.map(([field, data]) => (
                <div key={field} className="flex justify-between items-center">
                  <span className="text-sm font-mono">{field}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getCompletenessColor(data.completeness_percentage)}`}
                        style={{ width: `${data.completeness_percentage}%` }}
                      />
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${getCompletenessColorClass(data.completeness_percentage)}`}>
                      {data.completeness_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {enrichmentFields.length > 0 && (
          <div>
            <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
              Enrichment Fields
              <Badge variant="outline" className="text-xs">AI Enhanced</Badge>
            </h4>
            <div className="space-y-1">
              {enrichmentFields.map(([field, data]) => (
                <div key={field} className="flex justify-between items-center">
                  <span className="text-sm font-mono">{field}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getCompletenessColor(data.completeness_percentage)}`}
                        style={{ width: `${data.completeness_percentage}%` }}
                      />
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${getCompletenessColorClass(data.completeness_percentage)}`}>
                      {data.completeness_percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading && !missingDataMap) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        <span>Loading data completeness analysis...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertCircle className="h-4 w-4 text-red-500" />
        <AlertDescription className="text-red-700">
          Error: {error}
        </AlertDescription>
      </Alert>
    );
  }

  if (!missingDataMap) {
    return (
      <Alert>
        <AlertDescription>
          No data available. Click refresh to load the analysis.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Intelligence Enrichment Analysis</h2>
          <p className="text-gray-600">
            Data completeness analysis for {missingDataMap.summary.total_records_analyzed} records 
            across {missingDataMap.summary.tables_analyzed} tables
          </p>
        </div>
        <Button
          onClick={() => {
            fetchMissingDataMap();
            fetchEnrichmentGaps();
          }}
          disabled={loading}
          variant="outline"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <RefreshCw className="w-4 h-4 mr-2" />
          )}
          Refresh
        </Button>
      </div>

      {/* Critical Issues Alert */}
      {!missingDataMap.summary.intelligence_table_exists && (
        <Alert className="border-red-200 bg-red-50">
          <XCircle className="h-4 w-4 text-red-500" />
          <AlertDescription className="text-red-700">
            <strong>Critical Issue:</strong> No intelligence reports found. The intelligence enrichment pipeline appears to be inactive.
          </AlertDescription>
        </Alert>
      )}

      {/* Recommendations */}
      {missingDataMap.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-orange-500" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {missingDataMap.recommendations.map((recommendation, idx) => (
                <div key={idx} className="flex items-start gap-2 p-2 bg-orange-50 rounded">
                  <span className="text-sm">{recommendation}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Critical Gaps */}
      {enrichmentGaps?.gaps_analysis.critical_missing_data && (
        <Card>
          <CardHeader>
            <CardTitle>Critical Missing Data</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {enrichmentGaps.gaps_analysis.critical_missing_data.map((gap, idx) => (
                <div key={idx} className="border rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getSeverityIcon(gap.severity)}
                      <span className="font-medium">{gap.type.replace('_', ' ')}</span>
                      <Badge variant={gap.severity === 'critical' ? 'destructive' : 'secondary'}>
                        {gap.severity}
                      </Badge>
                    </div>
                    <span className="text-sm text-gray-500">
                      {gap.affected_records} affected
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{gap.description}</p>
                  <p className="text-sm text-blue-700 font-medium">{gap.recommended_action}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Table Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Table Analysis</CardTitle>
          <div className="flex gap-2">
            {Object.keys(missingDataMap.missing_data_map).map((tableName) => (
              <Button
                key={tableName}
                variant={selectedTable === tableName ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedTable(tableName)}
              >
                {tableName} ({missingDataMap.missing_data_map[tableName].total_records})
              </Button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          {(() => {
            const tableData = missingDataMap.missing_data_map[selectedTable];
            
            if (tableData.error) {
              return (
                <Alert className="border-red-200 bg-red-50">
                  <XCircle className="h-4 w-4 text-red-500" />
                  <AlertDescription className="text-red-700">
                    Error analyzing {selectedTable}: {tableData.error}
                  </AlertDescription>
                </Alert>
              );
            }

            if (tableData.total_records === 0) {
              return (
                <Alert>
                  <AlertDescription>
                    No data found in {selectedTable} table.
                  </AlertDescription>
                </Alert>
              );
            }

            return (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Summary Stats */}
                <div className="space-y-4">
                  <h3 className="font-semibold">Completeness Summary</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-blue-50 rounded">
                      <div className="text-2xl font-bold text-blue-700">
                        {tableData.overall_completeness.toFixed(1)}%
                      </div>
                      <div className="text-sm text-blue-600">Overall Completeness</div>
                    </div>
                    <div className="p-3 bg-green-50 rounded">
                      <div className="text-2xl font-bold text-green-700">
                        {tableData.core_fields_completeness.toFixed(1)}%
                      </div>
                      <div className="text-sm text-green-600">Core Fields</div>
                    </div>
                    <div className="p-3 bg-orange-50 rounded">
                      <div className="text-2xl font-bold text-orange-700">
                        {tableData.enrichment_fields_completeness.toFixed(1)}%
                      </div>
                      <div className="text-sm text-orange-600">Enrichment Fields</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="text-2xl font-bold text-gray-700">
                        {tableData.total_records}
                      </div>
                      <div className="text-sm text-gray-600">Total Records</div>
                    </div>
                  </div>
                  
                  {/* Field Completeness */}
                  {renderFieldCompleteness(tableData)}
                </div>

                {/* Dot Matrix */}
                <div className="overflow-auto">
                  {renderDotMatrix(tableData)}
                </div>
              </div>
            );
          })()}
        </CardContent>
      </Card>

      {/* Analysis Timestamp */}
      <div className="text-xs text-gray-500">
        Analysis generated: {new Date(missingDataMap.analysis_timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default DataCompletenessHeatmap;