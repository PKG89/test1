"""File parsing with encoding detection and validation."""

import pandas as pd
import chardet
import logging
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
from src.models.bot_data import ParsedData, ColumnMapping

logger = logging.getLogger(__name__)


class FileParsingError(Exception):
    """Exception raised for file parsing errors."""
    pass


class FileParser:
    """Handles file parsing with encoding detection and validation."""
    
    # Supported delimiters
    DELIMITERS = [' ', '\t', ',', ';', '|']
    
    # Maximum file size in bytes (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # Supported extensions
    SUPPORTED_EXTENSIONS = ['.txt', '.xyz']
    
    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected encoding name
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
                
                # Default to utf-8 if confidence is too low
                if confidence < 0.7:
                    logger.warning(f"Low confidence ({confidence:.2f}), defaulting to utf-8")
                    return 'utf-8'
                
                return encoding or 'utf-8'
        except Exception as e:
            logger.error(f"Error detecting encoding: {e}")
            return 'utf-8'
    
    @staticmethod
    def detect_delimiter(file_path: Path, encoding: str = 'utf-8', sample_lines: int = 10) -> str:
        """
        Detect delimiter by analyzing first few lines.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            sample_lines: Number of lines to sample
            
        Returns:
            Detected delimiter
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= sample_lines:
                        break
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        lines.append(line)
            
            if not lines:
                return ' '
            
            # Count occurrences of each delimiter
            delimiter_counts = {}
            for delimiter in FileParser.DELIMITERS:
                counts = [line.count(delimiter) for line in lines]
                # Check consistency: all lines should have similar counts
                if counts and max(counts) > 0:
                    avg_count = sum(counts) / len(counts)
                    consistency = 1 - (max(counts) - min(counts)) / (max(counts) + 1)
                    delimiter_counts[delimiter] = (avg_count, consistency)
            
            # Choose delimiter with highest average count and consistency
            if delimiter_counts:
                best_delimiter = max(
                    delimiter_counts.items(),
                    key=lambda x: x[1][0] * x[1][1]  # avg_count * consistency
                )[0]
                logger.info(f"Detected delimiter: {repr(best_delimiter)}")
                return best_delimiter
            
            return ' '
        except Exception as e:
            logger.error(f"Error detecting delimiter: {e}")
            return ' '
    
    @staticmethod
    def validate_file(file_path: Path) -> Tuple[bool, str]:
        """
        Validate file extension and size.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        if file_path.suffix.lower() not in FileParser.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file extension. Supported: {', '.join(FileParser.SUPPORTED_EXTENSIONS)}"
        
        # Check size
        file_size = file_path.stat().st_size
        if file_size > FileParser.MAX_FILE_SIZE:
            max_mb = FileParser.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, ""
    
    @staticmethod
    def parse_file(
        file_path: Path,
        encoding: str,
        delimiter: str,
        column_mapping: ColumnMapping,
        skip_comments: bool = True
    ) -> ParsedData:
        """
        Parse file into structured data.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            delimiter: Column delimiter
            column_mapping: Column mapping configuration
            skip_comments: Whether to skip comment lines
            
        Returns:
            ParsedData object with parsed points and statistics
        """
        try:
            # Read file with pandas
            df = pd.read_csv(
                file_path,
                sep=delimiter,
                encoding=encoding,
                comment='#' if skip_comments else None,
                header=None,
                dtype=str,  # Read as string first
                skipinitialspace=True,
                on_bad_lines='skip'
            )
            
            total_rows = len(df)
            
            if total_rows == 0:
                raise FileParsingError("No valid data rows found")
            
            # Validate required columns exist
            max_col = max(column_mapping.x_col, column_mapping.y_col, column_mapping.z_col)
            if max_col >= df.shape[1]:
                raise FileParsingError(
                    f"File has only {df.shape[1]} columns, but mapping requires {max_col + 1}"
                )
            
            points = []
            invalid_rows = 0
            anomalies = []
            warnings = []
            
            for idx, row in df.iterrows():
                try:
                    # Extract coordinates
                    x_str = str(row[column_mapping.x_col]).strip()
                    y_str = str(row[column_mapping.y_col]).strip()
                    z_str = str(row[column_mapping.z_col]).strip()
                    
                    # Convert to float
                    x = float(x_str)
                    y = float(y_str)
                    z = float(z_str)
                    
                    # Round Z to 2 decimals
                    z = round(z, 2)
                    
                    # Check for anomalies
                    if abs(x) > 1e8 or abs(y) > 1e8 or abs(z) > 1e6:
                        anomalies.append(
                            f"Row {idx + 1}: Unusually large coordinate values (X={x}, Y={y}, Z={z})"
                        )
                    
                    # Extract optional fields
                    point = {
                        'x': x,
                        'y': y,
                        'z': z
                    }
                    
                    # Name
                    if column_mapping.name_col is not None and column_mapping.name_col < df.shape[1]:
                        name = str(row[column_mapping.name_col]).strip()
                        if name and name.lower() != 'nan':
                            point['name'] = name
                    
                    # Code
                    if column_mapping.code_col is not None and column_mapping.code_col < df.shape[1]:
                        code = str(row[column_mapping.code_col]).strip()
                        if code and code.lower() != 'nan':
                            point['code'] = code
                    
                    # Comment
                    if column_mapping.comment_col is not None and column_mapping.comment_col < df.shape[1]:
                        # Combine remaining columns as comment
                        comment_parts = []
                        for col_idx in range(column_mapping.comment_col, df.shape[1]):
                            val = str(row[col_idx]).strip()
                            if val and val.lower() != 'nan':
                                comment_parts.append(val)
                        if comment_parts:
                            point['comment'] = ' '.join(comment_parts)
                    
                    points.append(point)
                    
                except (ValueError, TypeError) as e:
                    invalid_rows += 1
                    warnings.append(f"Row {idx + 1}: Could not parse coordinates - {str(e)}")
            
            valid_rows = len(points)
            
            # Log summary
            logger.info(
                f"Parsed {valid_rows} valid points from {total_rows} total rows "
                f"({invalid_rows} invalid)"
            )
            
            if valid_rows == 0:
                raise FileParsingError("No valid points could be parsed from file")
            
            return ParsedData(
                points=points,
                total_rows=total_rows,
                valid_rows=valid_rows,
                invalid_rows=invalid_rows,
                anomalies=anomalies[:10],  # Limit to first 10 anomalies
                warnings=warnings[:10]  # Limit to first 10 warnings
            )
            
        except FileParsingError:
            raise
        except Exception as e:
            logger.error(f"Error parsing file: {e}", exc_info=True)
            raise FileParsingError(f"Failed to parse file: {str(e)}")
