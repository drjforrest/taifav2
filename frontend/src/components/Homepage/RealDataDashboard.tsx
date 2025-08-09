/**
 * Real Data Dashboard Component
 * Displays live statistics from the ETL pipeline
 */

import { useHomepageData } from '@/hooks/useRealData';
import { Activity, CheckCircle, Database, MapPin, TrendingUp, Zap } from 'lucide-react';
import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  isRealTime?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend = 'stable',
  isRealTime = false 
}) => (
  <div
    className="p-6 rounded-2xl border transition-all duration-300 ease-in-out hover:shadow-lg hover:scale-105 hover:-translate-y-1 relative"
    style={{
      backgroundColor: "var(--color-card)",
      borderColor: "var(--color-border)",
    }}
  >
    {isRealTime && (
      <div className="absolute top-3 right-3 flex items-center">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-1" />
        <span className="text-xs font-medium" style={{ color: "var(--color-success)" }}>
          LIVE
        </span>
      </div>
    )}
    
    <div
      className="p-3 rounded-lg mb-4 inline-block"
      style={{
        backgroundColor: "var(--color-primary-background)",
      }}
    >
      <div style={{ color: "var(--color-primary)" }}>
        {icon}
      </div>
    </div>
    
    <h3
      className="text-2xl font-bold mb-2"
      style={{ color: "var(--color-card-foreground)" }}
    >
      {typeof value === 'number' ? value.toLocaleString() : value}
    </h3>
    
    <p
      className="text-sm font-medium mb-1"
      style={{ color: "var(--color-card-foreground)" }}
    >
      {title}
    </p>
    
    {subtitle && (
      <p
        className="text-xs"
        style={{ color: "var(--color-muted-foreground)" }}
      >
        {subtitle}
      </p>
    )}
  </div>
);

const LoadingSkeleton: React.FC = () => (
  <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
    {[...Array(8)].map((_, i) => (
      <div
        key={i}
        className="p-6 rounded-2xl border animate-pulse"
        style={{
          backgroundColor: "var(--color-card)",
          borderColor: "var(--color-border)",
        }}
      >
        <div
          className="w-12 h-12 rounded-lg mb-4"
          style={{ backgroundColor: "var(--color-muted)" }}
        />
        <div
          className="h-8 rounded mb-2"
          style={{ backgroundColor: "var(--color-muted)" }}
        />
        <div
          className="h-4 rounded mb-1"
          style={{ backgroundColor: "var(--color-muted)" }}
        />
        <div
          className="h-3 rounded w-2/3"
          style={{ backgroundColor: "var(--color-muted)" }}
        />
      </div>
    ))}
  </div>
);

const ErrorDisplay: React.FC<{ error: string; onRetry: () => void }> = ({ error, onRetry }) => (
  <div
    className="p-8 rounded-2xl border text-center"
    style={{
      backgroundColor: "var(--color-card)",
      borderColor: "var(--color-destructive)",
    }}
  >
    <div
      className="p-3 rounded-lg mb-4 inline-block"
      style={{
        backgroundColor: "var(--color-destructive-background)",
      }}
    >
      <Activity
        className="h-6 w-6"
        style={{ color: "var(--color-destructive)" }}
      />
    </div>
    
    <h3
      className="text-lg font-semibold mb-2"
      style={{ color: "var(--color-card-foreground)" }}
    >
      Unable to Load Live Data
    </h3>
    
    <p
      className="text-sm mb-4"
      style={{ color: "var(--color-muted-foreground)" }}
    >
      {error}
    </p>
    
    <button
      onClick={onRetry}
      className="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 hover:opacity-90"
      style={{
        backgroundColor: "var(--color-primary)",
        color: "var(--color-primary-foreground)",
      }}
    >
      Retry Connection
    </button>
  </div>
);

