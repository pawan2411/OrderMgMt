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
    messages: list of dicts [{'role': 'user', 'content': ...}]
    """
    client = get_client()
    if not client:
        return "Error: TOGETHER_API_KEY not set. Please set the environment variable."

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
    # Simplified prompt for 8B model
    system_prompt = (
        "Classify the user's intent.\n"
        "ORDER_MGMT = user wants to report, log, or discuss an order\n"
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

def extract_attribute(user_input, attribute_name, context_text=None, options=None):
    """
    Extracts specific attribute from user input.
    attribute_name: Name of the attribute to extract (e.g. 'channel', 'portal')
    context_text: Description of what we are looking for.
    options: List of valid options (optional).
    
    Returns: The extracted value or None if not found/unclear.
    """
    
    system_prompt = f"You are a data extraction assistant. Your goal is to extract the '{attribute_name}' from the user's input."
    
    if context_text:
        system_prompt += f"\nContext: {context_text}"
        
    if options:
        system_prompt += f"\nValid Options: {', '.join(options)}"
        system_prompt += "\nIf the user input matches one of the options (even loosely), return that option key EXACTLY."
        system_prompt += "\nIf the input does not match any valid option, return 'NOT_FOUND'."
    else:
        system_prompt += "\nExtract the value as a clean string. If the user is answering the question, extract the answer."
        system_prompt += "\nIf the user is saying something unrelated or refusal, return 'NOT_FOUND'."
        
    system_prompt += "\nReturn ONLY the extracted value (or NOT_FOUND). Do not add any conversational text."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    response = call_qwen(messages)
    if not response or "NOT_FOUND" in response:
        return None
    
    # Simple cleanup
    cleaned = response.strip().strip("'").strip('"')
    
    # Double check validation if options provided (LLM might hallucinate slightly)
    if options:
        # fuzzy match or exact match check
        if cleaned in options:
            return cleaned
        # Try to find if any option is a substring of the response
        for opt in options:
            if opt.lower() == cleaned.lower():
                return opt
        return None
        
    return cleaned

def extract_multiple_attributes(user_input, attribute_names, context_text=None):
    """
    Extracts multiple attributes from a single narrative user response.
    This is used for grouped questions where one answer contains multiple data points.
    
    attribute_names: List of attribute names to extract
    context_text: The question that was asked
    
    Returns: Dict mapping attribute_name -> extracted_value
    """
    
    system_prompt = (
        "You are a data extraction assistant. The user has answered a question that covers multiple attributes.\n"
        f"Extract the following attributes from their response: {', '.join(attribute_names)}.\n\n"
    )
    
    if context_text:
        system_prompt += f"The question they were answering: {context_text}\n\n"
    
    system_prompt += (
        "Return a JSON object with the extracted values. Use the exact attribute names as keys.\n"
        "For any attribute not mentioned or unclear in the response, use null as the value.\n"
        "Example format: {\"attribute1\": \"value1\", \"attribute2\": \"value2\", \"attribute3\": null}\n\n"
        "Return ONLY the JSON object, no other text."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    response = call_qwen(messages)
    if not response:
        return {attr: None for attr in attribute_names}
    
    try:
        # Parse JSON response
        import json
        data = json.loads(response)
        
        # Ensure all attributes are present
        result = {}
        for attr in attribute_names:
            result[attr] = data.get(attr)
        
        return result
    except json.JSONDecodeError:
        print(f"Warning: Could not parse JSON from LLM: {response}")
        return {attr: None for attr in attribute_names}

def extract_all_mentioned_attributes(user_input, attribute_schema, conversation_history=""):
    """
    Universal extractor: Scans user's response for ANY mentioned attributes.
    Optimized for smaller 8B model with chunked attribute lists.
    """
    import json
    
    # For 8B model: Only include the most relevant attributes based on context
    # Group by subclass and only send relevant ones
    relevant_attrs = []
    
    # Keywords to detect which area we're discussing (expanded for better detection)
    content_lower = user_input.lower() + conversation_history.lower()
    
    # Build focused attribute list based on conversation context
    area_keywords = {
        "Order Intake": ["order", "channel", "edi", "portal", "email", "pdf", "manual", "sales", "entry", "create"],
        "Commercial Validation": ["sku", "quantity", "price", "fob", "promo", "pricing", "checklist", "required field", "shipping instruction"],
        "Credit Governance": ["credit", "limit", "approve", "block", "analyst", "d&b", "dunn", "bradstreet", "hold", "release", "threshold"],
        "Inventory & Production": ["warehouse", "stock", "mto", "mts", "production", "fulfillment", "scheduling", "queue"],
        "Warehouse Operations": ["pick", "pack", "scanner", "paper", "list", "barcode", "handheld", "crash"],
        "Transportation Management": ["ship", "carrier", "fedex", "ups", "tracking", "ltl", "label", "freight", "address", "weight"],
        "Billing Execution": ["invoice", "freight", "billing", "landed cost", "pdf", "maria", "charge", "fee"],
        "Revenue Accounting": ["revenue", "tax", "gl", "recognition", "accounting"],
        "Cash Application": ["pay", "lockbox", "ach", "wire", "check", "match", "bank", "remit", "cash", "auto-cash", "60%", "30%", "apply"],
        "Dispute & Deduction Management": ["dispute", "deduction", "short", "damaged", "write off", "nightmare", "hold", "pricing dispute"],
        "Collections & Dunning": ["ar", "aging", "collection", "dunning", "debt", "overdue"],
        "Customer Master & Onboarding": ["customer", "entity", "tax id", "terms", "master", "setup"],
        "Reverse Logistics": ["return", "rma", "restock", "credit memo"],
        "Reporting & Audit Controls": ["dso", "kpi", "metric", "cycle time", "audit", "report", "accuracy", "compile"]
    }
    
    # Find relevant subclasses
    relevant_subclasses = set()
    for subclass, keywords in area_keywords.items():
        if any(kw in content_lower for kw in keywords):
            relevant_subclasses.add(subclass)
    
    # If no specific area detected, include common intake/credit attributes
    if not relevant_subclasses:
        relevant_subclasses = {"Order Intake", "Commercial Validation", "Credit Governance"}
    
    # Build focused attribute list
    for attr_name, attr_info in attribute_schema.items():
        if attr_info.get("subclass") in relevant_subclasses:
            relevant_attrs.append({
                "name": attr_name,
                "desc": attr_info.get("description", ""),
                "ex": attr_info.get("examples", [])[:2]  # 2 examples for 72B
            })
    
    # Using 72B model - can handle more attributes (up to 25)
    relevant_attrs = relevant_attrs[:25]
    
    # Build simple attribute list with process focus
    attr_list = "\n".join([f"- {a['name']}: {a['desc']} (e.g., {a['ex'][0] if a['ex'] else 'N/A'})" for a in relevant_attrs])
    
    # Process discovery extraction prompt
    system_prompt = (
        "You are extracting PROCESS INFORMATION from an interview about Order-to-Cash.\n"
        "The user is describing HOW their company handles orders, NOT a specific order.\n\n"
        f"PROCESS ASPECTS TO LOOK FOR:\n{attr_list}\n\n"
        "RULES:\n"
        "1. Extract process descriptions, not specific order data\n"
        "2. Capture HOW the company does each thing\n"
        "3. Return valid JSON object\n"
        "4. Use exact attribute names as keys\n"
        "5. If nothing found, return {}\n\n"
        "Example: {\"source_channel\": \"Multiple - EDI from retailers, B2B portal, and manual PDF entry\", \"order_completeness_score\": \"Variable adherence to required field checklist\"}"
    )
    
    # Include conversation context so short answers can be mapped correctly
    user_message = user_input
    if conversation_history:
        user_message = f"Context (previous conversation): {conversation_history}\n\nLatest user response: {user_input}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    response = call_qwen(messages, temperature=0.0)
    if not response:
        return {}
    
    # Clean up response - 8B might add extra text
    response = response.strip()
    
    # Try to extract JSON from response
    try:
        # Look for JSON object in response
        if "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
            return json.loads(json_str)
        return {}
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: JSON parse error: {e}")
        return {}

def generate_next_question(missing_attributes, collected_data, attribute_schema, conversation_history="", user_style="neutral", focus_area=None):
    """
    Generates the next PROCESS DISCOVERY question.
    Asks HOW the company handles each aspect, not about specific order data.
    """
    import json
    
    # Get focus area attributes
    if focus_area:
        attributes_to_ask = focus_area.get("attributes", [])[:3]
        current_subclass = focus_area.get("subclass", "")
    else:
        attributes_to_ask = missing_attributes[:3]
        if attributes_to_ask:
            info = attribute_schema.get(attributes_to_ask[0], {})
            current_subclass = info.get("subclass", "")
        else:
            current_subclass = ""
    
    # Collect the process questions from the schema
    process_questions = []
    for attr_name in attributes_to_ask:
        info = attribute_schema.get(attr_name, {})
        pq = info.get("process_question", "")
        if pq:
            process_questions.append(pq)
    
    # If we have direct process questions, use LLM to combine/rephrase naturally
    if process_questions:
        system_prompt = (
            f"You are a Deloitte consultant interviewing a client about their Order-to-Cash process.\n"
            f"Current topic: {current_subclass}\n\n"
            f"You need to understand these aspects of their process:\n"
            + "\n".join([f"- {pq}" for pq in process_questions]) + "\n\n"
            "Write ONE natural, conversational question that covers these topics.\n"
            "Sound like a consultant doing process discovery, NOT collecting order data.\n"
            "Return ONLY the question, nothing else."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the next interview question."}
        ]
        
        question = call_qwen(messages, temperature=0.7)
        
        if question and len(question) > 10:
            return question.strip()
    
    # Fallback: use first process_question directly
    if attributes_to_ask:
        first_attr = attributes_to_ask[0]
        info = attribute_schema.get(first_attr, {})
        return info.get("process_question", f"Could you tell me about your {current_subclass} process?")
    
    return "Could you tell me more about that process?"

    return question.strip()




def assess_conversation_style(conversation_history, recent_responses):
    """
    Analyzes user's communication style from their responses.
    
    conversation_history: Full conversation so far
    recent_responses: List of user's recent messages
    
    Returns: "narrative", "brief", "technical", or "neutral"
    """
    
    if not recent_responses or len(recent_responses) == 0:
        return "neutral"
    
    # Simple heuristic: check average response length
    avg_length = sum(len(r.split()) for r in recent_responses) / len(recent_responses)
    
    if avg_length > 50:
        return "narrative"
    elif avg_length < 10:
        return "brief"
    else:
        return "neutral"
    
    # Could enhance with LLM analysis for more sophistication
