# Dynamic Purpose Filter Enhancement

## Feature Description
Enhanced the Purpose filter to dynamically show only the purposes available in the currently selected suburbs. This reduces clutter and provides a more intuitive filtering experience by showing only relevant options.

## Problem Solved
Previously, the Purpose filter showed all purposes from the entire dataset, which could be overwhelming and include irrelevant options. For example, if a user selected only residential suburbs, they would still see industrial and commercial purposes that don't exist in those areas.

## Solution Overview
Implemented a dynamic filtering system where:
- **No suburbs selected**: Purpose filter shows all available purposes
- **Suburbs selected**: Purpose filter shows only purposes that exist in those suburbs
- **Real-time updates**: Purpose options update immediately when suburb selections change
- **Automatic cleanup**: Previously selected purposes that are no longer available are automatically deselected

## Implementation Details

### Backend Changes (app.py)

#### New API Endpoint: `/api/available-purposes`
```python
@app.route('/api/available-purposes', methods=['POST'])
def get_available_purposes():
    """Returns purposes available for selected suburbs."""
    # Get session data
    df = session_manager.get_data(session_id)
    selected_suburbs = filters.get('suburbs', [])
    
    if not selected_suburbs:
        # No suburbs selected, return all purposes
        purposes = df['Primary purpose'].dropna().unique().tolist()
    else:
        # Filter by selected suburbs first, then get available purposes
        suburb_filtered_df = df[df['Property locality'].isin(valid_suburbs)]
        purposes = suburb_filtered_df['Primary purpose'].dropna().unique().tolist()
    
    return jsonify({
        "purposes": sorted(purposes),
        "count": len(purposes)
    })
```

### Frontend Changes (templates/index.html)

#### 1. Enhanced State Management
```javascript
let appState = {
    // ... existing state
    allPurposes: [],           // All purposes in dataset
    availablePurposes: [],     // Purposes available for current suburbs
    // ...
};
```

#### 2. Dynamic Purpose Update Functions
```javascript
// Update available purposes based on current suburb selection
async function updateAvailablePurposesWithCache() {
    const cacheKey = getPurposeCacheKey(appState.filters.suburbs);
    
    // Check cache first for performance
    if (purposeCache.has(cacheKey)) {
        appState.availablePurposes = purposeCache.get(cacheKey);
        updatePurposeFilterUI();
        return;
    }
    
    // Fetch from API and cache result
    const response = await fetch('/api/available-purposes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: appState.sessionId,
            suburbs: appState.filters.suburbs
        })
    });
    
    const result = await response.json();
    purposeCache.set(cacheKey, result.purposes);
    appState.availablePurposes = result.purposes;
    updatePurposeFilterUI();
}
```

#### 3. Dynamic UI Updates
```javascript
// Update the purpose filter UI with available options
function updatePurposeFilterUI() {
    const purposeOptions = document.getElementById('purposeOptions');
    purposeOptions.innerHTML = '';
    
    if (appState.availablePurposes.length === 0) {
        purposeOptions.innerHTML = '<div class="p-4 text-sm text-gray-500 text-center">No purposes available for selected suburbs</div>';
        return;
    }
    
    // Rebuild purpose options with only available purposes
    appState.availablePurposes.forEach(purpose => {
        // Create checkbox option with event handlers
        // Preserve existing selections where possible
    });
}
```

#### 4. Automatic Selection Cleanup
```javascript
// Remove selected purposes that are no longer available
function cleanupInvalidPurposeSelections() {
    const availableSet = new Set(appState.availablePurposes);
    const originalLength = appState.filters.purposes.length;
    
    appState.filters.purposes = appState.filters.purposes.filter(purpose => 
        availableSet.has(purpose)
    );
    
    // If selections were removed, update UI and fetch new data
    if (appState.filters.purposes.length !== originalLength) {
        updatePurposeButtonText();
        fetchFilteredData();
    }
}
```

#### 5. Event Integration
Enhanced suburb selection handlers to trigger purpose updates:
```javascript
// Individual suburb checkbox
optionDiv.querySelector('input').addEventListener('change', (e) => {
    // ... existing suburb logic ...
    debouncedPurposeUpdate(); // NEW: Update available purposes
    fetchFilteredData();
});

// Select All suburbs
selectAllBtn.addEventListener('click', (e) => {
    // ... existing logic ...
    debouncedPurposeUpdate(); // NEW: Update available purposes
    fetchFilteredData();
});

// Clear All suburbs
clearAllBtn.addEventListener('click', (e) => {
    // ... existing logic ...
    debouncedPurposeUpdate(); // NEW: Update available purposes
    fetchFilteredData();
});
```

## Performance Optimizations

