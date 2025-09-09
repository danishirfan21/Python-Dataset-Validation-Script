# API Reference

This document provides detailed API reference for the Agent Data Validator library.

## Classes

### ValidationConfig

Configuration class for customizing validation behavior.

#### Constructor

```python
ValidationConfig(
    min_turns: int = 1,
    max_turns: int = 100,
    min_message_length: int = 1,
    max_message_length: int = 5000,
    min_assistant_reply_length: int = 1,
    max_assistant_reply_length: int = 5000,
    required_fields: List[str] = ['turn_id', 'speaker'],
    optional_fields: List[str] = ['message', 'assistant_reply', 'tool_used', 'tool_input', 'tool_output', 'confidence_score', 'metadata'],
    allowed_speakers: List[str] = ['user', 'assistant'],
    allowed_tools: Optional[List[str]] = None,
    require_tool_input: bool = True,
    require_tool_output: bool = True,
    confidence_score_min: float = 0.0,
    confidence_score_max: float = 1.0,
    strict_mode: bool = False,
    check_turn_sequence: bool = True,
    allow_empty_messages: bool = False
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_turns` | int | 1 | Minimum number of turns required in a conversation |
| `max_turns` | int | 100 | Maximum number of turns allowed in a conversation |
| `min_message_length` | int | 1 | Minimum length for user messages |
| `max_message_length` | int | 5000 | Maximum length for user messages |
| `min_assistant_reply_length` | int | 1 | Minimum length for assistant replies |
| `max_assistant_reply_length` | int | 5000 | Maximum length for assistant replies |
| `required_fields` | List[str] | ['turn_id', 'speaker'] | Fields that must be present in every turn |
| `optional_fields` | List[str] | [various] | Fields that are allowed but not required |
| `allowed_speakers` | List[str] | ['user', 'assistant'] | Valid values for the speaker field |
| `allowed_tools` |Optional[List[str]] | None | Valid tool names (None = any tool allowed) |
| `require_tool_input` | bool | True | Whether tool_input is required when tool_used is present |
| `require_tool_output` | bool | True | Whether tool_output is required when tool_used is present |
| `confidence_score_min` | float | 0.0 | Minimum allowed confidence score |
| `confidence_score_max` | float | 1.0 | Maximum allowed confidence score |
| `strict_mode` | bool | False | Enable strict validation (more restrictive rules) |
| `check_turn_sequence` | bool | True | Whether to validate turn_id sequence |
| `allow_empty_messages` | bool | False | Whether to allow empty messages/replies |

#### Example

```python
from validator import ValidationConfig

# Create custom configuration
config = ValidationConfig(
    min_turns=3,
    max_turns=20,
    required_fields=['turn_id', 'speaker', 'timestamp'],
    allowed_speakers=['human', 'ai'],
    allowed_tools=['web_search', 'calculator'],
    strict_mode=True
)
```

---

### AgentDataValidator

Main validator class for validating conversation datasets.

#### Constructor

```python
AgentDataValidator(config: Optional[ValidationConfig] = None)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | Optional[ValidationConfig] | None | Validation configuration (uses default if None) |

#### Methods

##### validate_file(file_path: str) -> ValidationResult

Validate a data file.

**Parameters:**
- `file_path` (str): Path to the JSON or YAML file to validate

**Returns:**
- `ValidationResult`: Results of the validation

**Example:**
```python
validator = AgentDataValidator()
result = validator.validate_file('conversation.json')
if result.is_valid:
    print("File is valid!")
else:
    for error in result.errors:
        print(f"Error: {error.message}")
```

##### validate_data(data: Any) -> ValidationResult

Validate conversation data directly.

**Parameters:**
- `data` (Any): The conversation data to validate (should be a list of turns)

**Returns:**
- `ValidationResult`: Results of the validation

**Example:**
```python
data = [
    {"turn_id": 1, "speaker": "user", "message": "Hello"},
    {"turn_id": 2, "speaker": "assistant", "assistant_reply": "Hi there!"}
]

validator = AgentDataValidator()
result = validator.validate_data(data)
```

---

### ValidationResult

Container for validation results.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_valid` | bool | Whether the data passed validation |
| `total_turns` | int | Total number of turns in the conversation |
| `errors` | List[ValidationError] | List of validation errors found |
| `warnings` | List[str] | List of validation warnings |

#### Methods

##### add_error(error_type: ErrorType, message: str, turn_id: Optional[int] = None, field: Optional[str] = None)

Add an error to the validation results.

**Parameters:**
- `error_type` (ErrorType): Type of error
- `message` (str): Error message
- `turn_id` (Optional[int]): Turn ID where error occurred
- `field` (Optional[str]): Field name where error occurred

##### add_warning(message: str)

Add a warning to the validation results.

**Parameters:**
- `message` (str): Warning message

