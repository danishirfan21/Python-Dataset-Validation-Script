# Agent Data Validator

**A production-ready tool for validating multi-turn assistant conversation datasets used in LLM training pipelines.**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 Overview

In the rapidly evolving field of Large Language Models (LLMs), data quality is paramount. Agent Data Validator ensures that conversation datasets used for training conversational AI agents meet strict formatting standards, preventing costly training failures and ensuring consistent model performance.

**Use Cases:**
- **LLM Training Pipelines**: Validate datasets before expensive training runs
- **Data Engineering**: Ensure conversation data meets schema requirements
- **Quality Assurance**: Automated validation in CI/CD workflows
- **Agent Development**: Validate tool-calling conversation datasets
- **Research**: Ensure experimental datasets follow consistent formats

---

## ✨ Key Features

### 🔍 **Comprehensive Validation**
- **Sequential Turn Validation**: Ensures proper conversation flow (turn_id: 1, 2, 3...)
- **Speaker Role Enforcement**: Validates user/assistant roles and required fields
- **Tool Usage Validation**: Ensures complete tool calling triplets (tool_used, tool_input, tool_output)
- **Type Safety**: Validates JSON data types (integers, strings, objects)
- **Format Support**: Handles both JSON arrays and JSONL formats

### 📊 **Professional Reporting**
- **Multiple Output Formats**: Console (for development) and Markdown (for documentation)
- **Detailed Error Messages**: Line numbers, error types, and specific fix suggestions
- **Error Categorization**: Groups similar errors for efficient debugging
- **Summary Statistics**: Quick overview of dataset health

### ⚙️ **Enterprise-Ready Configuration**
- **YAML Configuration**: Externally configurable validation rules
- **Custom Speaker Types**: Support for system messages and custom roles
- **Flexible Field Requirements**: Configurable required/optional fields
- **Tool Validation Rules**: Customizable tool usage requirements

### 🛠️ **Developer Experience**
- **CLI Interface**: Simple command-line usage with comprehensive options
- **Python API**: Programmatic integration for automation pipelines
- **Rich Documentation**: Complete API reference and usage examples
- **Test Coverage**: Comprehensive test suite with edge case handling

---

## 🔧 Technologies Used

- **Python 3.7+**: Core language with modern typing support
- **PyYAML**: Configuration file parsing
- **Argparse**: Professional CLI interface
- **JSON/JSONL**: Multi-format dataset support
- **Pathlib**: Modern file system operations
- **Dataclasses & Enums**: Type-safe data structures
- **Pytest**: Comprehensive testing framework

---

## 📋 Example Usage

### **Input: Valid Conversation Dataset**
```json
[
  {
    "turn_id": 1,
    "speaker": "user",
    "message": "What's the weather in San Francisco?"
  },
  {
    "turn_id": 2,
    "speaker": "assistant",
    "assistant_reply": "I'll check the current weather for you.",
    "tool_used": "weather_api",
    "tool_input": {"location": "San Francisco, CA"},
    "tool_output": {"temperature": "68°F", "condition": "sunny"}
  },
  {
    "turn_id": 3,
    "speaker": "assistant",
    "assistant_reply": "It's currently 68°F and sunny in San Francisco!"
  }
]
```

### **Command Line Usage**
```bash
# Basic validation
$ python validator.py conversation.json
✅ All validations passed! Dataset is properly formatted.

# Validate with custom rules
$ python validator.py dataset.json --config custom_rules.yaml

# Generate professional markdown report
$ python validator.py dataset.json --format markdown --output validation_report.md
```

### **Output: Error Detection & Reporting**
```bash
❌ Found 3 validation error(s):
============================================================

🔴 Line 2 (Turn 2)
   Error: Expected turn_id 2, got 3
   Type: turn_id_sequence_error
   💡 Suggestion: Update turn_id to 2 to maintain sequence.

🔴 Line 4 (Turn 4)
   Error: When using tools, both tool_input and tool_output are required. Missing: tool_output
   Type: tool_validation_error
   💡 Suggestion: Add the missing fields: tool_output

🔴 Line 5 (Turn 5)
   Error: turn_id must be an integer, got str
   Type: invalid_type
   💡 Suggestion: Change turn_id to an integer value.
```