### 1. Caching System
```javascript
const purposeCache = new Map();

function getPurposeCacheKey(suburbs) {
    return suburbs.sort().join('|');
}
```
- Caches purpose results by suburb combination
- Avoids redundant API calls for the same suburb selections
- Uses sorted suburb names as cache key for consistency

### 2. Debounced Updates
```javascript
const debouncedPurposeUpdate = debounce(updateAvailablePurposesWithCache, 300);
```
- 300ms debounce prevents excessive API calls during rapid suburb changes
- Balances responsiveness with performance

### 3. Optimized DOM Updates
- Only rebuilds purpose options when necessary
- Preserves existing selections where possible
- Uses DocumentFragment for batch DOM operations

## User Experience Improvements

### Before (Static Purpose Filter)
1. User selects residential suburbs
2. Purpose filter still shows all purposes including "Industrial", "Warehouse", etc.
3. User might select irrelevant purposes that don't exist in selected suburbs
4. Results show zero properties, causing confusion

### After (Dynamic Purpose Filter)
1. User selects residential suburbs
2. Purpose filter automatically updates to show only "Residence", "Townhouse", etc.
3. User can only select relevant purposes that actually exist
4. Results are always meaningful and non-empty (when purposes exist)

## Edge Cases Handled

### 1. No Suburbs Selected
- **Behavior**: Purpose filter shows all available purposes
- **Rationale**: User hasn't restricted by location, so all purposes are relevant

### 2. No Purposes Available
- **Behavior**: Shows "No purposes available for selected suburbs" message
- **Example**: User selects only industrial suburbs but dataset has no industrial properties

### 3. Invalid Purpose Selections
- **Behavior**: Automatically removes purposes that are no longer available
- **Example**: User had "Commercial" selected, then deselects all commercial suburbs

### 4. API Failures
- **Behavior**: Falls back to showing all purposes
- **User Experience**: Filter continues to work, just not dynamically filtered

### 5. Session Expiration
- **Behavior**: Redirects to upload page with clear error message
- **Handling**: Graceful degradation without breaking the interface

## Example Usage Scenarios

### Scenario 1: Residential Area Analysis
1. User selects residential suburbs: "Bondi", "Manly", "Coogee"
2. Purpose filter updates to show: "Residence", "Townhouse", "Apartment"
3. User selects "Residence" 
4. Results show only residential properties in selected suburbs

### Scenario 2: Commercial Property Research
1. User selects CBD and commercial areas
2. Purpose filter updates to show: "Commercial", "Office", "Retail", "Shop"
3. User can focus on relevant commercial purposes only

### Scenario 3: Mixed Development Analysis
1. User selects mixed-use suburbs
2. Purpose filter shows: "Residence", "Commercial", "Mixed use", "Retail"
3. User can analyze the mix of property types in those areas

## Benefits

1. **Reduced Cognitive Load**: Users see only relevant options, reducing decision fatigue
2. **Improved Accuracy**: Prevents selection of non-existent purpose/suburb combinations
3. **Better Performance**: Caching and debouncing optimize API usage
4. **Intuitive Workflow**: Filter behavior matches user mental model
5. **Automatic Cleanup**: Prevents invalid filter states that would show zero results

## Technical Benefits

1. **Maintainable Code**: Clean separation of concerns with dedicated functions
2. **Robust Error Handling**: Graceful fallbacks for all failure scenarios
3. **Performance Optimized**: Caching and debouncing prevent unnecessary work
4. **Extensible Design**: Easy to add similar dynamic filtering to other components

## Files Modified

1. **Backend**: `Property-Data-Dashboard/app.py`
   - Added `/api/available-purposes` endpoint
   - Implemented suburb-based purpose filtering logic

2. **Frontend**: `Property-Data-Dashboard/templates/index.html`
   - Enhanced state management with `availablePurposes`
   - Added dynamic purpose update functions
   - Integrated purpose updates with suburb selection events
   - Added caching and performance optimizations
   - Enhanced error handling and user feedback

## Deployment

The enhancement has been deployed by restarting the Docker container:
```bash
docker-compose restart web
```

The application is now running with dynamic purpose filtering at http://localhost:8080/

## Testing

Users can now:
1. Upload CSV data and see all purposes initially
2. Select one or more suburbs and watch the Purpose filter update automatically
3. See only purposes that actually exist in the selected suburbs
4. Experience automatic cleanup of invalid purpose selections
5. Use "Select All" and "Clear All" for suburbs and see purpose filter respond
6. Reset all filters and see purpose filter return to showing all purposes
7. Export data with confidence that suburb/purpose combinations are valid

The dynamic purpose filtering provides a much more intuitive and efficient property analysis experience!