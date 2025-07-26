# Purpose Filter Enhancement

## Feature Description
Added a multi-select filter for the "PURPOSE" column (Primary purpose field) that allows users to select and deselect different property purposes, similar to the existing suburb filter. This provides more granular filtering capabilities for property analysis.

## User Interface

### Purpose Filter UI
Added a new filter section in the sidebar between the Contract Date filter and Repeat Sales filter:

```
Purpose
[Select purposes... ▼]
```

When clicked, shows a dropdown with:
- **Search box**: "Search purposes..." for quick filtering
- **Select All / Clear All buttons**: Bulk selection controls
- **Checkbox list**: All available property purposes with checkboxes
- **Dynamic text**: Shows "Select purposes...", single purpose name, or "X purposes selected"

### Filter Integration
The purpose filter works seamlessly with all other filters:
- Combines with suburb, price range, date range, and repeat sales filters
- Maintains state during sorting and pagination
- Included in export functionality (CSV/PDF)
- Reset with "Reset Filters" button

## Implementation Details

### Backend Changes (app.py)

#### 1. Enhanced Upload Endpoint
Added purpose options to initial filter data:

```python
# Prepare initial data for the dashboard filters
suburbs = df['Property locality'].unique().tolist()
purposes = df['Primary purpose'].unique().tolist()  # New
min_price = float(df['Purchase price'].min())
max_price = float(df['Purchase price'].max())
min_date = df['Contract date'].min().strftime('%Y-%m-%d')
max_date = df['Contract date'].max().strftime('%Y-%m-%d')

response_data = {
    "message": "File processed successfully",
    "session_id": session_id,
    "filters": {
        "suburbs": sorted(suburbs),
        "purposes": sorted([p for p in purposes if pd.notna(p)]),  # Filter out NaN
        "priceRange": [min_price, max_price],
        "dateRange": [min_date, max_date]
    }
}
```

#### 2. Enhanced Data Endpoint
Added purpose filtering logic in `/api/data`:

```python
# Purpose filter
if filters.get('purposes') is not None:
    if len(filters['purposes']) > 0:
        # Validate purposes exist in data
        valid_purposes = [p for p in filters['purposes'] if p in df['Primary purpose'].values]
        if valid_purposes:
            filtered_df = filtered_df[filtered_df['Primary purpose'].isin(valid_purposes)]
        else:
            # No valid purposes selected, return empty result
            filtered_df = filtered_df.iloc[0:0]  # Empty dataframe with same structure
    else:
        # Empty purposes array means no purposes selected, return empty result
        filtered_df = filtered_df.iloc[0:0]  # Empty dataframe with same structure
```

#### 3. Enhanced Export Endpoint
Added the same purpose filtering logic to `/api/export` for consistency.

### Frontend Changes (templates/index.html)

#### 1. Updated App State
Added `purposes` array to filter state and `allPurposes` to global state:

```javascript
let appState = {
    sessionId: null,
    filters: {
        suburbs: [],
        purposes: [],  // New
        priceRange: [0, 0],
        dateRange: [null, null],
        repeatSales: false,
        sortColumn: 'Contract date',
        sortDirection: 'desc',
        page: 1,
        rowsPerPage: 10,
    },
    initialFilterValues: {},
    allSuburbs: [],
    allPurposes: [],  // New
    totalRows: 0,
};
```

#### 2. Added Purpose Filter UI
Created HTML structure with dropdown, search, and multi-select functionality:

```html
<!-- Purpose Filter -->
<div class="mb-6">
    <label class="block text-sm font-medium text-gray-700 mb-2">Purpose</label>
    <div class="multi-select-container">
        <button id="purposeSelectBtn" class="w-full bg-white border border-gray-300 rounded-md shadow-sm pl-3 pr-10 py-2 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            <span id="purposeSelectText" class="block truncate">Select purposes...</span>
        </button>
        <div id="purposeDropdown" class="multi-select-dropdown mt-1">
            <!-- Search and controls -->
            <!-- Options list -->
        </div>
    </div>
</div>
```

#### 3. Added JavaScript Functions

**setupPurposeFilter(purposes)**: Creates the purpose dropdown with:
- Checkbox options for each purpose
- Search functionality
- Select All / Clear All buttons
- Event handlers for selection changes

