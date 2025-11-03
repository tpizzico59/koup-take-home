import json
from openai import OpenAI
import config
import tools


class CareCoordinatorLLM:
    """OpenAI client with ReAct tool execution loop."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        self.system_prompt = self._load_system_prompt()
        self.tool_schemas = self._get_tool_schemas()
    
    def _load_system_prompt(self):
        """Load system prompt from markdown file."""
        with open('system_prompt.md', 'r') as f:
            return f.read()
    
    def _get_tool_schemas(self):
        """Define tool schemas for OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_patient",
                    "description": "Search for a patient by name and date of birth. Returns full patient context including id, name, dob, pcp, ehrId, referred_providers, and appointments.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Patient full name"},
                            "dob": {"type": "string", "description": "Date of birth in MM/DD/YYYY format"}
                        },
                        "required": ["name", "dob"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_providers",
                    "description": "List providers with optional filters.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "specialty": {"type": "string", "description": "Filter by specialty"},
                            "city": {"type": "string", "description": "Filter by city"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_insurance",
                    "description": "Check if an insurance plan is accepted.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "insurance_name": {"type": "string", "description": "Insurance plan name"}
                        },
                        "required": ["insurance_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_self_pay_rate",
                    "description": "Get self-pay cost for a specialty.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "specialty": {"type": "string", "description": "Medical specialty"}
                        },
                        "required": ["specialty"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_appointment_history",
                    "description": "Check if patient has seen provider in last 5 years to determine NEW vs ESTABLISHED appointment type.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer", "description": "Patient ID"},
                            "provider_id": {"type": "integer", "description": "Provider ID"}
                        },
                        "required": ["patient_id", "provider_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_available_slots",
                    "description": "List available appointment slots within date range.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "provider_id": {"type": "integer", "description": "Provider ID"},
                            "department_name": {"type": "string", "description": "Exact department name"},
                            "start_date": {"type": "string", "description": "Start date YYYY-MM-DD"},
                            "end_date": {"type": "string", "description": "End date YYYY-MM-DD"},
                            "duration_minutes": {"type": "integer", "description": "Appointment duration (30 for NEW, 15 for ESTABLISHED)"}
                        },
                        "required": ["provider_id", "department_name", "start_date", "end_date", "duration_minutes"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_appointment",
                    "description": "Create a new appointment. Only call after explicit nurse approval.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "integer", "description": "Patient ID"},
                            "provider_id": {"type": "integer", "description": "Provider ID"},
                            "department_name": {"type": "string", "description": "Exact department name"},
                            "datetime_str": {"type": "string", "description": "ISO-8601 datetime"},
                            "appointment_type": {"type": "string", "enum": ["NEW", "ESTABLISHED"]}
                        },
                        "required": ["patient_id", "provider_id", "department_name", "datetime_str", "appointment_type"]
                    }
                }
            }
        ]
    
    def chat(self, messages, max_iterations=10):
        """
        Execute ReAct loop: chat with LLM and execute tools until completion.
        
        Args:
            messages: List of conversation messages
            max_iterations: Max tool execution loops
            
        Returns:
            Final assistant message content
        """
        # Add system prompt if not present
        if not messages or messages[0].get('role') != 'system':
            messages = [{"role": "system", "content": self.system_prompt}] + messages
        
        conversation = messages.copy()
        
        for _ in range(max_iterations):
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=conversation,
                tools=self.tool_schemas,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Build assistant message
            assistant_msg = {"role": "assistant", "content": message.content}
            
            # Add tool calls if present
            if message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            conversation.append(assistant_msg)
            
            # If no tool calls, we're done
            if not message.tool_calls:
                return message.content
            
            # Execute each tool call
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                # Execute tool
                try:
                    if tool_name in tools.TOOLS:
                        result = tools.TOOLS[tool_name](**arguments)
                    else:
                        result = {"error": f"Unknown tool: {tool_name}"}
                except Exception as e:
                    result = {"error": str(e)}
                
                # Add tool response to conversation
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        
        # Max iterations reached
        return "I apologize, but I'm having trouble completing this request. Could you try rephrasing?"


# Global LLM instance
llm = CareCoordinatorLLM()