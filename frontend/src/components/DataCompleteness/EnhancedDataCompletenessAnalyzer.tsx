'use client';

import Button from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import {
  useEnhancedDataCompleteness,
  type RecordAnalysis
} from '@/hooks/useEnhancedDataCompleteness';
import {
  AlertCircle,
  AlertTriangle,
  BarChart3,
  CheckCircle,
  Clock,
  Database,
  Eye,
  Filter,
  Loader2,
  RefreshCw,
  TrendingUp,
  XCircle
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

const EnhancedDataCompletenessAnalyzer: React.FC = () => {
  const {
    recordAnalysis: analysisData,
    problematicRecords,
    loading,
    error,
    selectedTable,
    setSelectedTable,
    fetchRecordAnalysis,
    fetchProblematicRecords,
    refresh
  } = useEnhancedDataCompleteness({
    autoFetch: true,
    defaultTable: 'publications'
  });

  const [activeTab, setActiveTab] = useState<'overview' | 'patterns' | 'records' | 'problematic'>('overview');
  const [selectedRecord, setSelectedRecord] = useState<RecordAnalysis | null>(null);
  const [minMissingFields, setMinMissingFields] = useState(3);

  const tables = ['publications', 'innovations', 'intelligence_reports'];

  useEffect(() => {
    if (activeTab === 'problematic') {
      fetchProblematicRecords(selectedTable, { minMissingFields, sortBy: 'missing_percentage' });
    }
  }, [activeTab, selectedTable, minMissingFields, fetchProblematicRecords]);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'high': return <AlertCircle className="w-4 h-4 text-orange-500" />;
      case 'medium': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const renderOverview = () => {
    if (!analysisData) return null;

    const { record_analysis, schema_info } = analysisData;
    const avgMissingFields = record_analysis.reduce((sum: number, r: any) => sum + r.missing_fields_count, 0) / record_analysis.length;
    const avgCompleteness = record_analysis.reduce((sum: number, r: any) => sum + r.completeness_score, 0) / record_analysis.length;

    return (
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex flex-col justify-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Records</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{analysisData.total_records}</p>
                </div>
                <div className="flex items-center justify-center">
                  <Database className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex flex-col justify-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Completeness</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{avgCompleteness.toFixed(1)}%</p>
                </div>
                <div className="flex items-center justify-center">
                  <BarChart3 className="w-8 h-8 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex flex-col justify-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Missing Fields</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{avgMissingFields.toFixed(1)}</p>
                </div>
                <div className="flex items-center justify-center">
                  <AlertCircle className="w-8 h-8 text-orange-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex flex-col justify-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Fields</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{schema_info.total_fields}</p>
                </div>
                <div className="flex items-center justify-center">
                  <Filter className="w-8 h-8 text-purple-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Field Completeness Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle>Field Completeness Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2 text-gray-900 dark:text-white">Core Fields</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {schema_info.core_fields.map((field: string) => {
                    const missingCount = record_analysis.filter((r: any) => r.missing_fields.includes(field)).length;
                    const completeness = ((record_analysis.length - missingCount) / record_analysis.length) * 100;
                    return (
                      <div key={field} className="p-2 border border-gray-200 dark:border-gray-600 rounded">
                        <div className="text-xs font-mono mb-1 text-gray-700 dark:text-gray-300">{field}</div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                completeness >= 80 ? 'bg-green-500' :
                                completeness >= 60 ? 'bg-yellow-500' :
                                completeness >= 40 ? 'bg-orange-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${completeness}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-600 dark:text-gray-400">{completeness.toFixed(0)}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2 text-gray-900 dark:text-white">Enrichment Fields</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {schema_info.enrichment_fields.map((field: string) => {
                    const missingCount = record_analysis.filter((r: any) => r.missing_fields.includes(field)).length;
                    const completeness = ((record_analysis.length - missingCount) / record_analysis.length) * 100;
                    return (
                      <div key={field} className="p-2 border border-gray-200 dark:border-gray-600 rounded">
                        <div className="text-xs font-mono mb-1 text-gray-700 dark:text-gray-300">{field}</div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                completeness >= 80 ? 'bg-green-500' :
                                completeness >= 60 ? 'bg-yellow-500' :
                                completeness >= 40 ? 'bg-orange-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${completeness}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-600 dark:text-gray-400">{completeness.toFixed(0)}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderPatterns = () => {
    if (!analysisData?.pattern_analysis) return null;

    const { pattern_analysis } = analysisData;

    return (
      <div className="space-y-6">
        {/* Systematic Issues */}
        {pattern_analysis.systematic_issues.issues.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-500" />
                Systematic Issues ({pattern_analysis.systematic_issues.total_issues})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {pattern_analysis.systematic_issues.issues.map((issue: any, idx: number) => (
                  <div key={idx} className={`p-3 border border-gray-200 dark:border-gray-600 rounded ${getSeverityColor(issue.severity)}`}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getSeverityIcon(issue.severity)}
                        <span className="font-medium text-gray-900 dark:text-white">{issue.field}</span>
                        <Badge variant={issue.severity === 'critical' ? 'destructive' : 'secondary'}>
                          {issue.severity}
                        </Badge>
                      </div>
                      <span className="text-sm font-mono">{issue.missing_percentage.toFixed(1)}%</span>
                    </div>
                    <p className="text-sm mb-1 text-gray-700 dark:text-gray-300">{issue.description}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 italic">{issue.likely_cause}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Field Correlations */}
        {pattern_analysis.field_correlations.strong_correlations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-500" />
                Field Correlations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {pattern_analysis.field_correlations.strong_correlations.map((corr: any, idx: number) => (
                  <div key={idx} className="p-3 border border-gray-200 dark:border-gray-600 rounded">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm text-gray-700 dark:text-gray-300">{corr.field1}</span>
                        <span className="text-gray-400 dark:text-gray-500">↔</span>
                        <span className="font-mono text-sm text-gray-700 dark:text-gray-300">{corr.field2}</span>
                        {corr.likely_systematic && (
                          <Badge variant="destructive" className="text-xs">Systematic</Badge>
                        )}
                      </div>
                      <span className="text-sm font-bold">{(corr.correlation_strength * 100).toFixed(1)}%</span>
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      Missing together in {corr.co_missing_count} records
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Missing Clusters */}
        {pattern_analysis.missing_clusters.common_patterns.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Common Missing Data Patterns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {pattern_analysis.missing_clusters.common_patterns.map((pattern: any, idx: number) => (
                  <div key={idx} className="p-3 border border-gray-200 dark:border-gray-600 rounded">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-white">{pattern.record_count} records</span>
                        {pattern.likely_systematic && (
                          <Badge variant="destructive" className="text-xs">Systematic</Badge>
                        )}
                      </div>
                      <span className="text-sm">{pattern.percentage.toFixed(1)}%</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {pattern.missing_fields.map((field: string) => (
                        <Badge key={field} variant="outline" className="text-xs">
                          {field}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Temporal Patterns */}
        {pattern_analysis.temporal_patterns.has_temporal_data && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-purple-500" />
                Temporal Patterns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {pattern_analysis.temporal_patterns.patterns.map((period: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-2 border border-gray-200 dark:border-gray-600 rounded">
                    <span className="font-mono text-sm text-gray-700 dark:text-gray-300">{period.period}</span>
                    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span>{period.total_records} records</span>
                      <span>{period.avg_missing_fields.toFixed(1)} avg missing</span>
                      {period.most_missing_field && (
                        <Badge variant="outline" className="text-xs">
                          {period.most_missing_field}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  const renderRecords = () => {
    if (!analysisData) return null;

    const { record_analysis } = analysisData;

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Individual Record Analysis</h3>
          <span className="text-sm text-gray-600 dark:text-gray-400">{record_analysis.length} records</span>
        </div>

        <div className="grid gap-3 max-h-96 overflow-y-auto">
          {record_analysis.slice(0, 50).map((record: any) => (
            <div
              key={record.record_id}
              className={`p-3 border border-gray-200 dark:border-gray-600 rounded cursor-pointer transition-colors ${
                selectedRecord?.record_id === record.record_id 
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
              onClick={() => setSelectedRecord(record)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm">#{record.record_id}</span>
                  <Badge 
                    variant={record.completeness_score >= 80 ? 'default' : 'destructive'}
                    className="text-xs"
                  >
                    {record.completeness_score.toFixed(1)}% complete
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-red-600">
                    {record.missing_fields_count} missing
                  </span>
                  <Eye className="w-4 h-4 text-gray-400" />
                </div>
              </div>
              
              {record.missing_fields.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {record.missing_fields.slice(0, 5).map((field: string) => (
                    <Badge key={field} variant="outline" className="text-xs">
                      {field}
                    </Badge>
                  ))}
                  {record.missing_fields.length > 5 && (
                    <Badge variant="outline" className="text-xs">
                      +{record.missing_fields.length - 5} more
                    </Badge>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Record Detail Modal */}
        {selectedRecord && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Record #{selectedRecord.record_id}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedRecord(null)}
                >
                  Close
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2 text-red-600">
                    Missing Fields ({selectedRecord.missing_fields.length})
                  </h4>
                  <div className="space-y-1">
                    {selectedRecord.missing_core_fields.length > 0 && (
                      <div>
                        <span className="text-xs text-red-700 font-medium">Core:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {selectedRecord.missing_core_fields.map((field: string) => (
                            <Badge key={field} variant="destructive" className="text-xs">
                              {field}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {selectedRecord.missing_enrichment_fields.length > 0 && (
                      <div>
                        <span className="text-xs text-orange-700 font-medium">Enrichment:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {selectedRecord.missing_enrichment_fields.map((field: string) => (
                            <Badge key={field} variant="secondary" className="text-xs">
                              {field}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2 text-green-600">
                    Present Fields ({selectedRecord.present_fields.length})
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {selectedRecord.present_fields.map((field: string) => (
                      <Badge key={field} variant="outline" className="text-xs">
                        {field}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              {selectedRecord.temporal_info && (
                <div className="mt-4 p-2 bg-gray-50 rounded">
                  <span className="text-xs text-gray-600">
                    Date: {selectedRecord.temporal_info.date} 
                    ({selectedRecord.temporal_info.days_ago} days ago)
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  const renderProblematicRecords = () => {
    if (!problematicRecords) return null;

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Most Problematic Records</h3>
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600 dark:text-gray-400">Min missing fields:</label>
            <select
              value={minMissingFields}
              onChange={(e) => setMinMissingFields(Number(e.target.value))}
              className="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value={1}>1+</option>
              <option value={3}>3+</option>
              <option value={5}>5+</option>
              <option value={10}>10+</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600 dark:text-red-400 mb-1">
                  {problematicRecords.summary.total_problematic}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Problematic Records</div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600 dark:text-orange-400 mb-1">
                  {problematicRecords.summary.percentage_problematic.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Of Total Records</div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">
                  {problematicRecords.summary.avg_missing_fields.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Avg Missing Fields</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {problematicRecords.problematic_records.map((record: any) => (
            <div key={record.record_id} className="p-4 border border-gray-200 dark:border-gray-600 rounded">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-gray-700 dark:text-gray-300">#{record.record_id}</span>
                  <Badge variant="destructive">
                    {record.missing_fields_count} missing ({record.missing_percentage.toFixed(1)}%)
                  </Badge>
                </div>
                {record.temporal_info && (
                  <span className="text-xs text-gray-500">
                    {record.temporal_info.days_ago} days ago
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {record.missing_core_fields.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-red-700">Missing Core Fields:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {record.missing_core_fields.map((field: string) => (
                        <Badge key={field} variant="destructive" className="text-xs">
                          {field}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {record.missing_enrichment_fields.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-orange-700">Missing Enrichment Fields:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {record.missing_enrichment_fields.slice(0, 8).map((field: string) => (
                        <Badge key={field} variant="secondary" className="text-xs">
                          {field}
                        </Badge>
                      ))}
                      {record.missing_enrichment_fields.length > 8 && (
                        <Badge variant="secondary" className="text-xs">
                          +{record.missing_enrichment_fields.length - 8} more
                        </Badge>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading && !analysisData) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        <span className="text-gray-600 dark:text-gray-400">Loading enhanced data completeness analysis...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
        <AlertCircle className="h-4 w-4 text-red-500 dark:text-red-400" />
        <AlertDescription className="text-red-700 dark:text-red-300">
          Error: {error}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Enhanced Data Completeness Analysis</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Detailed record-level analysis with pattern detection for missing data
          </p>
        </div>
        <Button
          onClick={() => refresh()}
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

      {/* Table Selection */}
      <div className="flex gap-2">
        {tables.map((table) => (
          <Button
            key={table}
            variant={selectedTable === table ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setSelectedTable(table)}
          >
            {table.replace('_', ' ')}
          </Button>
        ))}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b">
        {[
          { key: 'overview', label: 'Overview', icon: BarChart3 },
          { key: 'patterns', label: 'Patterns', icon: TrendingUp },
          { key: 'records', label: 'Records', icon: Database },
          { key: 'problematic', label: 'Problematic', icon: AlertCircle }
        ].map((tab) => {
          const IconComponent = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600 bg-blue-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <IconComponent className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'patterns' && renderPatterns()}
        {activeTab === 'records' && renderRecords()}
        {activeTab === 'problematic' && renderProblematicRecords()}
      </div>

      {/* Analysis Timestamp */}
      {analysisData && (
        <div className="text-xs text-gray-500 mt-6">
          Analysis generated: {new Date(analysisData.analysis_timestamp).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default EnhancedDataCompletenessAnalyzer;