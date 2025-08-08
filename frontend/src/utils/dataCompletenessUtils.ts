/**
 * Data Completeness Utilities
 * Shared utility functions for data completeness visualization and analysis
 */

/**
 * Color schemes for data completeness visualization
 */
export const CompletenessColors = {
  EXCELLENT: 'bg-green-500',
  GOOD: 'bg-yellow-500', 
  FAIR: 'bg-orange-500',
  POOR: 'bg-red-500'
} as const;

export const CompletenessColorClasses = {
  EXCELLENT: 'text-green-700 bg-green-100',
  GOOD: 'text-yellow-700 bg-yellow-100',
  FAIR: 'text-orange-700 bg-orange-100', 
  POOR: 'text-red-700 bg-red-100'
} as const;

export const CompletenessTextColors = {
  EXCELLENT: 'text-green-600',
  GOOD: 'text-yellow-600',
  FAIR: 'text-orange-600',
  POOR: 'text-red-600'
} as const;

/**
 * Severity colors for critical gap analysis
 */
export const SeverityColors = {
  critical: 'text-red-600 bg-red-100',
  high: 'text-orange-600 bg-orange-100',
  medium: 'text-yellow-600 bg-yellow-100',
  low: 'text-green-600 bg-green-100'
} as const;

/**
 * Icon mappings for severity levels
 */
export const SeverityIcons = {
  critical: 'XCircle',
  high: 'AlertCircle', 
  medium: 'AlertCircle',
  low: 'CheckCircle'
} as const;

/**
 * Determine completeness level based on percentage
 */
export function getCompletenessLevel(percentage: number): keyof typeof CompletenessColors {
  if (percentage >= 80) return 'EXCELLENT';
  if (percentage >= 60) return 'GOOD';
  if (percentage >= 40) return 'FAIR';
  return 'POOR';
}

/**
 * Get background color class for completeness percentage
 */
export function getCompletenessColor(percentage: number): string {
  const level = getCompletenessLevel(percentage);
  return CompletenessColors[level];
}

/**
 * Get color class with background and text for completeness percentage
 */
export function getCompletenessColorClass(percentage: number): string {
  const level = getCompletenessLevel(percentage);
  return CompletenessColorClasses[level];
}

/**
 * Get text color class for completeness percentage
 */
export function getCompletenessTextColor(percentage: number): string {
  const level = getCompletenessLevel(percentage);
  return CompletenessTextColors[level];
}

/**
 * Get color class for severity level
 */
export function getSeverityColor(severity: string): string {
  return SeverityColors[severity as keyof typeof SeverityColors] || SeverityColors.low;
}

/**
 * Get icon name for severity level
 */
export function getSeverityIcon(severity: string): string {
  return SeverityIcons[severity as keyof typeof SeverityIcons] || SeverityIcons.low;
}

/**
 * Format completeness percentage for display
 */
export function formatCompleteness(percentage: number): string {
  return `${percentage.toFixed(1)}%`;
}

/**
 * Calculate overall completeness score from field completeness data
 */
export function calculateOverallCompleteness(
  fieldCompleteness: Record<string, { completeness_percentage: number }>
): number {
  const values = Object.values(fieldCompleteness);
  if (values.length === 0) return 0;
  
  const sum = values.reduce((acc, field) => acc + field.completeness_percentage, 0);
  return sum / values.length;
}

/**
 * Categorize fields by completeness level
 */
export function categorizeFieldsByCompleteness(
  fieldCompleteness: Record<string, { completeness_percentage: number }>
): {
  excellent: string[];
  good: string[];
  fair: string[];
  poor: string[];
} {
  const categories = {
    excellent: [] as string[],
    good: [] as string[],
    fair: [] as string[],
    poor: [] as string[]
  };

  Object.entries(fieldCompleteness).forEach(([fieldName, data]) => {
    const level = getCompletenessLevel(data.completeness_percentage);
    switch (level) {
      case 'EXCELLENT':
        categories.excellent.push(fieldName);
        break;
      case 'GOOD':
        categories.good.push(fieldName);
        break;
      case 'FAIR':
        categories.fair.push(fieldName);
        break;
      case 'POOR':
        categories.poor.push(fieldName);
        break;
    }
  });

  return categories;
}

/**
 * Generate recommendations based on completeness analysis
 */
export function generateRecommendations(
  fieldCompleteness: Record<string, { 
    completeness_percentage: number;
    field_type: 'core' | 'enrichment';
  }>
): string[] {
  const recommendations: string[] = [];
  const categorized = categorizeFieldsByCompleteness(fieldCompleteness);
  
  // Check core fields
  const coreFields = Object.entries(fieldCompleteness)
    .filter(([_, data]) => data.field_type === 'core');
  const poorCoreFields = coreFields
    .filter(([_, data]) => data.completeness_percentage < 60)
    .map(([name]) => name);
    
  if (poorCoreFields.length > 0) {
    recommendations.push(`🔴 Critical: Fix core field completeness for ${poorCoreFields.join(', ')}`);
  }
  
  // Check enrichment fields
  if (categorized.poor.length > 0) {
    recommendations.push(`🟡 Consider enrichment pipeline for ${categorized.poor.length} fields with low completeness`);
  }
  
  if (categorized.excellent.length >= Object.keys(fieldCompleteness).length * 0.8) {
    recommendations.push('✅ Excellent data quality - maintain current standards');
  }
  
  return recommendations;
}