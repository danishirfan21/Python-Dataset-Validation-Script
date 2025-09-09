# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-data-validator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for validating multi-turn assistant conversation datasets for LLM training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agent-data-validator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "agent-data-validator=validator:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

# docs/SCHEMA.md - Schema Documentation
"""
# Agent Conversation Dataset Schema

This document describes the required data format for multi-turn assistant conversations used in LLM training.

## Overview

Each conversation is represented as a JSON array of turn objects. Each turn represents either a user message or an assistant response, with optional tool usage.

## Schema Definition

### Root Structure
```json
[
  {
    // Turn object 1
  },
  {
    // Turn object 2  
  }
  // ... more turns
]
```

### Turn Object Schema

#### Base Fields (All Turns)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `turn_id` | integer | ✅ | Sequential ID starting from 1 |
| `speaker` | string | ✅ | Either "user" or "assistant" |

#### User Turn Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ⚠️ | User's message (configurable) |

#### Assistant Turn Fields  
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assistant_reply` | string | ✅ | Assistant's response text |

#### Tool Usage Fields (Optional)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_used` | string | ⚠️ | Name of the tool used |
| `tool_input` | object | ⚠️ | Input parameters for the tool |
| `tool_output` | object | ⚠️ | Output returned from the tool |

**Note**: If any tool field is present, all three (`tool_used`, `tool_input`, `tool_output`) must be present.

## Validation Rules

### Turn ID Rules
- Must be integers starting from 1
- Must increment sequentially (no gaps or duplicates)
- Each conversation must start with turn_id = 1

### Speaker Rules
- Must be exactly "user" or "assistant" (case-sensitive)
- User turns cannot have `assistant_reply` field
- Assistant turns must have `assistant_reply` field

### Tool Usage Rules
- Tool fields are mutually dependent:
  - If `tool_used` is present → `tool_input` and `tool_output` required
  - If `tool_input` is present → `tool_used` and `tool_output` required  
  - If `tool_output` is present → `tool_used` and `tool_input` required
- `tool_input` and `tool_output` must be valid JSON objects
- `tool_used` must be a non-empty string

### Type Validation
- `turn_id`: Must be integer (not string)
- `speaker`: Must be string
- `assistant_reply`: Must be string
- `tool_used`: Must be string
- `tool_input`: Must be object/dictionary
- `tool_output`: Must be object/dictionary

## Example Conversations

### Simple Conversation (No Tools)
```json
[
  {
    "turn_id": 1,
    "speaker": "user",
    "message": "Hello, how are you?"
  },
  {
    "turn_id": 2, 
    "speaker": "assistant",
    "assistant_reply": "Hello! I'm doing well, thank you for asking. How can I help you today?"
  },
  {
    "turn_id": 3,
    "speaker": "user", 
    "message": "What's the weather like?"
  },
  {
    "turn_id": 4,
    "speaker": "assistant",
    "assistant_reply": "I'd be happy to help you check the weather, but I'll need to know your location first. Could you please tell me what city or area you're interested in?"
  }
]
```

### Conversation with Tool Usage
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
    "assistant_reply": "I'll check the current weather in San Francisco for you.",
    "tool_used": "weather_api",
    "tool_input": {
      "location": "San Francisco, CA",
      "units": "fahrenheit"
    },
    "tool_output": {
      "temperature": 68,
      "condition": "partly cloudy",
      "humidity": 65,
      "wind_speed": 12
    }
  },
  {
    "turn_id": 3,
    "speaker": "assistant",
    "assistant_reply": "The current weather in San Francisco is 68°F and partly cloudy. The humidity is at 65% with winds at 12 mph. It's a nice day!"
  },
  {
    "turn_id": 4,
    "speaker": "user",
    "message": "Thanks! What about tomorrow?"
  },
  {
    "turn_id": 5,
    "speaker": "assistant",
    "assistant_reply": "Let me get tomorrow's forecast for San Francisco.",
    "tool_used": "weather_api", 
    "tool_input": {
      "location": "San Francisco, CA",
      "forecast_days": 1,
      "units": "fahrenheit"
    },
    "tool_output": {
      "forecast": [
        {
          "date": "2024-03-15",
          "high": 72,
          "low": 58,
          "condition": "sunny"
        }
      ]
    }
  },
  {
    "turn_id": 6,
    "speaker": "assistant", 
    "assistant_reply": "Tomorrow in San Francisco looks great! It will be sunny with a high of 72°F and a low of 58°F. Perfect weather for outdoor activities!"
  }
]
```

### Multi-Tool Conversation
```json
[
  {
    "turn_id": 1,
    "speaker": "user",
    "message": "I need to book a flight from NYC to LAX and then find a hotel nearby."
  },
  {
    "turn_id": 2,
    "speaker": "assistant",
    "assistant_reply": "I'll help you with both the flight and hotel. Let me start by searching for flights from NYC to LAX.",
    "tool_used": "flight_search",
    "tool_input": {
      "origin": "NYC",
      "destination": "LAX", 
      "departure_date": "2024-03-20"
    },
    "tool_output": {
      "flights": [
        {
          "flight_number": "AA123",
          "departure": "08:00",
          "arrival": "11:30",
          "price": 450
        }
      ]
    }
  },
  {
    "turn_id": 3,
    "speaker": "assistant",
    "assistant_reply": "I found a flight for you: American Airlines AA123 departing at 8:00 AM and arriving at 11:30 AM for $450. Now let me search for hotels near LAX.",
    "tool_used": "hotel_search",
    "tool_input": {
      "location": "LAX Airport",
      "check_in": "2024-03-20",
      "check_out": "2024-03-22",
      "radius_miles": 5
    },
    "tool_output": {
      "hotels": [
        {
          "name": "Airport Inn",
          "price_per_night": 120,
          "rating": 4.2,
          "distance_miles": 2.1
        }
      ]
    }
  },
  {
    "turn_id": 4,
    "speaker": "assistant",
    "assistant_reply": "Great! I also found the Airport Inn, which is 2.1 miles from LAX with a 4.2-star rating at $120 per night. Would you like me to provide more details about either option or search for alternatives?"
  }
]
```

## Common Validation Errors

### Turn ID Errors
```json
// ❌ Wrong: Missing turn_id
{
  "speaker": "user",
  "message": "Hello"
}

// ❌ Wrong: Non-sequential turn_id  
{
  "turn_id": 3,  // Should be 2 if previous was 1
  "speaker": "user",
  "message": "Hello"
}

// ❌ Wrong: String instead of integer
{
  "turn_id": "1",  // Should be 1 (integer)
  "speaker": "user", 
  "message": "Hello"
}
```

### Speaker Errors
```json
// ❌ Wrong: Invalid speaker value
{
  "turn_id": 1,
  "speaker": "bot",  // Should be "assistant"
  "assistant_reply": "Hello"
}

// ❌ Wrong: User with assistant_reply
{
  "turn_id": 1,
  "speaker": "user",
  "assistant_reply": "This shouldn't be here"
}

// ❌ Wrong: Assistant without assistant_reply
{
  "turn_id": 1,
  "speaker": "assistant"
  // Missing assistant_reply field
}
```

### Tool Usage Errors
```json
// ❌ Wrong: Incomplete tool usage
{
  "turn_id": 1,
  "speaker": "assistant",
  "assistant_reply": "Using a tool",
  "tool_used": "search",
  "tool_input": {"query": "test"}
  // Missing tool_output
}

// ❌ Wrong: Tool output without tool_used
{
  "turn_id": 1,
  "speaker": "assistant", 
  "assistant_reply": "Here's the result",
  "tool_output": {"result": "data"}
  // Missing tool_used and tool_input
}

// ❌ Wrong: Invalid tool input type
{
  "turn_id": 1,
  "speaker": "assistant",
  "assistant_reply": "Using a tool",
  "tool_used": "search",
  "tool_input": "should be object",  // Should be {}
  "tool_output": {"result": "data"}
}
```

## File Formats

### JSON Array Format (Recommended)
```json
[
  {"turn_id": 1, "speaker": "user", "message": "Hello"},
  {"turn_id": 2, "speaker": "assistant", "assistant_reply": "Hi there!"}
]
```

### JSONL Format (Also Supported)
```
{"turn_id": 1, "speaker": "user", "message": "Hello"}
{"turn_id": 2, "speaker": "assistant", "assistant_reply": "Hi there!"}
```

## Customization

The validator supports custom schemas via YAML configuration files. See `validation_config.yaml` for an example of how to:

- Add custom required fields
- Define additional optional fields  
- Allow custom speaker types (e.g., "system")
- Modify tool validation rules

## Best Practices

1. **Consistent Formatting**: Use consistent field names across all conversations
2. **Sequential Turn IDs**: Always start from 1 and increment by 1
3. **Complete Tool Usage**: If using tools, always include all three tool fields
4. **Meaningful Replies**: Ensure assistant_reply contains the actual response text
5. **Proper Types**: Use correct JSON types (integers for turn_id, objects for tool data)
6. **Validation**: Always validate your data before using it for training

## Integration with Training Pipelines

This schema is designed to be easily integrated into LLM training pipelines:

- Turn IDs enable easy conversation reconstruction
- Speaker fields enable role-specific processing
- Tool usage fields support function calling training
- Consistent structure enables batch processing
- Validation ensures data quality for training
"""