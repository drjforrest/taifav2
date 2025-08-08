'use client'

import { DashboardValidationReport, dashboardValidator } from '@/utils/dashboard-data-validator'
import { Activity, AlertTriangle, CheckCircle, Database, RefreshCw, XCircle } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function DataValidationPanel() {
  const [report, setReport] = useState<DashboardValidationReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    runValidation()
  }, [])

  const runValidation = async () => {
    setLoading(true)
    try {
      const validationReport = await dashboardValidator.validateDashboard()
      setReport(validationReport)
    } catch (error) {
      console.error('Validation failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'fallback':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Database className="h-4 w-4 text-gray-600" />
    }
  }

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'degraded':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  if (!report && !loading) {
    return null
  }

  return (
    <div className="mb-8">
      <div 
        className={`p-4 rounded-lg border cursor-pointer transition-all ${
          report ? getOverallStatusColor(report.overallStatus) : 'bg-gray-50 border-gray-200'
        }`}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="h-5 w-5" />
            <div>
              <h3 className="font-semibold">
                Dashboard Data Validation
                {report && (
                  <span className="ml-2 text-sm font-normal">
                    ({report.summary.realDataPercentage}% real data)
                  </span>
                )}
              </h3>
              <p className="text-sm opacity-75">
                {loading ? 'Validating data connections...' : 
                 report ? `Status: ${report.overallStatus} - ${report.summary.successfulEndpoints}/${report.summary.totalEndpoints} endpoints healthy` :
                 'Click to validate data connections'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {loading && <RefreshCw className="h-4 w-4 animate-spin" />}
            <button
              onClick={(e) => {
                e.stopPropagation()
                runValidation()
              }}
              className="px-3 py-1 text-xs rounded border hover:bg-white/50 transition-colors"
              disabled={loading}
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {expanded && report && (
        <div className="mt-4 space-y-4">
          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-white rounded border">
              <div className="text-2xl font-bold text-green-600">
                {report.summary.successfulEndpoints}
              </div>
              <div className="text-sm text-gray-600">Successful</div>
            </div>
            <div className="p-3 bg-white rounded border">
              <div className="text-2xl font-bold text-yellow-600">
                {report.summary.fallbackEndpoints}
              </div>
              <div className="text-sm text-gray-600">Fallback</div>
            </div>
            <div className="p-3 bg-white rounded border">
              <div className="text-2xl font-bold text-red-600">
                {report.summary.failedEndpoints}
              </div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="p-3 bg-white rounded border">
              <div className="text-2xl font-bold text-blue-600">
                {report.summary.realDataPercentage}%
              </div>
              <div className="text-sm text-gray-600">Real Data</div>
            </div>
          </div>

          {/* Detailed Results */}
          <div className="bg-white rounded border">
            <div className="p-4 border-b">
              <h4 className="font-semibold">Endpoint Details</h4>
            </div>
            <div className="divide-y">
              {report.results.map((result, index) => (
                <div key={index} className="p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(result.status)}
                    <div>
                      <div className="font-medium text-sm">
                        {result.endpoint.replace(/^.*\/api\//, '/api/')}
                      </div>
                      <div className="text-xs text-gray-500">
                        {result.dataPoints} data points
                        {result.error && ` • Error: ${result.error}`}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-xs px-2 py-1 rounded ${
                      result.hasRealData ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {result.hasRealData ? 'Real Data' : 'Mock/Fallback'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {report.overallStatus !== 'healthy' && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded">
              <h4 className="font-semibold text-blue-800 mb-2">Recommendations</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                {report.summary.failedEndpoints > 0 && (
                  <li>• Check backend API server status and connectivity</li>
                )}
                {report.summary.fallbackEndpoints > 0 && (
                  <li>• Some endpoints are returning empty data - consider running ETL pipelines</li>
                )}
                {report.summary.realDataPercentage < 50 && (
                  <li>• Low real data coverage - run data collection and enrichment processes</li>
                )}
                <li>• Use the ETL monitoring tab to trigger data collection pipelines</li>
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}