# Property Data Dashboard

A comprehensive, production-ready web application for analyzing and visualizing property sales data from CSV files. Built with Flask, pandas, and modern web technologies, this dashboard provides powerful filtering, visualization, and export capabilities.

## 🚀 Features

### Core Functionality
- **Large File Processing**: Handles CSV files up to 500MB with automatic encoding detection
- **Interactive Filtering**: Multi-dimensional filtering with real-time updates
- **Data Visualization**: KPI cards, charts, and paginated tables
- **Export Capabilities**: CSV and PDF export with filtered data
- **Session Management**: Secure, isolated user sessions with Redis support
- **Production Ready**: Comprehensive error handling, logging, and security features

### Advanced Filtering
- **Suburb Filter**: Multi-select with search functionality
- **Dynamic Purpose Filter**: Shows only purposes available in selected suburbs
- **Price Range**: Precise input boxes for minimum and maximum prices
- **Date Range**: Flexible date filtering with single or range selection
- **Repeat Sales**: Special clustering for properties sold multiple times
- **Pagination**: Variable page sizes (10, 50, 100, 200 properties per page)

### Data Processing Features
- **Automatic Encoding Detection**: Handles various CSV encodings automatically
- **Column Mapping**: Intelligent mapping of CSV columns to expected fields
- **Data Validation**: Comprehensive validation with user-friendly error messages
- **Performance Optimization**: Caching, debouncing, and efficient data processing

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python 3.9, Flask, pandas, Gunicorn
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript, Chart.js
- **Data Storage**: In-memory with optional Redis session storage
- **Containerization**: Docker with Docker Compose
- **Security**: Rate limiting, input validation, CSRF protection

### Project Structure
```
Property-Data-Dashboard/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── error_handler.py      # Centralized error handling
├── file_processor.py     # Robust CSV file processing
├── session_manager.py    # Session management with Redis support
├── rate_limiter.py       # Rate limiting implementation
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-container setup
├── .gitignore          # Git ignore rules
└── templates/
    └── index.html       # Single-page application frontend
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM allocated to Docker (recommended: 8GB)

### Installation & Setup

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd Property-Data-Dashboard
   ```

2. **Configure Docker memory** (Important for large files)
   - Open Docker Desktop
   - Go to Settings > Resources > Advanced
   - Set Memory to at least 4GB (8GB recommended)
   - Apply & Restart

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the dashboard**
   Open your browser and navigate to: http://localhost:8080

## 📊 Usage Guide

### Getting Started
1. **Upload Data**: Click the upload area and select a CSV file
2. **Wait for Processing**: Progress bar shows upload and processing status
3. **Explore Data**: Use filters in the left sidebar to analyze your data
4. **Export Results**: Use CSV or PDF export buttons for filtered data

### Filter Options

#### Suburb Filter
- Multi-select dropdown with search functionality
- "Select All" and "Clear All" options
- Real-time search as you type

#### Purpose Filter (Dynamic)
- Shows only purposes available in selected suburbs
- Automatically updates when suburb selection changes
- Prevents invalid suburb/purpose combinations

#### Price Range
- Input boxes for precise minimum and maximum values
- Empty minimum defaults to $0
- Empty maximum defaults to dataset maximum
- Supports any numeric value within data range

#### Date Range
- Flexible date inputs supporting various formats
- Can filter by start date only, end date only, or both
- Debounced input to prevent excessive filtering while typing

#### Repeat Sales
- Special filter for properties sold multiple times
- Clusters same properties together chronologically
- Useful for investment analysis and price tracking

#### Pagination
- Choose from 10, 50, 100, or 200 properties per page
- Maintains selection across filter changes
- Shows current page info and total results

### Data Export
- **CSV Export**: Complete filtered dataset in CSV format
- **PDF Export**: Formatted report with summary statistics (first 1000 rows)
- Both exports respect all active filters

## ⚙️ Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode (development only) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_FILE_SIZE` | `500` | Maximum file size in MB |
| `SESSION_TIMEOUT` | `3600` | Session timeout in seconds |
| `REDIS_URL` | `None` | Redis connection URL for session storage |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `SECRET_KEY` | `auto-generated` | Flask secret key |

