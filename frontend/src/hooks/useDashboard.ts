"use client";

import { useEffect, useState } from "react";
import { apiClient, API_ENDPOINTS } from "@/lib/api-client";
import { 
  DashboardStats, 
  RecentActivity, 
  ETLStatus, 
  ETLHealth, 
  ETLMetrics 
} from "@/types/api";

export interface DashboardData extends DashboardStats {
  loading: boolean;
  error: string | null;
  etl_status?: ETLStatus;
}

export interface APIResponse {
  success: boolean;
  message?: string;
  data?: any;
}

export function useDashboard(): DashboardData {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    total_publications: 0,
    total_innovations: 0,
    total_organizations: 0,
    verified_individuals: 0,
    african_countries_covered: 0,
    unique_keywords: 0,
    avg_african_relevance: 0,
    avg_ai_relevance: 0,
    last_updated: "",
    loading: true,
    error: null,
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setDashboardData((prev) => ({ ...prev, loading: true, error: null }));

      // Get dashboard stats from API
      const apiData = await apiClient.get<DashboardStats>(API_ENDPOINTS.stats);
        
      setDashboardData({
        total_publications: apiData.total_publications || 0,
        total_innovations: apiData.total_innovations || 0,
        total_organizations: apiData.total_organizations || 0,
        verified_individuals: apiData.verified_individuals || 0,
        african_countries_covered: apiData.african_countries_covered || 0,
        unique_keywords: apiData.unique_keywords || 0,
        avg_african_relevance: apiData.avg_african_relevance || 0,
        avg_ai_relevance: apiData.avg_ai_relevance || 0,
        last_updated: apiData.last_updated || new Date().toISOString(),
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error("Error fetching dashboard stats:", err);
      setDashboardData((prev) => ({
        ...prev,
        loading: false,
        error:
          err instanceof Error
            ? err.message
            : "Failed to fetch dashboard statistics",
      }));
    }
  };

  return dashboardData;
}

// Hook for getting recent activity
export function useRecentActivity() {
  const [activity, setActivity] = useState({
    recentPublications: [] as any[],
    recentInnovations: [] as any[],
    loading: true,
    error: null as string | null,
  });

  useEffect(() => {
    fetchRecentActivity();
  }, []);

  const fetchRecentActivity = async () => {
    try {
      const activityData = await apiClient.get<RecentActivity>(
        API_ENDPOINTS.recentActivity
      );

      setActivity({
        recentPublications: activityData.recentPublications || [],
        recentInnovations: activityData.recentInnovations || [],
        loading: false,
        error: null,
      });
    } catch (err) {
      console.error("Error fetching recent activity:", err);
      setActivity((prev) => ({
        ...prev,
        loading: false,
        error:
          err instanceof Error
            ? err.message
            : "Failed to fetch recent activity",
      }));
    }
  };

  return activity;
}