### **Python API Integration**
```python
from validator import AgentDataValidator, ValidationConfig

# Basic usage
validator = AgentDataValidator()
errors = validator.validate_file("conversation.json")

if not errors:
    print("✅ Dataset ready for training!")
else:
    print(f"❌ Found {len(errors)} issues to fix")
    report = validator.generate_report("markdown")
    
# Custom configuration for enterprise use
config = ValidationConfig(
    valid_speakers=["user", "assistant", "system"],
    required_keys_user=["turn_id", "speaker", "message", "timestamp"]
)
validator = AgentDataValidator(config)
```

---

## 📁 Project Structure

```
agent-data-validator/
├── 📄 validator.py              # Core validation engine & CLI
├── 📄 demo.py                   # Interactive demonstration
├── 📄 requirements.txt          # Dependencies
├── 📄 setup.py                  # Package configuration
├── 📄 README.md                 # Project documentation
│
├── 📁 examples/                 # Example datasets & configs
│   ├── valid_example.json      # Properly formatted conversation
│   ├── invalid_example.json    # Examples with various errors
│   └── validation_config.yaml  # Configuration template
│
├── 📁 tests/                    # Comprehensive test suite
│   ├── test_validator.py       # Core validation tests
│   └── test_data/              # Test datasets
│
└── 📁 docs/                     # Documentation
    ├── SCHEMA.md               # Dataset schema specification
    └── API.md                  # Python API reference
```

---

## 🚀 Running Locally

### **Quick Start**
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/agent-data-validator.git
cd agent-data-validator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate example files
python validator.py --create-examples

# 4. Test validation
python validator.py valid_example.json
python validator.py invalid_example.json

# 5. Run interactive demo
python demo.py
```

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Run test suite
python -m pytest tests/ -v --cov=validator

# Format code
black validator.py tests/

# Type checking
mypy validator.py
```

### **Package Installation**
```bash
# Install as editable package
pip install -e .

# Use as command-line tool
agent-data-validator conversation.json --format markdown
```

---

## 🎯 Validation Schema

### **Required Fields**
| Speaker | Required Fields | Optional Fields |
|---------|----------------|-----------------|
| `user` | `turn_id`, `speaker` | `message`, custom fields |
| `assistant` | `turn_id`, `speaker`, `assistant_reply` | `tool_used`, `tool_input`, `tool_output` |

### **Tool Usage Rules**
- If any tool field is present → all 3 required (`tool_used`, `tool_input`, `tool_output`)
- `tool_input` and `tool_output` must be valid JSON objects
- Tools are optional but must be complete when used

### **Validation Rules**
- **Turn IDs**: Sequential integers starting from 1
- **Speaker Values**: Must be "user" or "assistant" (configurable)
- **Type Safety**: Strict JSON type validation
- **Business Logic**: Speaker-specific field requirements

---

## 🔮 Future Enhancements

### **Immediate Roadmap**
- [ ] **Performance Optimization**: Streaming validation for large datasets (>1M turns)
- [ ] **Advanced Reporting**: HTML dashboard with interactive error visualization
- [ ] **Schema Evolution**: Backward compatibility validation for dataset versioning
- [ ] **Integration Hooks**: Webhooks for CI/CD pipeline integration

### **Advanced Features**
- [ ] **Semantic Validation**: Content quality checks (response relevance, tool usage appropriateness)
- [ ] **Multi-format Support**: CSV, Parquet, and database integration
- [ ] **Distributed Validation**: Parallel processing for enterprise-scale datasets
- [ ] **ML-Powered QA**: Automated detection of conversation quality issues

### **Enterprise Features**
- [ ] **Cloud Integration**: AWS S3, GCS, Azure Blob storage support
- [ ] **Monitoring & Alerts**: Integration with Datadog, Prometheus
- [ ] **Audit Logging**: Compliance-ready validation audit trails
- [ ] **API Service**: REST API for microservice architectures

---

## 🤝 Contributing

This project demonstrates production-ready code for LLM infrastructure roles. The codebase showcases:

- **Clean Architecture**: Separation of concerns with configurable validation logic
- **Enterprise Patterns**: Error handling, logging, and extensible design
- **Testing Best Practices**: Comprehensive test coverage with edge cases
- **Documentation Standards**: Clear API documentation and usage examples
- **CI/CD Ready**: Linting, formatting, and automated testing setup

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built for the future of conversational AI** 🤖✨

*Perfect for roles in LLM training infrastructure, agent tooling, and AI data engineering.*