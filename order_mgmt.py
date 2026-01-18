"""
Order Management Module - Hierarchical Flow

Manages the conversation flow for Order Management process discovery.
Uses hierarchical question flow with conditional branching.
"""

from attribute_schema import (
    REQUIRED_ATTRIBUTES, QUESTION_FLOW,
    get_next_question_info, get_missing_attributes, is_complete,
    run_inferences, get_progress, INFERENCE_FUNCTIONS
)
from llm_utils import (
    extract_all_mentioned_attributes,
    generate_next_question,
    assess_conversation_style
)


class OrderManager:
    def __init__(self):
        self.attribute_schema = REQUIRED_ATTRIBUTES
    
    def get_initial_state(self):
        return {
            "active": True,
            "collected_data": {},
            "conversation_history": [],
            "user_responses": [],
            "question_count": 0,
            "user_style": "neutral",
            "current_question_id": None,
        }

    def process_input(self, user_input, state):
        """
        Process user input with hierarchical flow:
        1. Extract any mentioned attributes
        2. Run inferences on collected data
        3. Find next applicable question
        4. Generate natural question
        """
        
        # Add user's response to history
        state["user_responses"].append(user_input)
        state["conversation_history"].append(f"User: {user_input}")
        
        # Build rolling 3-conversation window for context
        recent_history = state["conversation_history"][-6:]
        conv_context = "\n".join(recent_history)
        
        # Get current question context for better extraction
        current_q_id = state.get("current_question_id")
        current_q_key = None
        if current_q_id:
            for q in QUESTION_FLOW:
                if q["id"] == current_q_id:
                    current_q_key = q["key"]
                    break
        
        # Extract attributes from user response
        extracted = extract_all_mentioned_attributes(
            user_input=user_input,
            attribute_schema=self.attribute_schema,
            conversation_history=conv_context,
            expected_key=current_q_key
        )
        
        # Update collected data
        for attr_name, attr_value in extracted.items():
            if attr_value is not None:
                state["collected_data"][attr_name] = attr_value
                print(f"[Captured] {attr_name}: {attr_value}")
        
        # Run inferences (e.g., has_manual_intake from order_origin_channels)
        state["collected_data"] = run_inferences(state["collected_data"])
        
        # Check if complete
        if is_complete(state["collected_data"]):
            self.save_record(state["collected_data"])
            state["active"] = False
            
            response = (
                "This has been incredibly insightful. "
                "I have captured all the key process details for Order Management. "
                "Your information has been recorded."
            )
            state["conversation_history"].append(f"Bot: {response}")
            return response, state
        
        # Get next question
        next_q = get_next_question_info(state["collected_data"])
        
        if next_q:
            state["current_question_id"] = next_q["id"]
            state["question_count"] += 1
            
            # Generate natural version of the question
            question = generate_next_question(
                question_info=next_q,
                collected_data=state["collected_data"],
                conversation_history=conv_context
            )
            
            state["conversation_history"].append(f"Bot: {question}")
            return question, state
        else:
            # Shouldn't reach here, but fallback
            state["active"] = False
            return "Thank you, I believe we've covered the key points.", state

    def start_conversation(self):
        """
        Returns the initial question to kick off the conversation.
        """
        state = self.get_initial_state()
        
        # Get first question
        first_q = get_next_question_info(state["collected_data"])
        state["current_question_id"] = first_q["id"] if first_q else None
        
        opening = (
            "Thank you for your time. I'm here to understand your Order-to-Cash process. "
            f"Let's start with the basics: {first_q['question'] if first_q else 'How do orders come into your organization?'}"
        )
        state["conversation_history"].append(f"Bot: {opening}")
        
        return opening, state

    def save_record(self, data):
        """Save collected data to file."""
        import json
        from datetime import datetime
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        with open("order_records.txt", "a") as f:
            f.write(json.dumps(record, indent=2))
            f.write("\n" + "="*50 + "\n")
        
        print(f"[Saved] Record with {len(data)} attributes")