**updatePurposeButtonText()**: Updates button text based on selection:
- "Select purposes..." (none selected)
- Purpose name (one selected)
- "X purposes selected" (multiple selected)

#### 4. Enhanced Dashboard Setup
Updated `setupDashboard()` to initialize purpose filter:

```javascript
function setupDashboard(initialFilters) {
    appState.initialFilterValues = JSON.parse(JSON.stringify(initialFilters));
    setupSuburbFilter(initialFilters.suburbs);
    setupPurposeFilter(initialFilters.purposes);  // New
    setupPriceFilter(initialFilters.priceRange);
    setupDateFilter(initialFilters.dateRange);
    setupDataTableHeaders();
    resetAllFilters(false);
}
```

#### 5. Enhanced Reset Functionality
Updated `resetAllFilters()` to reset purpose selections:

```javascript
function resetAllFilters(fetch = true) {
    // ...
    appState.filters.purposes = [];  // Reset purposes
    // ...
    
    // Reset purpose UI elements
    if (purposeOptions) {
        purposeOptions.querySelectorAll('input').forEach(i => i.checked = false);
        purposeOptions.querySelectorAll('.purpose-option').forEach(option => option.classList.remove('hidden'));
    }
    if (purposeSearch) {
        purposeSearch.value = '';
    }
    updatePurposeButtonText();
    // ...
}
```

## User Experience Features

### Smart Filtering
- **Empty Selection Logic**: When no purposes are selected, shows zero results (consistent with suburb filter behavior)
- **Search Functionality**: Users can quickly find specific purposes by typing
- **Bulk Operations**: Select All and Clear All buttons for efficiency
- **Visual Feedback**: Button text updates to show current selection state

### Consistent Behavior
- **State Persistence**: Purpose selections maintained during session
- **Filter Combination**: Works seamlessly with all other filters
- **Export Integration**: Purpose filters apply to CSV and PDF exports
- **Reset Integration**: Included in global filter reset functionality

### Responsive Design
- **Dropdown Positioning**: Properly positioned dropdown that doesn't break layout
- **Mobile Friendly**: Touch-friendly checkboxes and buttons
- **Keyboard Support**: Escape key closes dropdown, search input focus
- **Click Outside**: Dropdown closes when clicking outside

## Example Usage Scenarios

### 1. Residential Property Analysis
```
Purpose: [Residential ✓] [Commercial ✗] [Industrial ✗]
Result: Shows only residential properties
```

### 2. Commercial Property Focus
```
Purpose: [Commercial ✓] [Office ✓] [Retail ✓]
Result: Shows commercial, office, and retail properties
```

### 3. Investment Analysis
```
Purpose: [Investment ✓] [Development ✓]
Suburbs: [CBD ✓] [North Sydney ✓]
Result: Shows investment and development properties in selected suburbs
```

## Benefits

1. **Enhanced Filtering**: Users can now filter by property purpose for more targeted analysis
2. **Improved Workflow**: Reduces need to manually scan through different property types
3. **Better Analytics**: Enables purpose-specific market analysis and reporting
4. **Consistent UX**: Familiar interface pattern matching the suburb filter
5. **Flexible Selection**: Multi-select allows for complex filtering scenarios

## Files Modified

1. **Backend**: `Property-Data-Dashboard/app.py`
   - Added purpose data to upload response
   - Added purpose filtering logic to data endpoint
   - Added purpose filtering logic to export endpoint

2. **Frontend**: `Property-Data-Dashboard/templates/index.html`
   - Added purpose filter UI components
   - Added JavaScript state management for purposes
   - Added setupPurposeFilter() function
   - Added updatePurposeButtonText() function
   - Enhanced resetAllFilters() function
   - Added event listeners for purpose filter interactions

## Deployment

The enhancement has been deployed by restarting the Docker container:
```bash
docker-compose restart web
```

The application is now running with the purpose filter at http://localhost:8080/

## Testing

Users can now:
1. Upload a CSV file with property data
2. Use the "Purpose" filter to select/deselect different property purposes
3. Combine purpose filtering with other filters (suburbs, price, date, repeat sales)
4. Search for specific purposes using the search box
5. Use Select All/Clear All for bulk operations
6. Export filtered results that include purpose filtering
7. Reset all filters including purpose selections

The purpose filter provides the same intuitive experience as the suburb filter, making it easy for users to analyze properties by their intended use or classification.