**Example:**
```python
result = validator.validate_file('data.json')
print(f"Valid: {result.is_valid}")
print(f"Total turns: {result.total_turns}")
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")

for error in result.errors:
    print(f"Error in turn {error.turn_id}: {error.message}")
```

---

### ValidationError

Represents a single validation error.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `error_type` | ErrorType | Type of error |
| `message` | str | Human-readable error message |
| `turn_id` | Optional[int] | Turn ID where error occurred (if applicable) |
| `field` | Optional[str] | Field name where error occurred (if applicable) |

---

### ErrorType

Enumeration of error types.

#### Values

| Value | Description |
|-------|-------------|
| `STRUCTURE_ERROR` | Invalid data structure or format |
| `REQUIRED_FIELD_MISSING` | Required field is missing |
| `INVALID_FIELD_TYPE` | Field has wrong data type |
| `INVALID_FIELD_VALUE` | Field value is not allowed |
| `SEQUENCE_ERROR` | Turn sequence is invalid |
| `CONTENT_ERROR` | Content validation failed |
| `TOOL_ERROR` | Tool usage validation failed |

## Functions

### create_example_files()

Create example valid and invalid data files for testing.

**Parameters:** None

**Returns:** None

**Side Effects:** Creates `valid_example.json` and `invalid_example.json` in current directory

**Example:**
```python
from validator import create_example_files

create_example_files()
# Creates valid_example.json and invalid_example.json
```

### main()

Main CLI function for command-line usage.

**Parameters:** Uses sys.argv for command-line arguments

**Returns:** None

**Example:**
```bash
python validator.py --create-examples
python validator.py conversation.json
python validator.py --config config.yaml data.json --verbose
```

## Command Line Interface

### Basic Usage

```bash
python validator.py [OPTIONS] [FILES...]
```

### Options

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to YAML configuration file |
| `--create-examples` | Create example files for testing |
| `--report PATH` | Generate validation report to specified file |
| `--verbose` | Enable verbose output |
| `--help` | Show help message |

### Examples

```bash
# Validate single file
python validator.py conversation.json

# Validate multiple files
python validator.py data1.json data2.yaml data3.json

# Create example files
python validator.py --create-examples

# Use custom configuration
python validator.py --config my_config.yaml data.json

# Generate report
python validator.py --report validation_report.md data.json

# Verbose output
python validator.py --verbose data.json
```

## Configuration File Format

Configuration can be provided via YAML file:

```yaml
# validation_config.yaml
min_turns: 2
max_turns: 50
min_message_length: 5
max_message_length: 2000
min_assistant_reply_length: 10
max_assistant_reply_length: 2000

required_fields:
  - turn_id
  - speaker
  - message

optional_fields:
  - assistant_reply
  - tool_used
  - tool_input
  - tool_output
  - confidence_score
  - metadata

allowed_speakers:
  - user
  - assistant

tools:
  allowed_tools:
    - web_search
    - code_search
    - calculator
  require_tool_input: true
  require_tool_output: true

confidence_score:
  min_value: 0.0
  max_value: 1.0

strict_mode: false
check_turn_sequence: true
allow_empty_messages: false
```

## Error Handling

### File Loading Errors

If a file cannot be loaded (file not found, invalid JSON/YAML, etc.), a `ValidationResult` with `STRUCTURE_ERROR` is returned.

### Data Structure Errors

If the data structure is invalid (not a list, contains non-objects, etc.), appropriate `STRUCTURE_ERROR` entries are added to the result.

### Validation Errors

All validation errors are collected and returned in the `ValidationResult.errors` list. Validation continues even after errors are found to provide comprehensive feedback.

## Extension Points

### Custom Validation Rules

To add custom validation rules, extend the `AgentDataValidator` class:

```python
class CustomValidator(AgentDataValidator):
    def _validate_turn(self, turn, position, result):
        # Call parent validation first
        super()._validate_turn(turn, position, result)
        
        # Add custom validation
        if 'custom_field' in turn:
            if not self._validate_custom_field(turn['custom_field']):
                result.add_error(
                    ErrorType.INVALID_FIELD_VALUE,
                    "Custom field validation failed",
                    turn.get('turn_id'),
                    'custom_field'
                )
    
    def _validate_custom_field(self, value):
        # Custom validation logic
        return isinstance(value, str) and len(value) > 0
```

### Custom Error Types

Extend the `ErrorType` enum for custom error categories:

```python
class CustomErrorType(ErrorType):
    CUSTOM_ERROR = "custom_error"
```

## Performance Considerations

- **Memory Usage**: Large files are loaded entirely into memory. For very large datasets, consider processing in chunks.
- **Validation Speed**: Validation is linear with respect to the number of turns. Complex regex or custom validation rules may slow down processing.
- **File I/O**: JSON parsing is generally faster than YAML. Consider using JSON for performance-critical applications.

## Thread Safety

The validator classes are thread-safe for read operations, but configuration should not be modified concurrently. Create separate validator instances for concurrent use with different configurations.
