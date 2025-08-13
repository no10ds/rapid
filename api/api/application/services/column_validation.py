import pandera
from api.common.custom_exceptions import ColumnValidationError

def validate_column(column: pandera.Column):
    has_name(column)
    has_data_type(column)
    has_nullable(column)
    has_unique(column)
    has_valid_format(column)
    has_valid_partition_index(column)



def has_name(column: pandera.Column):
    if not column.name:
        raise ColumnValidationError("Column name cannot be empty")
    

def has_data_type(column: pandera.Column):    
    if column.dtype is None:
        raise ColumnValidationError(f"Column '{column.name}' must have a defined data type")
    

def has_nullable(column: pandera.Column):    
    if column.nullable is None:
        raise ColumnValidationError(f"Column '{column.name}' must specify whether it allows null values")
    

def has_unique(column: pandera.Column):
    if column.unique is None:
        raise ColumnValidationError(f"Column '{column.name}' must specify whether it allows unique values")
    

def has_valid_format(column: pandera.Column):    
    if not column.metadata:
        raise ColumnValidationError(f"Column '{column.name}' must have metadata")
    
    if "format" not in column.metadata:
        raise ColumnValidationError(f"Column '{column.name}' must have a 'format' field in metadata")
    
    format_value = column.metadata["format"]
    if format_value is not None and not isinstance(format_value, str):
        raise ColumnValidationError(f"Column '{column.name}' has an invalid format value")
        

def has_valid_partition_index(column: pandera.Column):
    if not column.metadata:
        raise ColumnValidationError(f"Column '{column.name}' must have metadata")
    
    if "partition_index" not in column.metadata:
        raise ColumnValidationError(f"Column '{column.name}' must have a 'partition_index' field in metadata")
    
    partition_index = column.metadata["partition_index"]
    if partition_index is not None and (not isinstance(partition_index, int) or partition_index <= 0):
        raise ColumnValidationError(f"Column '{column.name}' has an invalid partition index")