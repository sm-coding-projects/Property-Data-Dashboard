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

@app.route('/api/session/<session_id>', methods=['GET'])
def check_session(session_id):
    """Check if a session is valid."""
    try:
        if session_manager.session_exists(session_id):
            session_info = session_manager.get_session_info(session_id)
            return jsonify({
                "valid": True,
                "session_info": session_info
            }), 200
        else:
            return jsonify({
                "valid": False,
                "message": "Session not found or expired"
            }), 404
    except Exception as e:
        logger.error(f"Session check failed: {str(e)}")
        return jsonify({
            "valid": False,
            "message": "Error checking session"
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
            # Check if session exists but data is None vs session doesn't exist
            if session_manager.session_exists(session_id):
                error_msg = "Session data is corrupted. Please upload your file again."
            else:
                error_msg = "Session not found or expired. Please upload your file again."
            
            return error_handler.handle_validation_error(
                ValidationError(error_msg),
                {'endpoint': 'data', 'session_id': session_id}
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        # Validate and sanitize filter inputs
        try:
            # Suburb filter
            if filters.get('suburbs') is not None:
                if len(filters['suburbs']) > 0:
                    # Validate suburbs exist in data
                    valid_suburbs = [s for s in filters['suburbs'] if s in df['Property locality'].values]
                    if valid_suburbs:
                        filtered_df = filtered_df[filtered_df['Property locality'].isin(valid_suburbs)]
                    else:
                        # No valid suburbs selected, return empty result
                        filtered_df = filtered_df.iloc[0:0]  # Empty dataframe with same structure
                else:
                    # Empty suburbs array means no suburbs selected, return empty result
                    filtered_df = filtered_df.iloc[0:0]  # Empty dataframe with same structure
                
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
        


        # Paginated Table Data
        sort_column = filters.get('sortColumn', 'Contract date')
        sort_direction = filters.get('sortDirection', 'desc')
        page = filters.get('page', 1)
        rows_per_page = 10
        
        if sort_column not in filtered_df.columns:
            sort_column = 'Contract date'

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

@app.route('/api/export', methods=['POST'])
def export_data():
    """Export filtered data as CSV or PDF."""
    try:
        filters = request.json or {}
        export_format = filters.get('export_format', 'csv')
        
        # Get session ID from request
        session_id = filters.get('session_id')
        if not session_id:
            return error_handler.handle_validation_error(
                ValidationError("Session ID is required"),
                {'endpoint': 'export', 'ip': request.remote_addr}
            )
        
        # Retrieve data from session
        df = session_manager.get_data(session_id)
        if df is None:
            if session_manager.session_exists(session_id):
                error_msg = "Session data is corrupted. Please upload your file again."
            else:
                error_msg = "Session not found or expired. Please upload your file again."
            
            return error_handler.handle_validation_error(
                ValidationError(error_msg),
                {'endpoint': 'export', 'session_id': session_id}
            )
        
        # Apply the same filters as in get_filtered_data
        filtered_df = df.copy()
        
        try:
            # Suburb filter
            if filters.get('suburbs') is not None:
                if len(filters['suburbs']) > 0:
                    valid_suburbs = [s for s in filters['suburbs'] if s in df['Property locality'].values]
                    if valid_suburbs:
                        filtered_df = filtered_df[filtered_df['Property locality'].isin(valid_suburbs)]
                    else:
                        # No valid suburbs selected, return empty result
                        filtered_df = filtered_df.iloc[0:0]  # Empty dataframe with same structure
                else:
                    # Empty suburbs array means no suburbs selected, return empty result
                    filtered_df = filtered_df.iloc[0:0]  # Empty dataframe with same structure
                
            # Price range filter
            if filters.get('priceRange') and len(filters['priceRange']) == 2:
                min_p, max_p = filters['priceRange']
                if min_p <= max_p and min_p >= 0:
                    filtered_df = filtered_df[filtered_df['Purchase price'].between(min_p, max_p)]
                
            # Date range filter
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
            logger.error(f"Error applying filters for export: {str(e)}")
            filtered_df = df.copy()

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

        # Prepare data for export
        export_columns = ['Property house number', 'Property street name', 'Property locality', 
                         'Purchase price', 'Contract date', 'Primary purpose', 'Property ID']
        
        # Only include columns that exist in the dataframe
        available_columns = [col for col in export_columns if col in filtered_df.columns]
        export_df = filtered_df[available_columns].copy()
        
        # Format the data for export
        if 'Contract date' in export_df.columns:
            export_df['Contract date'] = export_df['Contract date'].dt.strftime('%Y-%m-%d')
        
        if 'Purchase price' in export_df.columns:
            export_df['Purchase price'] = export_df['Purchase price'].round(2)

        if export_format.lower() == 'csv':
            # Export as CSV
            from flask import Response
            import io
            
            output = io.StringIO()
            export_df.to_csv(output, index=False)
            output.seek(0)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=property_sales_data.csv'}
            )
            
        elif export_format.lower() == 'pdf':
            # Export as PDF
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.units import inch
                import io
                
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                                      topMargin=72, bottomMargin=18)
                
                # Container for the 'Flowable' objects
                elements = []
                
                # Add title
                styles = getSampleStyleSheet()
                title = Paragraph("Property Sales Data Export", styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 12))
                
                # Add summary info
                summary_text = f"Total Properties: {len(export_df)}<br/>"
                if 'Purchase price' in export_df.columns:
                    total_value = export_df['Purchase price'].sum()
                    avg_price = export_df['Purchase price'].mean()
                    summary_text += f"Total Sales Value: ${total_value:,.2f}<br/>"
                    summary_text += f"Average Price: ${avg_price:,.2f}<br/>"
                
                summary = Paragraph(summary_text, styles['Normal'])
                elements.append(summary)
                elements.append(Spacer(1, 12))
                
                # Prepare table data (limit to first 1000 rows for PDF)
                table_df = export_df.head(1000)
                
                # Create table data
                data = [table_df.columns.tolist()]
                for _, row in table_df.iterrows():
                    row_data = []
                    for col in table_df.columns:
                        value = row[col]
                        if pd.isna(value):
                            row_data.append('')
                        elif col == 'Purchase price':
                            row_data.append(f'${value:,.0f}')
                        else:
                            row_data.append(str(value))
                    data.append(row_data)
                
                # Create table
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                
                if len(export_df) > 1000:
                    note = Paragraph(f"<br/>Note: Only first 1000 rows shown. Total rows: {len(export_df)}", 
                                   styles['Normal'])
                    elements.append(note)
                
                # Build PDF
                doc.build(elements)
                buffer.seek(0)
                
                return Response(
                    buffer.getvalue(),
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment; filename=property_sales_data.pdf'}
                )
                
            except ImportError:
                return error_handler.handle_processing_error(
                    ProcessingError("PDF export not available. Please install reportlab: pip install reportlab"),
                    {'endpoint': 'export', 'format': 'pdf'}
                )
        else:
            return error_handler.handle_validation_error(
                ValidationError("Invalid export format. Use 'csv' or 'pdf'"),
                {'endpoint': 'export', 'format': export_format}
            )
            
    except Exception as e:
        return error_handler.handle_processing_error(
            e,
            {'endpoint': 'export', 'session_id': filters.get('session_id'), 'ip': request.remote_addr}
        )

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0')
