# Phase 2 Longitudinal Intelligence API Reference

## Base URL

- **Development**: `http://localhost:8030`
- **Production**: `https://api.taifa-fiala.net`

## Authentication

All endpoints use the same authentication mechanism as the main TAIFA-FIALA API.

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Burst**: 10 requests per second

## Endpoints

### Health Check

#### `GET /api/longitudinal-intelligence/health`

Check the health status of Phase 2 services.

**Response**:

```json
{
  "status": "healthy",
  "services": {
    "historical_trends": "operational",
    "weak_signals": "operational",
    "domain_evolution": "operational"
  },
  "timestamp": "2025-08-08T22:57:00Z"
}
```

### Historical Trend Analysis

#### `GET /api/longitudinal-intelligence/innovation-lifecycle`

Analyze innovation lifecycle stages and distributions.

**Query Parameters**:

- `include_stages` (boolean): Include detailed stage breakdown
- `time_range` (string): Filter by time range (e.g., "6m", "1y", "2y")

**Response**:

```json
{
  "total_innovations": 142,
  "average_time_to_market_days": 365,
  "stage_distribution": [
    {
      "stage": "Research",
      "count": 45,
      "average_duration_days": 180,
      "success_rate": 0.85
    }
  ],
  "success_patterns": [...],
  "bottlenecks": [...]
}
```

#### `GET /api/longitudinal-intelligence/domain-evolution`

Track domain maturity evolution over time.

**Response**:

```json
{
  "domains": [
    {
      "domain_name": "Healthcare AI",
      "maturity_stage": "growing",
      "publication_count": 234,
      "growth_rate": 34.5,
      "key_technologies": ["Deep Learning", "Computer Vision"],
      "trend_direction": "upward"
    }
  ],
  "emerging_count": 3,
  "declining_count": 1
}
```

#### `GET /api/longitudinal-intelligence/success-patterns`

Identify patterns associated with successful innovations.

**Query Parameters**:

- `domain` (string): Filter by specific domain
- `min_confidence` (float): Minimum confidence score (0.0-1.0)

**Response**:

```json
{
  "patterns": [
    {
      "pattern_type": "collaboration",
      "description": "Multi-institutional partnerships",
      "success_rate": 0.78,
      "supporting_evidence": [...],
      "confidence_score": 0.92
    }
  ]
}
```

### Weak Signal Detection

#### `GET /api/longitudinal-intelligence/emergence-indicators`

Detect early signals for emerging technologies.

**Query Parameters**:

- `threshold` (float): Confidence threshold (default: 0.6)
- `time_window` (string): Analysis window (default: "3m")

**Response**:

```json
{
  "indicators": [
    {
      "technology": "Federated Learning in Healthcare",
      "confidence": 0.87,
      "evidence": ["Patent filings surge", "Research collaboration increase"],
      "geographic_concentration": "South Africa",
      "timeline_months": 6
    }
  ]
}
```

#### `GET /api/longitudinal-intelligence/geographic-shifts`

Detect innovation hub migration patterns.

**Response**:

```json
{
  "shifts": [
    {
      "from_region": "North Africa",
      "to_region": "East Africa",
      "innovation_type": "Mobile AI",
      "shift_magnitude": 0.65,
      "timeframe": "2024 Q2-Q3",
      "evidence": [...]
    }
  ]
}
```

#### `GET /api/longitudinal-intelligence/technology-convergence`

Identify cross-domain technology combinations.

**Response**:

```json
{
  "convergences": [
    {
      "technologies": ["Blockchain", "IoT", "AI"],
      "convergence_strength": 0.78,
      "domain": "Supply Chain",
      "potential_applications": ["Food Traceability", "Carbon Credits"]
    }
  ]
}
```

#### `GET /api/longitudinal-intelligence/funding-anomalies`

Detect unusual funding patterns.

**Query Parameters**:

- `anomaly_types` (string): Comma-separated list: "spike,gap,shift"
- `significance_threshold` (float): Minimum significance level

**Response**:

```json
{
  "anomalies": [
    {
      "anomaly_type": "spike",
      "region": "Nigeria",
      "innovation_type": "FinTech",
      "magnitude": 2.3,
      "timeframe": "Q3 2024",
      "significance": 0.89
    }
  ]
}
```

### Comprehensive Analysis

#### `GET /api/longitudinal-intelligence/longitudinal-summary`

Get integrated longitudinal intelligence report.

**Query Parameters**:

- `include_lifecycle` (boolean): Include lifecycle analysis
- `include_evolution` (boolean): Include domain evolution
- `include_signals` (boolean): Include weak signals
- `include_funding` (boolean): Include funding anomalies

**Response**:

```json
{
  "summary": {
    "analysis_date": "2025-08-08T22:57:00Z",
    "total_innovations_tracked": 142,
    "active_domains": 8,
    "emerging_technologies": 12
  },
  "lifecycle_summary": {...},
  "domain_evolution": {...},
  "emergence_indicators": {...},
  "geographic_shifts": {...},
  "technology_convergence": {...},
  "funding_anomalies": {...}
}
```

#### `GET /api/longitudinal-intelligence/trend-alerts`

Get active trend alerts and warnings.

**Query Parameters**:

- `alert_type` (string): "emergence", "geographic", "convergence", "funding", "all"
- `threshold` (float): Alert sensitivity threshold
- `priority` (string): "high", "medium", "low", "all"

**Response**:

```json
{
  "alerts": [
    {
      "alert_id": "uuid",
      "alert_type": "emergence",
      "priority": "high",
      "title": "Quantum Computing Breakthrough Signal",
      "description": "Strong emergence indicators detected",
      "confidence": 0.91,
      "created_at": "2025-08-08T22:57:00Z",
      "evidence": [...],
      "recommended_actions": [...]
    }
  ],
  "summary": {
    "total_alerts": 15,
    "high_priority": 2,
    "medium_priority": 5,
    "low_priority": 8
  }
}
```

## Trends API Endpoints

### `GET /api/trends/lifecycles`

General lifecycle analytics overview.

### `GET /api/trends/lifecycles/{innovation_id}`

Individual innovation lifecycle tracking.

### `GET /api/trends/time-to-market`

Time-to-market analysis across innovations.

### `GET /api/trends/domains`

Domain evolution trends overview.

### `GET /api/trends/domains/emerging`

Emerging domain identification.

### `GET /api/trends/patterns/success`

Success pattern retrieval.

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid threshold value",
    "details": "Threshold must be between 0.0 and 1.0",
    "timestamp": "2025-08-08T22:57:00Z"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Invalid request parameters
- `NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side processing error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

## Frontend Integration

### TypeScript Types

```typescript
interface LongitudinalData {
  lifecycle_analysis: {
    stages: LifecycleStage[];
    total_tracked: number;
    average_time_to_market: number;
  };
  domain_evolution: {
    domains: DomainEvolutionData[];
    emerging_count: number;
    declining_count: number;
  };
  weak_signals: {
    emergence_indicators: EmergenceIndicator[];
    geographic_shifts: GeographicShift[];
    technology_convergence: TechnologyConvergence[];
    funding_anomalies: FundingAnomaly[];
  };
  trend_alerts: {
    high_priority: number;
    medium_priority: number;
    low_priority: number;
    total_active: number;
  };
}
```

### Usage Example

```typescript
import { apiClient, API_ENDPOINTS } from "@/lib/api-client";

// Fetch comprehensive analysis
const analysis = await apiClient.get<LongitudinalData>(
  `${API_ENDPOINTS.longitudinalIntelligence.longitudinalSummary}?include_lifecycle=true&include_evolution=true&include_signals=true&include_funding=true`
);

// Get high-priority alerts
const alerts = await apiClient.get(
  `${API_ENDPOINTS.longitudinalIntelligence.trendAlerts}?alert_type=all&priority=high&threshold=0.8`
);
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
source ../venv/bin/activate
python3 test_phase2_implementation.py
```

Expected output: **26/26 tests passed (100% pass rate)**