### Development Setup
```bash
# Set environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Production Deployment
```bash
# Set production environment variables
export DEBUG=false
export LOG_LEVEL=INFO
export REDIS_URL=redis://localhost:6379/0
export MAX_FILE_SIZE=500
export SESSION_TIMEOUT=3600

# Use Docker Compose
docker-compose up --build -d
```

## 🔒 Security Features

- **Input Validation**: Comprehensive validation of all user inputs
- **File Upload Security**: File type, size, and content validation
- **Rate Limiting**: IP-based rate limiting to prevent abuse
- **Session Security**: Secure session management with automatic cleanup
- **Error Handling**: User-friendly error messages without exposing system details
- **CSRF Protection**: Built-in CSRF protection for all forms

## 🚀 Performance Features

- **Caching**: Intelligent caching of filter results and API responses
- **Debouncing**: Prevents excessive API calls during rapid user input
- **Memory Management**: Automatic cleanup of expired sessions
- **Optimized Processing**: Efficient pandas operations for large datasets
- **Pagination**: Reduces memory usage and improves response times

## 📈 Recent Enhancements

### Dynamic Purpose Filtering
- Purpose filter now shows only purposes available in selected suburbs
- Automatic cleanup of invalid purpose selections
- Caching system for improved performance
- Real-time updates as suburb selections change

### Enhanced Pagination
- Variable page sizes: 10, 50, 100, 200 properties per page
- Improved pagination controls with accurate result counts
- Automatic page reset when changing page size

### Price Input Enhancement
- Replaced sliders with precise input boxes
- Default behavior: 0 (min) to Max (no upper limit)
- Support for exact value entry
- Better keyboard accessibility

### Repeat Sales Clustering
- Properties sold multiple times are grouped together
- Chronological ordering within each property group
- Consistent clustering in both table view and exports

### Robust Error Handling
- Comprehensive error handling with user-friendly messages
- Automatic fallback behaviors for API failures
- Session expiration handling with clear user guidance

## 🧪 Testing

The application includes comprehensive error handling and has been tested with:
- Various CSV file formats and encodings
- Large datasets (300MB+ files)
- Different browser environments
- Edge cases and error conditions
- Security vulnerabilities and performance limits

## 📝 API Endpoints

### Core Endpoints
- `GET /` - Main dashboard interface
- `POST /api/upload` - File upload and processing
- `POST /api/data` - Filtered data retrieval
- `POST /api/export` - Data export (CSV/PDF)
- `POST /api/available-purposes` - Dynamic purpose filtering
- `GET /api/session/<session_id>` - Session validation
- `GET /health` - Health check for monitoring

### Rate Limiting
All API endpoints are protected by rate limiting:
- 100 requests per minute per IP address
- Configurable limits via environment variables
- Graceful handling of rate limit exceeded scenarios

## 🐛 Troubleshooting

### Common Issues

**File Upload Fails**
- Check file size (max 500MB by default)
- Ensure file is in CSV format
- Verify CSV has required columns (Property locality, Purchase price, etc.)

**Out of Memory Errors**
- Increase Docker memory allocation to 8GB
- Use smaller CSV files for testing
- Check available system memory

**Session Expired**
- Sessions expire after 1 hour by default
- Upload a new file to create a new session
- Configure longer session timeout if needed

**Slow Performance**
- Use pagination with smaller page sizes
- Enable Redis for session storage
- Optimize CSV file structure

### Logs and Monitoring
- Application logs are available via `docker-compose logs web`
- Health check endpoint: `http://localhost:8080/health`
- Error details are logged with context for debugging

## 🤝 Contributing

This is a production-ready application with comprehensive features. For modifications:

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Update tests for any new functionality
4. Maintain security best practices
5. Update documentation for new features

## 📄 License

This project is provided as-is for property data analysis purposes. Please ensure compliance with data privacy regulations when processing property sales data.

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready ✅