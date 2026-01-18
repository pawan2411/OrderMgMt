import os
from openai import OpenAI
import json

# Initialize the client (can be set via parameter or TOGETHER_API_KEY env var)
_client = None
_api_key = None

def set_api_key(key):
    """Set the API key programmatically (e.g., from Streamlit input)."""
    global _api_key, _client
    _api_key = key
    _client = None  # Reset client so it gets recreated with new key

def get_client():
    global _client, _api_key
    if _client is None:
        api_key = _api_key or os.environ.get("TOGETHER_API_KEY")
        if not api_key:
            print("Warning: TOGETHER_API_KEY not set.")
            return None
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.together.xyz/v1",
        )
    return _client

MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct-Turbo"

def call_qwen(messages, temperature=0.0):
    """
    Calls the Qwen model via Together API.
    """
    client = get_client()
    if not client:
        return "Error: API key not set."

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None


def route_query(user_input):
    """
    Decides if the query is for Order Management or Other.
    Returns: 'ORDER_MGMT' or 'OTHER'
    """
    system_prompt = (
        "Classify the user's intent.\n"
        "ORDER_MGMT = user wants to report, log, or discuss an order process\n"
        "OTHER = anything else\n\n"
        "Reply with ONLY one word: ORDER_MGMT or OTHER"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    response = call_qwen(messages)
    if response and "ORDER" in response.upper():
        return "ORDER_MGMT"
    return "OTHER"


def extract_all_mentioned_attributes(user_input, attribute_schema, conversation_history="", expected_key=None):
    """
    Extracts process information from user response.
    
    user_input: The user's latest message
    attribute_schema: Dict of all attributes with metadata
    conversation_history: Recent conversation for context
    expected_key: The specific attribute key we're currently asking about
    """
    
    # Build focused extraction based on what we're asking
    if expected_key and expected_key in attribute_schema:
        attr_info = attribute_schema[expected_key]
        examples = attr_info.get("examples", [])
        
        system_prompt = (
            f"Extract the answer to this question from the user's response.\n\n"
            f"Question topic: {expected_key}\n"
            f"Expected answer type: Process description\n"
            f"Examples: {', '.join(examples[:3]) if examples else 'Any description'}\n\n"
            "Rules:\n"
            "1. Extract the user's answer as a concise, complete description\n"
            "2. Capture the key details they mentioned\n"
            "3. Return valid JSON: {\"" + expected_key + "\": \"extracted value\"}\n"
            "4. If they didn't answer or refused, return {}\n"
        )
    else:
        # Broad extraction - look for any attribute
        attr_list = []
        for key, info in attribute_schema.items():
            if info.get("type") == "M" and info.get("question"):
                examples = info.get("examples", [])
                attr_list.append(f"- {key}: {examples[0] if examples else 'process description'}")
        
        system_prompt = (
            "Extract any process information from the user's response.\n\n"
            f"Possible attributes to look for:\n" + "\n".join(attr_list[:15]) + "\n\n"
            "Rules:\n"
            "1. Extract only what the user clearly mentions\n"
            "2. Return valid JSON with attribute keys and values\n"
            "3. If nothing found, return {}\n"
        )
    
    # Include conversation context
    user_message = user_input
    if conversation_history:
        user_message = f"Context:\n{conversation_history}\n\nLatest response: {user_input}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    response = call_qwen(messages, temperature=0.0)
    if not response:
        return {}
    
    # Parse JSON from response
    response = response.strip()
    try:
        if "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
            return json.loads(json_str)
        return {}
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: JSON parse error: {e}")
        return {}


def generate_next_question(question_info, collected_data, conversation_history=""):
    """
    Generates a natural version of the next question.
    
    question_info: Dict with id, key, question, examples
    collected_data: What we've collected so far
    conversation_history: Recent conversation for context
    """
    
    base_question = question_info.get("question", "")
    examples = question_info.get("examples", [])
    q_id = question_info.get("id", "")
    
    # For simple questions, just return them directly with minor variation
    if len(base_question.split()) < 15:
        return base_question
    
    # For longer questions, use LLM to rephrase naturally
    system_prompt = (
        "You are a consultant conducting a process discovery interview.\n"
        "Rephrase the following question to sound natural and conversational.\n"
        "Keep the same meaning but make it flow naturally in conversation.\n"
        "Return ONLY the rephrased question, nothing else.\n\n"
        f"Original question: {base_question}\n"
        f"Examples of valid answers: {', '.join(examples[:2]) if examples else 'N/A'}"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Rephrase this question naturally."}
    ]
    
    response = call_qwen(messages, temperature=0.5)
    
    if response and len(response) > 10:
        return response.strip()
    
    return base_question


def assess_conversation_style(conversation_history, recent_responses):
    """
    Analyzes user's communication style from their responses.
    Returns: "narrative", "brief", "technical", or "neutral"
    """
    if not recent_responses:
        return "neutral"
    
    # Simple heuristic based on response length
    avg_length = sum(len(r.split()) for r in recent_responses) / len(recent_responses)
    
    if avg_length > 50:
        return "narrative"
    elif avg_length < 10:
        return "brief"
    else:
        return "neutral"