// Hook for ETL monitoring and control
export function useETLMonitoring() {
  const [etlData, setETLData] = useState<{
    status: ETLStatus | null;
    health: ETLHealth | null;
    loading: boolean;
    error: string | null;
  }>({
    status: null,
    health: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    fetchETLStatus();
    // Set up polling every 30 seconds
    const interval = setInterval(fetchETLStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchETLStatus = async () => {
    try {
      setETLData(prev => ({ ...prev, loading: true, error: null }));

      // Get ETL status from the backend API
      const etlStatusResponse = await apiClient.get<any>(API_ENDPOINTS.etl.status);
        
      // Handle both wrapped and unwrapped responses
      const responseData = etlStatusResponse.data || etlStatusResponse;
      
      if (responseData && responseData.pipelines) {
        // Parse the actual response structure from the API
        const pipelines = responseData.pipelines;
        
        // Helper function to determine if a pipeline is "active" (running or recently successful)
        const isPipelineActive = (pipeline: any) => {
          if (!pipeline) return false;
          
          // Currently running
          if (pipeline.status === 'running') return true;
          
          // Recently completed successfully (within last 6 hours)
          if (pipeline.last_run && pipeline.status === 'idle') {
            const lastRun = new Date(pipeline.last_run);
            const sixHoursAgo = new Date(Date.now() - 6 * 60 * 60 * 1000);
            return lastRun > sixHoursAgo;
          }
          
          return false;
        };
        
        // Convert backend response to frontend ETLStatus format
        const status: ETLStatus = {
          academic_pipeline_active: isPipelineActive(pipelines.academic_pipeline),
          news_pipeline_active: isPipelineActive(pipelines.news_pipeline),
          serper_pipeline_active: isPipelineActive(pipelines.discovery_pipeline),
          enrichment_pipeline_active: isPipelineActive(pipelines.enrichment_pipeline),
          last_academic_run: pipelines.academic_pipeline?.last_run,
          last_news_run: pipelines.news_pipeline?.last_run,
          last_serper_run: pipelines.discovery_pipeline?.last_run,
          last_enrichment_run: pipelines.enrichment_pipeline?.last_run,
          total_processed_today: responseData.total_processed_today || 0,
          errors_today: responseData.errors_today || 0,
        };

        const health: ETLHealth = {
          status: responseData.system_health === 'healthy' ? 'healthy' : 'degraded',
          last_check: responseData.last_updated || new Date().toISOString(),
          response_time: 150,
        };

        setETLData({
          status,
          health,
          loading: false,
          error: null,
        });
      } else {
        // Default to inactive state when no valid data
        setETLData({
          status: {
            academic_pipeline_active: false,
            news_pipeline_active: false,
            serper_pipeline_active: false,
            enrichment_pipeline_active: false,
            last_academic_run: null,
            last_news_run: null,
            last_serper_run: null,
            last_enrichment_run: null,
            total_processed_today: 0,
            errors_today: 0,
          },
          health: {
            status: "down",
            last_check: new Date().toISOString(),
            response_time: 0,
          },
          loading: false,
          error: "ETL monitoring unavailable",
        });
      }
    } catch (err) {
      console.error("Error fetching ETL status:", err);
      setETLData((prev) => ({
        ...prev,
        loading: false,
        error:
          err instanceof Error ? err.message : "Failed to fetch ETL status",
      }));
    }
  };

  const triggerAcademicPipeline = async () => {
    try {
      const result = await apiClient.post<APIResponse>(API_ENDPOINTS.etl.triggerAcademic);

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return {
          success: true,
          message: result.message || "Academic pipeline triggered successfully",
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger academic pipeline",
        };
      }
    } catch (err) {
      console.error("Error triggering academic pipeline:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger academic pipeline",
      };
    }
  };

  const triggerNewsPipeline = async () => {
    try {
      const result = await apiClient.post<APIResponse>(API_ENDPOINTS.etl.triggerNews);

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return { 
          success: true, 
          message: result.message || "News pipeline triggered successfully" 
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger news pipeline",
        };
      }
    } catch (err) {
      console.error("Error triggering news pipeline:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger news pipeline",
      };
    }
  };

  const triggerSerperSearch = async (query?: string) => {
    try {
      const result = await apiClient.post<APIResponse>(
        API_ENDPOINTS.etl.triggerDiscovery,
        query ? { query } : undefined
      );

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return {
          success: true,
          message: result.message || "Discovery search triggered successfully",
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger discovery search",
        };
      }
    } catch (err) {
      console.error("Error triggering Serper search:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger Serper search",
      };
    }
  };

  const triggerEnrichment = async (
    intelligence_types: string[] = ["innovation_discovery", "funding_landscape"],
    time_period: string = "last_7_days",
    geographic_focus?: string[],
    provider: string = "perplexity",
    enable_snowball_sampling: boolean = true
  ) => {
    try {
      const result = await apiClient.post<APIResponse>(
        API_ENDPOINTS.etl.triggerEnrichment,
        { 
          intelligence_types,
          time_period,
          geographic_focus,
          provider,
          enable_snowball_sampling
        }
      );

      if (result.success) {
        // Refresh status after triggering
        await fetchETLStatus();
        return {
          success: true,
          message: result.message || "AI enrichment triggered successfully",
        };
      } else {
        return {
          success: false,
          message: result.message || "Failed to trigger AI enrichment",
        };
      }
    } catch (err) {
      console.error("Error triggering AI enrichment:", err);
      return {
        success: false,
        message:
          err instanceof Error
            ? err.message
            : "Failed to trigger AI enrichment",
      };
    }
  };

  return {
    status: etlData.status,
    health: etlData.health,
    loading: etlData.loading,
    error: etlData.error,
    triggerAcademicPipeline,
    triggerNewsPipeline,
    triggerSerperSearch,
    triggerEnrichment,
    refresh: fetchETLStatus,
  };
}
