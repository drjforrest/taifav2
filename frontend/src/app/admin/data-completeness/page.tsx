'use client';

import EnhancedDataCompletenessAnalyzer from '@/components/DataCompleteness/EnhancedDataCompletenessAnalyzer';

export default function DataCompletenessPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Data Completeness Analysis
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Comprehensive analysis of missing data patterns and record-level completeness
          </p>
        </div>
        
        <EnhancedDataCompletenessAnalyzer />
      </div>
    </div>
  );
}
