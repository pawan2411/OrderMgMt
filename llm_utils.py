import os
from openai import OpenAI
import json

# Initialize the client (can be set via parameter or TOGETHER_API_KEY env var)
_client = None
_api_key = None

# Available models
AVAILABLE_MODELS = {
    "Qwen 2.5 72B (Recommended)": "Qwen/Qwen2.5-72B-Instruct-Turbo",
    "Qwen 2.5 7B (Faster)": "Qwen/Qwen2.5-7B-Instruct-Turbo",
}
_model_name = "Qwen/Qwen2.5-72B-Instruct-Turbo"  # Default

def set_api_key(key):
    """Set the API key programmatically (e.g., from Streamlit input)."""
    global _api_key, _client
    _api_key = key
    _client = None  # Reset client so it gets recreated with new key

def set_model(model_name):
    """Set the model to use for LLM calls."""
    global _model_name
    _model_name = model_name

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

def call_qwen(messages, temperature=0.0):
    """
    Calls the Qwen model via Together API.
    """
    global _model_name
    client = get_client()
    if not client:
        return "Error: API key not set."

    try:
        response = client.chat.completions.create(
            model=_model_name,
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
    Extracts ALL process information from user response.
    Captures multiple attributes if user provides rich answers.
    """
    from attribute_schema import QUESTION_FLOW
    
    # Build list of ALL attributes we might find (focus on unanswered ones)
    attr_list = []
    for q in QUESTION_FLOW:
        if q["type"] == "M" and q.get("question"):
            key = q["key"]
            examples = q.get("examples", [])
            attr_list.append({
                "key": key,
                "question": q["question"],
                "examples": examples[:2]
            })
    
    # Build the extraction prompt to find ALL mentioned attributes
    attr_descriptions = "\n".join([
        f"- {a['key']}: {a['question'][:50]}... (e.g., {', '.join(a['examples'][:2]) if a['examples'] else 'any value'})"
        for a in attr_list[:20]
    ])
    
    system_prompt = (
        "You are extracting ORDER PROCESS information from a client interview.\n"
        "The user may mention MULTIPLE things in one response. Extract ALL that apply.\n\n"
        f"ATTRIBUTES TO LOOK FOR:\n{attr_descriptions}\n\n"
        "RULES:\n"
        "1. Extract EVERY attribute the user mentions, not just one\n"
        "2. Even brief mentions count (e.g., 'PDF' → manual_intake_method: 'PDF')\n"
        "3. If they mention 'EDI, portal, and email/PDF' - that answers MULTIPLE questions\n"
        "4. Return valid JSON with ALL found attributes\n"
        "5. If nothing found, return {}\n\n"
        "EXAMPLE: If user says 'We get orders via EDI from retailers and signed PDFs from email'\n"
        "Return: {\"order_origin_channels\": \"EDI from retailers, email with signed PDFs\", "
        "\"manual_intake_method\": \"Email with signed PDF attachments\"}"
    )
    
    # Build context with conversation history
    user_message = user_input
    if conversation_history:
        user_message = f"CONVERSATION CONTEXT:\n{conversation_history}\n\nUSER'S LATEST ANSWER: {user_input}"
    else:
        user_message = f"USER'S ANSWER: {user_input}"
    
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
