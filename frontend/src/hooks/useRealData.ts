/**
 * React Hook for Real Data from ETL Pipeline
 * Manages fetching and caching of live statistics and innovations
 */

import { realDataService, RealStats } from '@/services/realDataService';
import { useCallback, useEffect, useState } from 'react';

export interface UseRealDataState {
  stats: RealStats | null;
  homepageData: any | null;
  innovations: any[] | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export interface UseRealDataActions {
  refetch: () => Promise<void>;
  refreshStats: () => Promise<void>;
  clearError: () => void;
}

export function useRealData(): UseRealDataState & UseRealDataActions {
  const [state, setState] = useState<UseRealDataState>({
    stats: null,
    homepageData: null,
    innovations: null,
    loading: true,
    error: null,
    lastUpdated: null,
  });

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error, loading: false }));
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, loading }));
  }, []);

  const fetchStats = useCallback(async (): Promise<RealStats | null> => {
    try {
      const stats = await realDataService.getStats();
      return stats;
    } catch (error) {
      console.error('Error fetching real stats:', error);
      return null;
    }
  }, []);

  const fetchHomepageData = useCallback(async (): Promise<any | null> => {
    try {
      const homepageData = await realDataService.getHomepageData();
      return homepageData;
    } catch (error) {
      console.error('Error fetching homepage data:', error);
      return null;
    }
  }, []);

  const fetchInnovations = useCallback(async (): Promise<any[] | null> => {
    try {
      const response = await realDataService.getInnovations(10, 0);
      return response.innovations;
    } catch (error) {
      console.error('Error fetching innovations:', error);
      return null;
    }
  }, []);

  const refetch = useCallback(async () => {
    setLoading(true);
    clearError();
    
    try {
      const [stats, homepageData, innovations] = await Promise.all([
        fetchStats(),
        fetchHomepageData(),
        fetchInnovations(),
      ]);

      setState(prev => ({
        ...prev,
        stats,
        homepageData,
        innovations,
        loading: false,
        error: null,
        lastUpdated: new Date(),
      }));
    } catch (error) {
      console.error('Error fetching real data:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch real data');
    }
  }, [fetchStats, fetchHomepageData, fetchInnovations, setError, setLoading, clearError]);

  const refreshStats = useCallback(async () => {
    try {
      const stats = await fetchStats();
      setState(prev => ({
        ...prev,
        stats,
        lastUpdated: new Date(),
      }));
    } catch (error) {
      console.error('Error refreshing stats:', error);
      setError(error instanceof Error ? error.message : 'Failed to refresh stats');
    }
  }, [fetchStats, setError]);

  // Initial data fetch
  useEffect(() => {
    refetch();
  }, [refetch]);

  return {
    ...state,
    refetch,
    refreshStats,
    clearError,
  };
}

// Hook specifically for homepage data with fallback to static data
export function useHomepageData() {
  const { homepageData, stats, loading, error, refetch } = useRealData();
  const [useStaticFallback, setUseStaticFallback] = useState(false);

  // Fallback to static data if real data fails
  useEffect(() => {
    if (error && !homepageData && !stats) {
      console.warn('Real data unavailable, using static fallback');
      setUseStaticFallback(true);
    } else if (homepageData || stats) {
      setUseStaticFallback(false);
    }
  }, [error, homepageData, stats]);

  const getDisplayData = useCallback(() => {
    if (useStaticFallback) {
      // Import and return static data as fallback
      return {
        realTimeData: {
          totalInnovations: 24,
          totalPublications: 96,
          totalOrganizations: 22,
          verifiedInnovations: 20,
          africanCountriesCovered: 44,
          uniqueKeywords: 70,
          verificationRate: 83.3,
        },
        qualityMetrics: {
          avgAfricanRelevance: 0.662,
          avgAIRelevance: 0.817,
          dataFreshness: 'cached',
          pipelineStatus: 'unknown',
        },
        dataQuality: {
          verificationLevel: 'static_fallback',
          lastVerified: new Date().toISOString(),
          confidenceLevel: 'medium',
          source: 'Static fallback data',
          dataFreshness: 'cached',
        },
        isRealData: false,
      };
    }

    return {
      ...homepageData,
      isRealData: true,
    };
  }, [useStaticFallback, homepageData]);

  return {
    data: getDisplayData(),
    stats,
    loading,
    error,
    isRealData: !useStaticFallback,
    refetch,
  };
}

// Lightweight hook just for stats
export function useStats() {
  const [stats, setStats] = useState<RealStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await realDataService.getStats();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
}