# Repeat Sales Clustering Enhancement

## Feature Description
Enhanced the "Show properties sold > once" feature to cluster/group properties that were sold multiple times so they appear together in the results. This makes it easier to see the sales history for each property.

## Example
When the repeat sales filter is enabled, properties like "14 Abc Drive" that was sold on 21/01/2022 and 21/01/2023 will now appear consecutively in the results, grouped together by address.

## Implementation Details

### Backend Changes (app.py)

#### 1. Enhanced Data Endpoint (`/api/data`)
Added special sorting logic when `repeatSales` filter is active:

```python
# Special sorting for repeat sales to cluster properties together
if filters.get('repeatSales') and len(filtered_df) > 0:
    # Create a composite address for grouping
    filtered_df['_composite_address'] = (
        filtered_df['Property house number'].astype(str) + ' ' + 
        filtered_df['Property street name'].astype(str) + ', ' + 
        filtered_df['Property locality'].astype(str)
    ).str.replace('nan ', '').str.replace(' nan', '').str.replace('nan', '')
    
    # Sort by composite address first, then by contract date within each property
    sorted_df = filtered_df.sort_values(
        by=['_composite_address', 'Contract date'], 
        ascending=[True, (sort_direction == 'asc')]
    )
    
    # Remove the temporary column before returning data
    sorted_df = sorted_df.drop('_composite_address', axis=1)
else:
    sorted_df = filtered_df.sort_values(by=sort_column, ascending=(sort_direction == 'asc'))
```

#### 2. Enhanced Export Endpoint (`/api/export`)
Applied the same clustering logic to exports to maintain consistency:

```python
# Apply clustering for repeat sales in export as well
if filters.get('repeatSales') and len(filtered_df) > 0:
    # Create a composite address for grouping
    filtered_df['_composite_address'] = (
        filtered_df['Property house number'].astype(str) + ' ' + 
        filtered_df['Property street name'].astype(str) + ', ' + 
        filtered_df['Property locality'].astype(str)
    ).str.replace('nan ', '').str.replace(' nan', '').str.replace('nan', '')
    
    # Sort by composite address first, then by contract date
    filtered_df = filtered_df.sort_values(
        by=['_composite_address', 'Contract date'], 
        ascending=[True, True]
    )
    
    # Remove the temporary column
    filtered_df = filtered_df.drop('_composite_address', axis=1)
```

### How It Works

1. **Composite Address Creation**: Creates a temporary column combining house number, street name, and locality to uniquely identify each property
2. **Multi-level Sorting**: 
   - Primary sort: By composite address (groups same properties together)
   - Secondary sort: By contract date within each property (chronological order of sales)
3. **Clean Up**: Removes the temporary composite address column before returning data
4. **Fallback**: When repeat sales filter is not active, uses normal sorting by the selected column

### Benefits

1. **Better Visualization**: Properties sold multiple times are now grouped together, making it easy to see the sales history
2. **Chronological Order**: Within each property group, sales are sorted by date (respecting user's sort direction preference)
3. **Consistent Experience**: Same clustering applies to both table view and exports (CSV/PDF)
4. **No Breaking Changes**: Normal sorting behavior is preserved when repeat sales filter is not active

### User Experience

- **Without Repeat Sales Filter**: Normal sorting by selected column (Price, Date, etc.)
- **With Repeat Sales Filter**: Properties are clustered by address, with sales within each property sorted chronologically

### Example Output
When repeat sales filter is enabled, the results might look like:

```
14 Abc Drive, Suburb A    $500,000    2022-01-21
14 Abc Drive, Suburb A    $650,000    2023-01-21
25 Main St, Suburb B      $400,000    2021-05-15
25 Main St, Suburb B      $480,000    2022-08-10
25 Main St, Suburb B      $520,000    2024-02-03
```

This makes it much easier to track property value changes over time and identify investment patterns.

## Files Modified
- `Property-Data-Dashboard/app.py` - Added clustering logic to both `/api/data` and `/api/export` endpoints

## Deployment
The enhancement has been deployed by restarting the Docker container:
```bash
docker-compose restart web
```

The application is now running with the clustering feature at http://localhost:8080/