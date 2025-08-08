'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge, Alert, AlertDescription } from '@/components/ui';
import { Loader2, RefreshCw, AlertCircle, CheckCircle, XCircle, Database, TrendingDown } from 'lucide-react';

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
  };
  actionable_insights: string[];
}

const DataCompletenessWidget: React.FC = () => {
  const [missingDataMap, setMissingDataMap] = useState<MissingDataMap | null>(null);
  const [enrichmentGaps, setEnrichmentGaps] = useState<EnrichmentGaps | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [mapResponse, gapsResponse] = await Promise.all([
        fetch('/api/data-completeness/intelligence-enrichment/missing-data-map'),
        fetch('/api/data-completeness/enrichment-gaps/analysis')
      ]);

      if (!mapResponse.ok) {
        throw new Error(`Missing data map: HTTP ${mapResponse.status}`);
      }
      if (!gapsResponse.ok) {
        throw new Error(`Enrichment gaps: HTTP ${gapsResponse.status}`);
      }

      const mapData = await mapResponse.json();
      const gapsData = await gapsResponse.json();
      
      setMissingDataMap(mapData);
      setEnrichmentGaps(gapsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data completeness');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getCompletenessColor = (percentage: number): string => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    if (percentage >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-green-600 bg-green-100';
    }
  };

  const renderMiniDotMatrix = (tableData: TableAnalysis, maxRows = 10, maxCols = 10) => {
    const { completeness_matrix, field_completeness } = tableData;
    const fields = Object.keys(field_completeness).slice(0, maxCols);
    const records = completeness_matrix.slice(0, maxRows);
    
    return (
      <div className="space-y-1">
        <div className="text-xs font-medium text-gray-600 mb-1">
          Data Matrix ({records.length}×{fields.length})
        </div>
        <div className="space-y-0.5">
          {records.map((record, recordIdx) => (
            <div key={recordIdx} className="flex gap-0.5">
              {fields.map((field) => (
                <div
                  key={`${recordIdx}-${field}`}
                  className={`w-2 h-2 rounded-sm ${
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
      </div>
    );
  };

  if (loading && !missingDataMap) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Data Completeness
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <Loader2 className="w-6 h-6 animate-spin mr-2" />
            <span className="text-sm">Loading analysis...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Data Completeness
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert className="border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <AlertDescription className="text-red-700 text-sm">
              {error}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!missingDataMap) return null;

  const criticalIssues = enrichmentGaps?.gaps_analysis.critical_missing_data.filter(
    gap => gap.severity === 'critical' || gap.severity === 'high'
  ) || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Intelligence Enrichment Status
          </div>
          <Button
            onClick={fetchData}
            disabled={loading}
            variant="outline"
            size="sm"
          >
            {loading ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <RefreshCw className="w-3 h-3" />
            )}
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Critical Status Alert */}
        {!missingDataMap.summary.intelligence_table_exists && (
          <Alert className="border-red-200 bg-red-50">
            <XCircle className="h-4 w-4 text-red-500" />
            <AlertDescription className="text-red-700 text-sm">
              Intelligence pipeline inactive - no reports generated
            </AlertDescription>
          </Alert>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-3">
          {Object.entries(missingDataMap.missing_data_map).map(([tableName, tableData]) => (
            <div key={tableName} className="text-center p-2 bg-gray-50 rounded">
              <div className={`text-lg font-bold ${getCompletenessColor(tableData.enrichment_fields_completeness)}`}>
                {tableData.enrichment_fields_completeness.toFixed(0)}%
              </div>
              <div className="text-xs text-gray-600">{tableName}</div>
              <div className="text-xs text-gray-500">{tableData.total_records} records</div>
            </div>
          ))}
        </div>

        {/* Critical Issues Summary */}
        {criticalIssues.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium text-red-600">
              <AlertCircle className="w-4 h-4" />
              {criticalIssues.length} Critical Issues
            </div>
            <div className="space-y-1">
              {criticalIssues.slice(0, 2).map((issue, idx) => (
                <div key={idx} className="text-xs p-2 bg-red-50 rounded border-l-2 border-red-200">
                  <div className="font-medium text-red-800">{issue.type.replace('_', ' ')}</div>
                  <div className="text-red-600">{issue.description}</div>
                </div>
              ))}
              {criticalIssues.length > 2 && (
                <div className="text-xs text-gray-500">
                  +{criticalIssues.length - 2} more issues
                </div>
              )}
            </div>
          </div>
        )}

        {/* Expandable Detailed View */}
        <div className="space-y-3">
          <Button
            onClick={() => setExpanded(!expanded)}
            variant="outline"
            size="sm"
            className="w-full"
          >
            {expanded ? 'Hide Details' : 'Show Detailed Analysis'}
          </Button>

          {expanded && (
            <div className="space-y-4 border-t pt-4">
              {/* Mini Dot Matrices */}
              <div className="space-y-3">
                {Object.entries(missingDataMap.missing_data_map).map(([tableName, tableData]) => (
                  <div key={tableName} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{tableName}</span>
                      <Badge variant="outline" className="text-xs">
                        {tableData.overall_completeness.toFixed(1)}% complete
                      </Badge>
                    </div>
                    {tableData.total_records > 0 ? (
                      renderMiniDotMatrix(tableData)
                    ) : (
                      <div className="text-xs text-gray-500 italic">No data available</div>
                    )}
                  </div>
                ))}
              </div>

              {/* Top Recommendations */}
              {missingDataMap.recommendations.length > 0 && (
                <div className="space-y-2">
                  <div className="text-sm font-medium">Top Recommendations</div>
                  <div className="space-y-1">
                    {missingDataMap.recommendations.slice(0, 3).map((rec, idx) => (
                      <div key={idx} className="text-xs p-2 bg-blue-50 rounded">
                        {rec.replace(/^🔴|🟡|🟠|✅\s*/, '')}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Analysis Timestamp */}
        <div className="text-xs text-gray-400 text-right">
          Updated: {new Date(missingDataMap.analysis_timestamp).toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
};

export default DataCompletenessWidget;