"""
Module for handling Excel import errors with standardized error messages
and consistent error reporting across the application.
"""

class ExcelImportError(Exception):
    """Base exception for Excel import errors."""
    pass


class ExcelHeaderError(ExcelImportError):
    """Exception raised when there are problems with Excel headers."""
    
    def __init__(self, missing_headers=None, invalid_headers=None):
        self.missing_headers = missing_headers or []
        self.invalid_headers = invalid_headers or []
        message = self._build_message()
        super().__init__(message)
    
    def _build_message(self):
        messages = []
        
        if self.missing_headers:
            headers_str = ", ".join(self.missing_headers)
            messages.append(f"Missing required headers: {headers_str}")
        
        if self.invalid_headers:
            headers_str = ", ".join(self.invalid_headers)
            messages.append(f"Invalid headers: {headers_str}")
        
        return ". ".join(messages)


class ExcelRowError(ExcelImportError):
    """Exception raised for errors in a specific row."""
    
    def __init__(self, row_number, errors):
        self.row_number = row_number
        self.errors = errors if isinstance(errors, list) else [errors]
        message = f"Error in row {row_number}: {'; '.join(self.errors)}"
        super().__init__(message)


class ExcelImportResult:
    """Class to track results of an Excel import operation."""
    
    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.errors = []
    
    @property
    def total_count(self):
        """Total number of rows processed."""
        return self.created_count + self.updated_count + self.skipped_count + self.error_count
    
    @property
    def success_count(self):
        """Number of rows successfully processed."""
        return self.created_count + self.updated_count
    
    def add_error(self, row_number, message):
        """Add an error message for a specific row."""
        self.errors.append(f"Row {row_number}: {message}")
        self.error_count += 1
    
    def add_errors_from_exception(self, exception):
        """Add errors from an ExcelImportError exception."""
        if isinstance(exception, ExcelHeaderError):
            for header in exception.missing_headers:
                self.add_error(1, f"Missing required header: {header}")
            for header in exception.invalid_headers:
                self.add_error(1, f"Invalid header: {header}")
        elif isinstance(exception, ExcelRowError):
            for error in exception.errors:
                self.add_error(exception.row_number, error)
        else:
            self.add_error("Unknown", str(exception))
    
    def __str__(self):
        """String representation of the import results."""
        return (
            f"Import results: {self.total_count} total rows processed, "
            f"{self.created_count} created, "
            f"{self.updated_count} updated, "
            f"{self.skipped_count} skipped, "
            f"{self.error_count} errors."
        )


class ExcelValidator:
    """Base class for Excel data validators."""
    
    def validate_headers(self, headers, required_headers):
        """Validate that all required headers are present."""
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            raise ExcelHeaderError(missing_headers=missing_headers)
        return True
    
    def validate_row(self, row_data, row_number, validators):
        """
        Validate a row of data using a dictionary of validator functions.
        
        Args:
            row_data: Dictionary of column name to value
            row_number: Row number for error reporting
            validators: Dictionary of field name to validator function
                       Each validator should raise ValueError with a message if invalid
        
        Returns:
            True if valid
            
        Raises:
            ExcelRowError if any validation fails
        """
        errors = []
        
        for field, validator in validators.items():
            value = row_data.get(field)
            try:
                if value is not None:
                    validator(value)
            except ValueError as e:
                errors.append(f"{field}: {str(e)}")
        
        if errors:
            raise ExcelRowError(row_number, errors)
        
        return True
