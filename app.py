from flask import Flask, request, jsonify, render_template
import pandas as pd
import io
import numpy as np

app = Flask(__name__)

# This will act as our simple, in-memory database for the uploaded data.
# In a production app, you might use Redis or a database for this.
data_store = {}
# We'll use a simple session ID. In a real multi-user app, you'd have a proper session mechanism.
SESSION_ID = "user_session"

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handles file upload and initial data processing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        try:
            # Use io.StringIO to read the file stream efficiently without saving to disk
            csv_data = io.StringIO(file.stream.read().decode("UTF-8"))
            df = pd.read_csv(csv_data)
            
            # --- Data Cleaning and Preparation ---
            df.columns = [col.strip() for col in df.columns] # Clean header whitespace
            df['Purchase price'] = pd.to_numeric(df['Purchase price'], errors='coerce')
            df['Contract date'] = pd.to_datetime(df['Contract date'], errors='coerce')
            
            # Drop rows with critical missing data
            df.dropna(subset=['Purchase price', 'Contract date', 'Property ID', 'Property locality'], inplace=True)
            
            # Store the cleaned DataFrame in our data_store
            data_store[SESSION_ID] = df
            
            # Prepare initial data for the dashboard filters
            suburbs = df['Property locality'].unique().tolist()
            min_price = float(df['Purchase price'].min())
            max_price = float(df['Purchase price'].max())
            min_date = df['Contract date'].min().strftime('%Y-%m-%d')
            max_date = df['Contract date'].max().strftime('%Y-%m-%d')
            
            return jsonify({
                "message": "File processed successfully",
                "filters": {
                    "suburbs": sorted(suburbs),
                    "priceRange": [min_price, max_price],
                    "dateRange": [min_date, max_date]
                }
            })

        except Exception as e:
            return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
    return jsonify({"error": "An unknown error occurred"}), 500


@app.route('/api/data', methods=['POST'])
def get_filtered_data():
    """Applies filters and returns aggregated data for the dashboard."""
    filters = request.json
    
    if SESSION_ID not in data_store:
        return jsonify({"error": "No data found. Please upload a file first."}), 400
        
    df = data_store[SESSION_ID]
    
    # Apply filters
    filtered_df = df.copy()
    
    # Suburb filter
    if filters.get('suburbs') and len(filters['suburbs']) > 0:
        filtered_df = filtered_df[filtered_df['Property locality'].isin(filters['suburbs'])]
        
    # Price range filter
    if filters.get('priceRange'):
        min_p, max_p = filters['priceRange']
        filtered_df = filtered_df[filtered_df['Purchase price'].between(min_p, max_p)]
        
    # Date range filter
    if filters.get('dateRange'):
        start_d, end_d = filters['dateRange']
        if start_d and end_d:
            # FIX: Convert string dates from JS to datetime objects for robust comparison
            start_d_dt = pd.to_datetime(start_d)
            end_d_dt = pd.to_datetime(end_d)
            filtered_df = filtered_df[filtered_df['Contract date'].between(start_d_dt, end_d_dt)]
        
    # Repeat sales filter
    if filters.get('repeatSales'):
        sale_counts = filtered_df['Property ID'].value_counts()
        repeat_ids = sale_counts[sale_counts > 1].index
        filtered_df = filtered_df[filtered_df['Property ID'].isin(repeat_ids)]

    # --- Prepare data for JSON response ---
    
    # Metrics
    prices = filtered_df['Purchase price']
    total_properties = len(filtered_df)
    
    total_sales = float(prices.sum())
    avg_price = float(prices.mean()) if total_properties > 0 else 0.0
    median_price = float(prices.median()) if total_properties > 0 else 0.0
    
    # Sales by Suburb Chart
    sales_by_suburb = filtered_df['Property locality'].value_counts().nlargest(15).sort_values()
    
    # Price Trend Chart
    price_trend = filtered_df.set_index('Contract date').resample('M')['Purchase price'].mean().reset_index()
    price_trend['Contract date'] = price_trend['Contract date'].dt.strftime('%Y-%m')

    # Paginated Table Data
    sort_column = filters.get('sortColumn', 'Contract date')
    sort_direction = filters.get('sortDirection', 'desc')
    page = filters.get('page', 1)
    rows_per_page = 10
    
    if sort_column not in filtered_df.columns:
        sort_column = 'Contract date'

    sorted_df = filtered_df.sort_values(by=sort_column, ascending=(sort_direction == 'asc'))
    
    start_index = (page - 1) * rows_per_page
    end_index = start_index + rows_per_page
    paginated_data = sorted_df.iloc[start_index:end_index]
    
    table_cols = ['Property house number', 'Property street name', 'Property locality', 'Purchase price', 'Contract date', 'Primary purpose']
    table_data = paginated_data[table_cols].to_dict(orient='records')

    for row in table_data:
        if pd.isna(row['Contract date']):
            row['Contract date'] = None
        else:
            row['Contract date'] = row['Contract date'].strftime('%Y-%m-%d')


    return jsonify({
        "metrics": {
            "totalProperties": int(total_properties),
            "totalSalesValue": total_sales,
            "avgPrice": avg_price,
            "medianPrice": median_price,
        },
        "charts": {
            "salesBySuburb": {
                "labels": sales_by_suburb.index.tolist(),
                "data": [int(x) for x in sales_by_suburb.values],
            },
            "priceTrend": {
                "labels": price_trend['Contract date'].tolist(),
                "data": price_trend['Purchase price'].tolist(),
            }
        },
        "table": {
            "data": table_data,
            "totalRows": int(len(filtered_df))
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
