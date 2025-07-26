"""
Robust file processing engine for CSV files.
Handles encoding detection, validation, and data cleaning.
"""
import io
import logging
import chardet
import pandas as pd
from typing import IO, Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from error_handler import ProcessingError, ValidationError


@dataclass
class ProcessingResult:
    """Result of file processing operation."""
    success: bool
    data: Optional[pd.DataFrame] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ValidationResult:
    """Result of data validation operation."""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []


class FileProcessor:
    """Robust CSV file processor with encoding detection and validation."""
    
    # Required columns and their possible variations
    COLUMN_MAPPINGS = {
        'Property ID': ['property_id', 'propertyid', 'id', 'property id'],
        'Property locality': ['locality', 'suburb', 'location', 'property locality', 'property_locality'],
        'Purchase price': ['price', 'purchase_price', 'sale_price', 'purchase price', 'purchase_price'],
        'Contract date': ['date', 'contract_date', 'sale_date', 'contract date', 'contract_date'],
        'Property house number': ['house_number', 'number', 'house number', 'property house number'],
        'Property street name': ['street', 'street_name', 'street name', 'property street name'],
        'Primary purpose': ['purpose', 'primary_purpose', 'primary purpose', 'property_type']
    }
    
    REQUIRED_COLUMNS = ['Property ID', 'Property locality', 'Purchase price', 'Contract date']
    
    def __init__(self, max_file_size: int = 500 * 1024 * 1024):
        self.max_file_size = max_file_size
        self.logger = logging.getLogger(__name__)
    
    def process_file(self, file_stream: IO, filename: str = None) -> ProcessingResult:
        """Process uploaded CSV file with comprehensive error handling."""
        try:
            # Validate file size
            file_content = file_stream.read()
            if len(file_content) > self.max_file_size:
                raise ProcessingError(f"File too large: {len(file_content)} bytes (max: {self.max_file_size})")
            
            # Reset stream position
            file_stream.seek(0)
            
            # Detect encoding
            encoding = self.detect_encoding(file_content)
            self.logger.info(f"Detected encoding: {encoding}")
            
            # Read CSV with detected encoding
            try:
                csv_data = io.StringIO(file_content.decode(encoding))
                df = pd.read_csv(csv_data)
            except UnicodeDecodeError:
                # Fallback to common encodings
                for fallback_encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        csv_data = io.StringIO(file_content.decode(fallback_encoding))
                        df = pd.read_csv(csv_data)
                        encoding = fallback_encoding
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ProcessingError("Unable to decode file with any supported encoding")
            
            # Validate and clean data
            validation_result = self.validate_columns(df)
            if not validation_result.is_valid:
                raise ValidationError(f"Column validation failed: {'; '.join(validation_result.errors)}")
            
            # Map columns to standard names
            df = self._map_columns(df)
            
            # Clean and process data
            df = self.clean_data(df)
            
            # Create metadata
            metadata = {
                'original_filename': filename,
                'encoding': encoding,
                'original_rows': len(df),
                'original_columns': len(df.columns),
                'file_size': len(file_content),
                'processing_warnings': validation_result.warnings
            }
            
            return ProcessingResult(
                success=True,
                data=df,
                warnings=validation_result.warnings,
                metadata=metadata
            )
            
        except (ProcessingError, ValidationError) as e:
            self.logger.error(f"File processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            self.logger.error(f"Unexpected error during file processing: {str(e)}")
            return ProcessingResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding using chardet."""
        # Use a sample for detection to improve performance
        sample_size = min(10000, len(file_content))
        sample = file_content[:sample_size]
        
        result = chardet.detect(sample)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)
        
        self.logger.debug(f"Encoding detection: {encoding} (confidence: {confidence})")
        
        # If confidence is low, try common encodings
        if confidence < 0.7:
            for test_encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    sample.decode(test_encoding)
                    return test_encoding
                except UnicodeDecodeError:
                    continue
        
        return encoding or 'utf-8'
    
    def validate_columns(self, df: pd.DataFrame) -> ValidationResult:
        """Validate CSV columns and suggest mappings."""
        errors = []
        warnings = []
        suggestions = []
        
        if df.empty:
            errors.append("File contains no data")
            return ValidationResult(False, errors, warnings, suggestions)
        
        # Clean column names
        df.columns = [col.strip() for col in df.columns]
        original_columns = df.columns.tolist()
        
        # Check for required columns
        missing_columns = []
        column_mapping = {}
        
        for required_col in self.REQUIRED_COLUMNS:
            found = False
            
            # Direct match
            if required_col in df.columns:
                column_mapping[required_col] = required_col
                found = True
            else:
                # Fuzzy match
                for col in df.columns:
                    if col.lower() in [mapping.lower() for mapping in self.COLUMN_MAPPINGS.get(required_col, [])]:
                        column_mapping[required_col] = col
                        suggestions.append(f"Mapped '{col}' to '{required_col}'")
                        found = True
                        break
            
            if not found:
                missing_columns.append(required_col)
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            suggestions.append(f"Available columns: {', '.join(original_columns)}")
        
        # Check for empty columns
        empty_columns = [col for col in df.columns if df[col].isna().all()]
        if empty_columns:
            warnings.append(f"Empty columns found: {', '.join(empty_columns)}")
        
        # Check data types for key columns
        if 'Purchase price' in column_mapping:
            price_col = column_mapping['Purchase price']
            if not pd.api.types.is_numeric_dtype(df[price_col]):
                # Try to convert
                try:
                    pd.to_numeric(df[price_col], errors='coerce')
                    warnings.append(f"Price column '{price_col}' converted to numeric")
                except:
                    errors.append(f"Price column '{price_col}' contains non-numeric data")
        
        if 'Contract date' in column_mapping:
            date_col = column_mapping['Contract date']
            try:
                pd.to_datetime(df[date_col], errors='coerce')
                warnings.append(f"Date column '{date_col}' will be converted to datetime")
            except:
                errors.append(f"Date column '{date_col}' contains invalid date formats")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, suggestions)
    
    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map columns to standard names."""
        column_mapping = {}
        
        for standard_name, variations in self.COLUMN_MAPPINGS.items():
            for col in df.columns:
                if col == standard_name:
                    column_mapping[col] = standard_name
                    break
                elif col.lower() in [v.lower() for v in variations]:
                    column_mapping[col] = standard_name
                    break
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for analysis."""
        original_rows = len(df)
        
        # Clean column names (remove extra whitespace)
        df.columns = [col.strip() for col in df.columns]
        
        # Convert data types
        if 'Purchase price' in df.columns:
            df['Purchase price'] = pd.to_numeric(df['Purchase price'], errors='coerce')
        
        if 'Contract date' in df.columns:
            df['Contract date'] = pd.to_datetime(df['Contract date'], errors='coerce')
        
        # Remove rows with critical missing data
        critical_columns = [col for col in self.REQUIRED_COLUMNS if col in df.columns]
        df = df.dropna(subset=critical_columns)
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Clean text columns
        text_columns = ['Property locality', 'Property street name', 'Primary purpose']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', pd.NA)
        
        # Log cleaning results
        cleaned_rows = len(df)
        if cleaned_rows < original_rows:
            self.logger.info(f"Data cleaning removed {original_rows - cleaned_rows} rows")
        
        return df


# Global file processor instance
file_processor = FileProcessor()