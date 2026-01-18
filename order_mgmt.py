from llm_utils import extract_all_mentioned_attributes, generate_next_question, assess_conversation_style
from attribute_schema import REQUIRED_ATTRIBUTES, get_missing_attributes, get_missing_by_subclass, is_complete, get_current_focus_area
import os

RECORD_FILE = "order_records.txt"

class OrderManager:
    def __init__(self):
        self.attribute_schema = REQUIRED_ATTRIBUTES

    def get_initial_state(self):
        return {
            "active": True,
            "collected_data": {},
            "conversation_history": [],
            "user_responses": [],
            "user_style": "neutral",
            "question_count": 0,
            "current_focus": None  # Track which class/subclass we're focusing on
        }

    def process_input(self, user_input, state):
        """
        Adaptive conversation processing with natural O2C flow:
        1. Extract any mentioned attributes from user response
        2. Assess communication style
        3. Generate next question following O2C flow order
        4. Complete when all attributes collected
        """
        
        # Add user's response to history
        state["user_responses"].append(user_input)
        state["conversation_history"].append(f"User: {user_input}")
        
        # Build rolling 3-conversation window for context (last 6 items = 3 exchanges)
        recent_history = state["conversation_history"][-6:]
        conv_context = "\n".join(recent_history)
        
        # Universal extraction: get ANY mentioned attributes
        extracted = extract_all_mentioned_attributes(
            user_input=user_input,
            attribute_schema=self.attribute_schema,
            conversation_history=conv_context
        )
        
        # Track if we captured anything this turn
        captured_this_turn = False
        
        # Update collected data with anything that was mentioned
        for attr_name, attr_value in extracted.items():
            if attr_value is not None:
                state["collected_data"][attr_name] = attr_value
                captured_this_turn = True
                print(f"[Captured] {attr_name}: {attr_value}")
        
        # Assess user's communication style (every few responses)
        if len(state["user_responses"]) >= 2:
            state["user_style"] = assess_conversation_style(
                conversation_history=conv_context,
                recent_responses=state["user_responses"][-3:]
            )
        
        # Get missing attributes in O2C flow order
        missing = get_missing_attributes(state["collected_data"])
        
        # Check if we have all required attributes
        if len(missing) == 0:
            # All required attributes collected!
            self.save_record(state["collected_data"])
            state["active"] = False
            
            response = (
                "This has been incredibly insightful. "
                "I have captured all the key process details. "
                "Your order-to-cash process information has been recorded."
            )
            state["conversation_history"].append(f"Bot: {response}")
            return response, state
        
        # Get current focus area (stays on same subclass until done, then moves to next)
        focus_area = get_current_focus_area(state["collected_data"])
        state["current_focus"] = focus_area
        
        # Track how many times we've tried this subclass without progress
        current_subclass = focus_area.get("subclass") if focus_area else None
        if current_subclass:
            if state.get("last_subclass") != current_subclass:
                state["subclass_attempts"] = 0
                state["last_subclass"] = current_subclass
            
            if not captured_this_turn:
                state["subclass_attempts"] = state.get("subclass_attempts", 0) + 1
            else:
                state["subclass_attempts"] = 0
        
        # If nothing was captured and answer was brief, ask for clarification (limit 2)
        if not captured_this_turn and len(user_input.split()) < 15:
            if state.get("clarification_count", 0) < 2 and state.get("subclass_attempts", 0) < 3:
                state["clarification_count"] = state.get("clarification_count", 0) + 1
                
                if focus_area and focus_area.get("attributes"):
                    attr_name = focus_area["attributes"][0]
                    attr_info = self.attribute_schema.get(attr_name, {})
                    examples = attr_info.get("examples", [])
                    
                    clarification = (
                        f"Could you elaborate a bit more? For example, I'm trying to understand: "
                        f"{attr_info.get('process_question', 'how you handle this')} "
                        f"Some examples might be: {', '.join(examples[:2]) if examples else 'various approaches'}."
                    )
                else:
                    clarification = "Could you provide more details about how that works in your process?"
                
                state["conversation_history"].append(f"Bot: {clarification}")
                return clarification, state
        
        # Reset clarification counter when we capture something
        if captured_this_turn:
            state["clarification_count"] = 0
        
        # If stuck on a subclass too long (3+ attempts), skip remaining attributes in it
        if state.get("subclass_attempts", 0) >= 3 and focus_area:
            skipped_attrs = focus_area.get("attributes", [])
            for attr in skipped_attrs:
                if attr not in state["collected_data"]:
                    state["collected_data"][attr] = "[Not discussed]"
                    print(f"[Skipped] {attr}")
            
            # Recalculate focus area after skipping
            focus_area = get_current_focus_area(state["collected_data"])
            state["current_focus"] = focus_area
            state["subclass_attempts"] = 0
            missing = get_missing_attributes(state["collected_data"])
        
        # Generate next question following the natural flow
        state["question_count"] += 1
        next_question = generate_next_question(
            missing_attributes=missing,
            collected_data=state["collected_data"],
            attribute_schema=self.attribute_schema,
            conversation_history=conv_context,
            user_style=state["user_style"],
            focus_area=focus_area
        )
        
        state["conversation_history"].append(f"Bot: {next_question}")
        return next_question, state

    def start_conversation(self):
        """
        Returns the initial question to kick off the conversation.
        Starts with Order Intake (first in O2C flow).
        """
        state = self.get_initial_state()
        
        # Opening question matches the example conversation
        opening = (
            "Thank you for your time. As discussed, we're here to map and understand your "
            "end-to-end Order-to-Cash process to identify opportunities for improvement. "
            "Let's start at the very beginning. How does an order come into your organization?"
        )
        state["conversation_history"].append(f"Bot: {opening}")
        
        return opening, state

    def save_record(self, data):
        """
        Save collected data to file with structured format.
        """
        import json
        from datetime import datetime
        
        # Add metadata
        record = {
            "timestamp": datetime.now().isoformat(),
            "attributes_captured": len(data),
            "data": data
        }
        
        with open(RECORD_FILE, "a") as f:
            f.write(json.dumps(record, indent=2) + "\n" + "="*80 + "\n")
        
        print(f"\n[SAVED] Order record with {len(data)} attributes captured")
