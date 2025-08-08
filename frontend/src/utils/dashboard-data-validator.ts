/**
 * Dashboard Data Validator
 * Validates that dashboard components are using real data from backend APIs
 */

import { API_ENDPOINTS, apiClient } from '@/lib/api-client'

export interface DataValidationResult {
  endpoint: string
  status: 'success' | 'error' | 'fallback'
  hasRealData: boolean
  dataPoints: number
  error?: string
  lastUpdated?: string
}

export interface DashboardValidationReport {
  overallStatus: 'healthy' | 'degraded' | 'critical'
  timestamp: string
  results: DataValidationResult[]
  summary: {
    totalEndpoints: number
    successfulEndpoints: number
    fallbackEndpoints: number
    failedEndpoints: number
    realDataPercentage: number
  }
}

export class DashboardDataValidator {
  private async validateEndpoint(
    endpoint: string, 
    expectedFields: string[] = []
  ): Promise<DataValidationResult> {
    try {
      const startTime = Date.now()
      const data = await apiClient.get(endpoint)
      const responseTime = Date.now() - startTime

      // Check if data exists and has expected structure
      const hasRealData = this.hasRealData(data, expectedFields)
      const dataPoints = this.countDataPoints(data)

      return {
        endpoint,
        status: hasRealData ? 'success' : 'fallback',
        hasRealData,
        dataPoints,
        lastUpdated: new Date().toISOString()
      }
    } catch (error) {
      return {
        endpoint,
        status: 'error',
        hasRealData: false,
        dataPoints: 0,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  private hasRealData(data: any, expectedFields: string[]): boolean {
    if (!data || typeof data !== 'object') return false

    // Check for mock data indicators
    if (data._isMockData || data.mock || data.demo) return false

    // Check if expected fields exist and have meaningful values
    for (const field of expectedFields) {
      const value = this.getNestedValue(data, field)
      if (value === undefined || value === null || value === 0) {
        continue // Some fields might legitimately be 0
      }
    }

    // Check for meaningful data counts
    if (data.total_innovations > 0 || data.total_publications > 0 || 
        data.total_organizations > 0 || data.length > 0) {
      return true
    }

    return false
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj)
  }

  private countDataPoints(data: any): number {
    if (Array.isArray(data)) return data.length
    if (typeof data === 'object' && data !== null) {
      let count = 0
      for (const key in data) {
        if (typeof data[key] === 'number' && data[key] > 0) count++
        if (Array.isArray(data[key])) count += data[key].length
      }
      return count
    }
    return 0
  }

  async validateDashboard(): Promise<DashboardValidationReport> {
    const validationPromises = [
      // Core dashboard stats
      this.validateEndpoint(API_ENDPOINTS.stats, [
        'total_innovations', 'total_publications', 'total_organizations'
      ]),

      // Analytics endpoints
      this.validateEndpoint(API_ENDPOINTS.analytics.innovations, [
        'summary.total_innovations', 'by_country', 'timeline'
      ]),
      
      this.validateEndpoint(API_ENDPOINTS.analytics.publications, [
        'summary.total_publications', 'by_source', 'trending_keywords'
      ]),

      // Trends endpoints
      this.validateEndpoint(API_ENDPOINTS.trends.lifecycles, []),
      this.validateEndpoint(API_ENDPOINTS.trends.domains, []),
      this.validateEndpoint(API_ENDPOINTS.trends.focusAreas, []),

      // Data Intelligence endpoints
      this.validateEndpoint(API_ENDPOINTS.dataIntelligence.citationAnalytics, []),
      this.validateEndpoint(API_ENDPOINTS.dataIntelligence.publicationIntelligence, []),

      // ETL status
      this.validateEndpoint(API_ENDPOINTS.etl.status, [
        'academic_pipeline_active', 'total_processed_today'
      ])
    ]

    const results = await Promise.all(validationPromises)

    // Calculate summary statistics
    const totalEndpoints = results.length
    const successfulEndpoints = results.filter(r => r.status === 'success').length
    const fallbackEndpoints = results.filter(r => r.status === 'fallback').length
    const failedEndpoints = results.filter(r => r.status === 'error').length
    const realDataPercentage = Math.round((successfulEndpoints / totalEndpoints) * 100)

    // Determine overall status
    let overallStatus: 'healthy' | 'degraded' | 'critical'
    if (realDataPercentage >= 80) {
      overallStatus = 'healthy'
    } else if (realDataPercentage >= 50) {
      overallStatus = 'degraded'
    } else {
      overallStatus = 'critical'
    }

    return {
      overallStatus,
      timestamp: new Date().toISOString(),
      results,
      summary: {
        totalEndpoints,
        successfulEndpoints,
        fallbackEndpoints,
        failedEndpoints,
        realDataPercentage
      }
    }
  }

  async validateSpecificComponent(componentName: string): Promise<DataValidationResult[]> {
    switch (componentName.toLowerCase()) {
      case 'realtimeanalytics':
        return Promise.all([
          this.validateEndpoint(API_ENDPOINTS.analytics.innovations),
          this.validateEndpoint(API_ENDPOINTS.analytics.publications),
          this.validateEndpoint(API_ENDPOINTS.analytics.etlPerformance)
        ])

      case 'researchtoinnovationpipeline':
        return Promise.all([
          this.validateEndpoint(API_ENDPOINTS.stats),
          this.validateEndpoint(API_ENDPOINTS.dataIntelligence.citationAnalytics),
          this.validateEndpoint(API_ENDPOINTS.trends.lifecycles),
          this.validateEndpoint(API_ENDPOINTS.trends.timeToMarket)
        ])

      case 'collaborationheatmap':
        return Promise.all([
          this.validateEndpoint(API_ENDPOINTS.stats),
          this.validateEndpoint(API_ENDPOINTS.dataIntelligence.publicationIntelligence),
          this.validateEndpoint(API_ENDPOINTS.trends.successPatterns),
          this.validateEndpoint(API_ENDPOINTS.dataIntelligence.collaborationOpportunities)
        ])

      case 'technologyadoptioncurves':
        return Promise.all([
          this.validateEndpoint(API_ENDPOINTS.trends.domains),
          this.validateEndpoint(API_ENDPOINTS.trends.emerging),
          this.validateEndpoint(API_ENDPOINTS.trends.focusAreas),
          this.validateEndpoint(API_ENDPOINTS.stats)
        ])

      default:
        throw new Error(`Unknown component: ${componentName}`)
    }
  }

  generateReport(report: DashboardValidationReport): string {
    const { overallStatus, summary, results } = report
    
    let reportText = `
# Dashboard Data Validation Report
Generated: ${new Date(report.timestamp).toLocaleString()}

## Overall Status: ${overallStatus.toUpperCase()}
- Real Data Coverage: ${summary.realDataPercentage}%
- Successful Endpoints: ${summary.successfulEndpoints}/${summary.totalEndpoints}
- Fallback Endpoints: ${summary.fallbackEndpoints}
- Failed Endpoints: ${summary.failedEndpoints}

## Endpoint Details:
`

    results.forEach(result => {
      const statusIcon = result.status === 'success' ? '✅' : 
                        result.status === 'fallback' ? '⚠️' : '❌'
      
      reportText += `
${statusIcon} ${result.endpoint}
   Status: ${result.status}
   Real Data: ${result.hasRealData ? 'Yes' : 'No'}
   Data Points: ${result.dataPoints}
   ${result.error ? `Error: ${result.error}` : ''}
`
    })

    return reportText
  }
}

// Export singleton instance
export const dashboardValidator = new DashboardDataValidator()