export const RealDataDashboard: React.FC = () => {
  const { data, stats, loading, error, isRealData, refetch } = useHomepageData();

  if (loading) {
    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 text-center">
          Loading Live Data...
        </h2>
        <LoadingSkeleton />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 text-center">
          Real-Time Innovation Dashboard
        </h2>
        <ErrorDisplay error={error} onRetry={refetch} />
      </div>
    );
  }

  const realTimeData = data?.realTimeData || {};
  const qualityMetrics = data?.qualityMetrics || {};
  const dataQuality = data?.dataQuality || {};

  return (
    <div>
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <h2 className="text-3xl font-bold">
            Real-Time Innovation Dashboard
          </h2>
          {isRealData && (
            <div className="ml-3 flex items-center px-3 py-1 rounded-full text-sm font-medium"
                 style={{
                   backgroundColor: "var(--color-success-background)",
                   color: "var(--color-success)",
                 }}>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2" />
              LIVE DATA
            </div>
          )}
        </div>
        
        <p className="text-lg max-w-3xl mx-auto" style={{ color: "var(--color-muted-foreground)" }}>
          {isRealData 
            ? "Live statistics from our ETL pipeline with integrated Serper, SerpAPI, and Snowball Sampling"
            : "Displaying cached data - live pipeline temporarily unavailable"
          }
        </p>
        
        {dataQuality.lastVerified && (
          <p className="text-sm mt-2" style={{ color: "var(--color-muted-foreground)" }}>
            Last updated: {new Date(dataQuality.lastVerified).toLocaleString()}
          </p>
        )}
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Innovations"
          value={realTimeData.totalInnovations || 0}
          subtitle="Verified AI innovations"
          icon={<TrendingUp className="h-6 w-6" />}
          isRealTime={isRealData}
        />
        
        <StatCard
          title="Academic Publications"
          value={realTimeData.totalPublications || 0}
          subtitle="Research papers analyzed"
          icon={<Database className="h-6 w-6" />}
          isRealTime={isRealData}
        />
        
        <StatCard
          title="Organizations"
          value={realTimeData.totalOrganizations || 0}
          subtitle="Research & industry partners"
          icon={<CheckCircle className="h-6 w-6" />}
          isRealTime={isRealData}
        />
        
        <StatCard
          title="Countries Covered"
          value={realTimeData.africanCountriesCovered || 0}
          subtitle="African nations represented"
          icon={<MapPin className="h-6 w-6" />}
          isRealTime={isRealData}
        />
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Verified Innovations"
          value={realTimeData.verifiedInnovations || 0}
          subtitle={`${realTimeData.verificationRate || 0}% verification rate`}
          icon={<CheckCircle className="h-6 w-6" />}
          isRealTime={isRealData}
        />
        
        <StatCard
          title="Unique Keywords"
          value={realTimeData.uniqueKeywords || 0}
          subtitle="AI/tech terms identified"
          icon={<Zap className="h-6 w-6" />}
          isRealTime={isRealData}
        />
        
        <StatCard
          title="African Relevance"
          value={`${Math.round((qualityMetrics.avgAfricanRelevance || 0) * 100)}%`}
          subtitle="Average relevance score"
          icon={<TrendingUp className="h-6 w-6" />}
          isRealTime={isRealData}
        />
        
        <StatCard
          title="AI Relevance"
          value={`${Math.round((qualityMetrics.avgAIRelevance || 0) * 100)}%`}
          subtitle="AI focus accuracy"
          icon={<Activity className="h-6 w-6" />}
          isRealTime={isRealData}
        />
      </div>

      {/* Pipeline Status Indicator */}
      <div className="mt-8 text-center">
        <div
          className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium"
          style={{
            backgroundColor: qualityMetrics.pipelineStatus === 'active' 
              ? "var(--color-success-background)" 
              : qualityMetrics.pipelineStatus === 'idle'
              ? "var(--color-info-background)"
              : "var(--color-muted)",
            color: qualityMetrics.pipelineStatus === 'active' 
              ? "var(--color-success)" 
              : qualityMetrics.pipelineStatus === 'idle'
              ? "var(--color-info)"
              : "var(--color-muted-foreground)",
          }}
        >
          <div 
            className={`w-2 h-2 rounded-full mr-2 ${
              qualityMetrics.pipelineStatus === 'active' 
                ? 'bg-green-500 animate-pulse' 
                : qualityMetrics.pipelineStatus === 'idle'
                ? 'bg-blue-500'
                : 'bg-gray-400'
            }`} 
          />
          ETL Pipeline: {qualityMetrics.pipelineStatus === 'active' ? 'Active' : 
                         qualityMetrics.pipelineStatus === 'idle' ? 'Standby' : 'Unknown'}
          {qualityMetrics.dataFreshness && ` • ${qualityMetrics.dataFreshness} data`}
        </div>
      </div>
    </div>
  );
};

export default RealDataDashboard;