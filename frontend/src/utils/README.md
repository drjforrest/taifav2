# Utils

This directory contains pure utility functions and constants that can be used across the application.

## Structure

### dataCompletenessUtils.ts
Utility functions for data completeness visualization and analysis.

**Constants:**
- `CompletenessColors` - Background colors for different completeness levels
- `CompletenessColorClasses` - Text + background color combinations
- `CompletenessTextColors` - Text-only colors for completeness levels
- `SeverityColors` - Colors for severity indicators
- `SeverityIcons` - Icon mappings for severity levels

**Functions:**
- `getCompletenessLevel(percentage)` - Determine completeness category
- `getCompletenessColor(percentage)` - Get background color class
- `getCompletenessColorClass(percentage)` - Get combined color classes
- `getCompletenessTextColor(percentage)` - Get text color class
- `getSeverityColor(severity)` - Get color class for severity
- `getSeverityIcon(severity)` - Get icon name for severity
- `formatCompleteness(percentage)` - Format percentage for display
- `calculateOverallCompleteness(fieldData)` - Calculate overall score
- `categorizeFieldsByCompleteness(fieldData)` - Group fields by level
- `generateRecommendations(fieldData)` - Generate actionable insights

## Usage

```typescript
import { getCompletenessColor, formatCompleteness } from '@/utils';

const colorClass = getCompletenessColor(75.5); // 'bg-yellow-500'
const formatted = formatCompleteness(75.5); // '75.5%'
```

## Benefits

- **Pure Functions**: No side effects, easy to test
- **Consistent Styling**: Centralized color and styling logic  
- **Type Safety**: Full TypeScript support
- **Reusability**: Functions can be used across multiple components
- **Maintainability**: Single source of truth for styling logic