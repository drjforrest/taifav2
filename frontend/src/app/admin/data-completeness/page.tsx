'use client';

import EnhancedDataCompletenessAnalyzer from '@/components/DataCompleteness/EnhancedDataCompletenessAnalyzer';

export default function DataCompletenessPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Data Completeness Analysis
        </h1>
        <p className="text-gray-600">
          Comprehensive analysis of missing data patterns and record-level completeness
        </p>
      </div>
      
      <EnhancedDataCompletenessAnalyzer />
    </div>
  );
}