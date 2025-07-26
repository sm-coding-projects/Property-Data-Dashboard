from flask import Flask, request, jsonify, render_template
import pandas as pd
import io
import numpy as np
import logging
import uuid
from datetime import datetime

# Import our custom modules
from config import config
from error_handler import error_handler, ValidationError, ProcessingError
from file_processor import file_processor
from session_manager import create_session_manager
from rate_limiter import rate_limiter, rate_limit

# Initialize Flask app with configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

# Setup logging
config.setup_logging()
logger = logging.getLogger(__name__)

# Initialize session manager
session_manager = create_session_manager(
    redis_config=config.get_redis_config(),
    session_timeout=config.SESSION_TIMEOUT
)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test session manager
        test_session = session_manager.session_exists('test')
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "components": {
                "session_manager": "ok",
                "file_processor": "ok"
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
@rate_limit(rate_limiter)
def upload_file():
    """Handles file upload and initial data processing."""
    try:
        # Validate request
        if 'file' not in request.files:
            return error_handler.handle_upload_error(
                ValidationError("No file part in request"), 
                {'endpoint': 'upload', 'ip': request.remote_addr}
            )
        
        file = request.files['file']
        if file.filename == '':
            return error_handler.handle_upload_error(
                ValidationError("No file selected"), 
                {'endpoint': 'upload', 'ip': request.remote_addr}
            )
        
        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            return error_handler.handle_upload_error(
                ValidationError("Only CSV files are allowed"), 
                {'endpoint': 'upload', 'filename': file.filename}
            )
        
        # Process file using robust file processor
        result = file_processor.process_file(file.stream, file.filename)
        
        if not result.success:
            return error_handler.handle_upload_error(
                ProcessingError(result.error_message),
                {'endpoint': 'upload', 'filename': file.filename}
            )
        
        df = result.data
        
        # Create session and store data
        session_id = session_manager.create_session(df, result.metadata)
        
        # Prepare initial data for the dashboard filters
        suburbs = df['Property locality'].unique().tolist()
        min_price = float(df['Purchase price'].min())
        max_price = float(df['Purchase price'].max())
        min_date = df['Contract date'].min().strftime('%Y-%m-%d')
        max_date = df['Contract date'].max().strftime('%Y-%m-%d')
        
        logger.info(f"File processed successfully: {file.filename}, Session: {session_id}")
        
        response_data = {
            "message": "File processed successfully",
            "session_id": session_id,
            "filters": {
                "suburbs": sorted(suburbs),
                "priceRange": [min_price, max_price],
                "dateRange": [min_date, max_date]
            }
        }
        
        # Add warnings if any
        if result.warnings:
            response_data["warnings"] = result.warnings
        
        return jsonify(response_data)
        
    except Exception as e:
        return error_handler.handle_upload_error(
            e, 
            {'endpoint': 'upload', 'ip': request.remote_addr}
        )


@app.route('/api/data', methods=['POST'])
def get_filtered_data():
    """Applies filters and returns aggregated data for the dashboard."""
    try:
        filters = request.json or {}
        
        # Get session ID from request
        session_id = filters.get('session_id')
        if not session_id:
            return error_handler.handle_validation_error(
                ValidationError("Session ID is required"),
                {'endpoint': 'data', 'ip': request.remote_addr}
            )
        
        # Retrieve data from session
        df = session_manager.get_data(session_id)
        if df is None:
            return error_handler.handle_validation_error(
                ValidationError("Session not found or expired. Please upload a file again."),
                {'endpoint': 'data', 'session_id': session_id}
            )
    
    # Apply filters
    filtered_df = df.copy()
    
    # Validate and sanitize filter inputs
    try:
        # Suburb filter
        if filters.get('suburbs') and len(filters['suburbs']) > 0:
            # Validate suburbs exist in data
            valid_suburbs = [s for s in filters['suburbs'] if s in df['Property locality'].values]
            if valid_suburbs:
                filtered_df = filtered_df[filtered_df['Property locality'].isin(valid_suburbs)]
            
        # Price range filter
        if filters.get('priceRange') and len(filters['priceRange']) == 2:
            min_p, max_p = filters['priceRange']
            # Validate price range
            if min_p <= max_p and min_p >= 0:
                filtered_df = filtered_df[filtered_df['Purchase price'].between(min_p, max_p)]
            
        # Date range filter - Fixed to handle single dates
        if filters.get('dateRange'):
            start_d, end_d = filters['dateRange']
            if start_d:
                try:
                    start_d_dt = pd.to_datetime(start_d)
                    filtered_df = filtered_df[filtered_df['Contract date'] >= start_d_dt]
                except (ValueError, TypeError):
                    logger.warning(f"Invalid start date: {start_d}")
            if end_d:
                try:
                    end_d_dt = pd.to_datetime(end_d)
                    filtered_df = filtered_df[filtered_df['Contract date'] <= end_d_dt]
                except (ValueError, TypeError):
                    logger.warning(f"Invalid end date: {end_d}")
            
        # Repeat sales filter
        if filters.get('repeatSales'):
            sale_counts = filtered_df['Property ID'].value_counts()
            repeat_ids = sale_counts[sale_counts > 1].index
            filtered_df = filtered_df[filtered_df['Property ID'].isin(repeat_ids)]
            
    except Exception as e:
        logger.error(f"Error applying filters: {str(e)}")
        # Return original data if filtering fails
        filtered_df = df.copy()

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
        
    except Exception as e:
        return error_handler.handle_processing_error(
            e,
            {'endpoint': 'data', 'session_id': filters.get('session_id'), 'ip': request.remote_addr}
        )

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0')
