# Services

This directory contains modular service classes that handle API communication and data processing for the TAIFA-FIALA frontend application.

## Structure

### DataCompletenessService
Centralized service for data completeness API endpoints with automatic fallback handling.

**Methods:**
- `getMissingDataMap()` - Fetches missing data analysis with fallback to mock data
- `getEnrichmentGaps()` - Fetches enrichment gaps analysis with fallback handling  
- `healthCheck()` - Checks availability of data completeness endpoints

### MockDataService
Provides consistent mock data for development and API unavailability scenarios.

**Methods:**
- `getMissingDataMap()` - Returns structured mock missing data map
- `getEnrichmentGaps()` - Returns structured mock enrichment gaps analysis

## Usage

```typescript
import { DataCompletenessService } from '@/services';

// Fetch data with automatic fallback
const missingData = await DataCompletenessService.getMissingDataMap();
const enrichmentGaps = await DataCompletenessService.getEnrichmentGaps();
```

## Benefits

- **Centralized API Logic**: All data completeness API calls in one place
- **Automatic Fallbacks**: Seamless transition to mock data when API unavailable
- **Better Error Handling**: Consistent error handling across components
- **Type Safety**: Full TypeScript support with proper return types
- **Testability**: Easy to mock services for unit testing