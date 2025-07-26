# Pagination Enhancement - Variable Page Sizes

## Feature Description
Enhanced the Property Sales Data table to allow users to select different page sizes (10, 50, 100, 200 properties per page) instead of being limited to the default 10 properties per page.

## User Interface Changes

### Page Size Selector
Added a dropdown selector in the table header that allows users to choose how many properties to display per page:

```
Property Sales Data    [Show: [10 ▼] per page]    [Export CSV] [Export PDF]
```

Available options:
- 10 properties per page (default)
- 50 properties per page
- 100 properties per page  
- 200 properties per page

### Updated Pagination Info
The pagination information now dynamically updates based on the selected page size:
- "Showing 1 to 10 of 1,234 results" (for 10 per page)
- "Showing 1 to 50 of 1,234 results" (for 50 per page)
- etc.

## Implementation Details

### Backend Changes (app.py)

#### Enhanced Data Endpoint
Modified the `/api/data` endpoint to accept and validate `rowsPerPage` parameter:

```python
# Paginated Table Data
sort_column = filters.get('sortColumn', 'Contract date')
sort_direction = filters.get('sortDirection', 'desc')
page = filters.get('page', 1)
rows_per_page = filters.get('rowsPerPage', 10)

# Validate rows_per_page to prevent abuse
valid_page_sizes = [10, 50, 100, 200]
if rows_per_page not in valid_page_sizes:
    rows_per_page = 10
```

**Security**: Added validation to ensure only allowed page sizes are accepted, preventing potential abuse.

### Frontend Changes (templates/index.html)

#### 1. Updated App State
Added `rowsPerPage` to the application state:

```javascript
let appState = {
    sessionId: null,
    filters: {
        suburbs: [],
        priceRange: [0, 0],
        dateRange: [null, null],
        repeatSales: false,
        sortColumn: 'Contract date',
        sortDirection: 'desc',
        page: 1,
        rowsPerPage: 10,  // New field
    },
    // ...
};
```

#### 2. Added Page Size Selector UI
Enhanced the table header with a dropdown selector:

```html
<div class="flex items-center gap-4">
    <h3 class="text-lg font-semibold text-gray-900">Property Sales Data</h3>
    <div class="flex items-center gap-2">
        <label for="rowsPerPageSelect" class="text-sm text-gray-600">Show:</label>
        <select id="rowsPerPageSelect" class="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500">
            <option value="10">10</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="200">200</option>
        </select>
        <span class="text-sm text-gray-600">per page</span>
    </div>
</div>
```

#### 3. Added Event Listener
Added event handling for page size changes:

```javascript
rowsPerPageSelect.addEventListener('change', () => {
    appState.filters.rowsPerPage = parseInt(rowsPerPageSelect.value);
    appState.filters.page = 1; // Reset to first page when changing page size
    fetchFilteredData();
});
```

#### 4. Updated Pagination Controls
Modified the `renderPaginationControls()` function to use dynamic page sizes:

```javascript
function renderPaginationControls() {
    const rowsPerPage = appState.filters.rowsPerPage;
    const totalPages = Math.ceil(appState.totalRows / rowsPerPage);
    const currentPage = appState.filters.page;
    
    const startItem = (currentPage - 1) * rowsPerPage + 1;
    const endItem = Math.min(currentPage * rowsPerPage, appState.totalRows);
    
    // Dynamic pagination info display
    let html = `<p class="text-sm text-gray-700">Showing <span class="font-medium">${startItem}</span> to <span class="font-medium">${endItem}</span> of <span class="font-medium">${appState.totalRows}</span> results</p>`;
    // ...
}
```

#### 5. Updated Reset Function
Enhanced the `resetAllFilters()` function to reset page size:

```javascript
function resetAllFilters(fetch = true) {
    // ...
    appState.filters.page = 1;
    appState.filters.rowsPerPage = 10;
    // ...
    rowsPerPageSelect.value = '10';
    // ...
}
```

## User Experience Improvements

### Automatic Page Reset
When users change the page size, the application automatically resets to page 1 to avoid confusion (e.g., if user is on page 10 with 10 items per page, switching to 100 items per page would show different data).

### Consistent State Management
The page size selection is maintained throughout the user session and is included in all API calls, ensuring consistent behavior across filtering, sorting, and pagination operations.

### Responsive Design
The page size selector is integrated seamlessly into the existing table header design and maintains the responsive layout on different screen sizes.

## Benefits

1. **Improved Productivity**: Users can view more properties at once, reducing the need for frequent page navigation
2. **Flexible Viewing**: Different users can choose their preferred viewing density
3. **Better Performance Control**: Users can balance between page load speed (smaller pages) and convenience (larger pages)
4. **Maintained Performance**: Backend validation ensures reasonable limits to prevent performance issues

## Example Usage

1. **Default View**: Shows 10 properties per page
2. **Quick Overview**: Select 50 or 100 per page to see more properties at once
3. **Bulk Analysis**: Select 200 per page for comprehensive data review
4. **Performance Optimization**: Use smaller page sizes on slower connections

## Files Modified

1. **Backend**: `Property-Data-Dashboard/app.py`
   - Added `rowsPerPage` parameter handling
   - Added validation for allowed page sizes

2. **Frontend**: `Property-Data-Dashboard/templates/index.html`
   - Added page size selector UI
   - Updated JavaScript state management
   - Enhanced pagination controls
   - Updated reset functionality

## Deployment

The enhancement has been deployed by restarting the Docker container:
```bash
docker-compose restart web
```

The application is now running with the pagination enhancement at http://localhost:8080/

## Testing

Users can now:
1. Upload a CSV file with property data
2. Use the "Show: [dropdown] per page" selector to choose 10, 50, 100, or 200 properties per page
3. Navigate through pages with the updated pagination controls
4. See accurate "Showing X to Y of Z results" information
5. Reset filters to return to default 10 per page setting