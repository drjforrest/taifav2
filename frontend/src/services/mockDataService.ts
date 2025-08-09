/**
 * Mock Data Service
 * Provides fallback data for development and API unavailability scenarios
 */

import { MissingDataMap, EnrichmentGaps } from '@/hooks/useDataCompleteness';

export class MockDataService {
  /**
   * Generate mock missing data map for data completeness analysis
   */
  static getMissingDataMap(): MissingDataMap {
    return {
      missing_data_map: {
        publications: {
          total_records: 96,
          completeness_matrix: [
            { title: true, abstract: true, development_stage: false, business_model: false },
            { title: true, abstract: false, development_stage: true, business_model: false }
          ],
          field_completeness: {
            title: { completeness_percentage: 100, complete_records: 96, missing_records: 0, field_type: 'core' },
            abstract: { completeness_percentage: 92, complete_records: 88, missing_records: 8, field_type: 'core' },
            development_stage: { completeness_percentage: 65, complete_records: 62, missing_records: 34, field_type: 'enrichment' },
            business_model: { completeness_percentage: 58, complete_records: 56, missing_records: 40, field_type: 'enrichment' }
          },
          overall_completeness: 78.5,
          core_fields_completeness: 95.0,
          enrichment_fields_completeness: 58.2
        },
        innovations: {
          total_records: 78,
          completeness_matrix: [
            { title: true, description: true, ai_techniques_used: false },
            { title: true, description: true, ai_techniques_used: true }
          ],
          field_completeness: {
            title: { completeness_percentage: 100, complete_records: 78, missing_records: 0, field_type: 'core' },
            description: { completeness_percentage: 95, complete_records: 74, missing_records: 4, field_type: 'core' },
            ai_techniques_used: { completeness_percentage: 45, complete_records: 35, missing_records: 43, field_type: 'enrichment' }
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
            title: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'core' },
            report_type: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'core' },
            key_findings: { completeness_percentage: 100, complete_records: 5, missing_records: 0, field_type: 'enrichment' }
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
        total_records_analyzed: 179,
        intelligence_table_exists: true
      },
      _isMockData: true
    };
  }

  /**
   * Generate mock enrichment gaps analysis
   */
  static getEnrichmentGaps(): EnrichmentGaps {
    return {
      gaps_analysis: {
        publications_gaps: {
          development_stage: 35,
          business_model: 42,
          funding_info: 68,
          citations: 55
        },
        innovations_gaps: {
          ai_techniques_used: 55,
          market_size: 87,
          funding_status: 58,
          business_model: 64
        },
        intelligence_gaps: {
          reports_exist: true,
          total_reports: 5,
          intelligence_gap_severity: 'medium'
        },
        critical_missing_data: [
          {
            type: 'funding_information',
            severity: 'high',
            description: 'Missing funding information for 68% of publications',
            impact: 'Cannot assess funding landscape accurately',
            affected_records: 65,
            recommended_action: 'Run AI enrichment pipeline to extract funding data'
          },
          {
            type: 'market_sizing',
            severity: 'critical',
            description: 'Missing market size data for 87% of innovations',
            impact: 'Cannot evaluate commercial potential',
            affected_records: 21,
            recommended_action: 'Implement market research data collection'
          }
        ],
        enrichment_priority: [
          {
            task: 'Extract funding information from publications',
            priority_score: 8.5,
            justification: 'High impact on funding analysis with moderate extraction complexity',
            estimated_effort: '2-3 days',
            expected_impact: 'Complete funding landscape visibility'
          },
          {
            task: 'Gather market size data for innovations',
            priority_score: 9.2,
            justification: 'Critical for commercial assessment, requires external data sources',
            estimated_effort: '1 week',
            expected_impact: 'Commercial viability scoring capability'
          }
        ]
      },
      actionable_insights: [
        'Focus on funding data extraction to improve financial analysis',
        'Prioritize market research integration for innovation assessment',
        'Consider automated enrichment pipelines for scalability',
        'Intelligence reports show good coverage but could be expanded'
      ]
    };
  }
}