from llm_utils import route_query, call_qwen
from order_mgmt import OrderManager

class Orchestrator:
    def __init__(self):
        self.order_manager = OrderManager()

    def handle_message(self, user_input, session_state):
        """
        Main entry point for handling user messages.
        session_state: A dictionary-like object (streamlit session state)
        """
        
        # Ensure 'mode' exists
        if "mode" not in session_state:
            session_state["mode"] = "GENERAL"

        current_mode = session_state["mode"]
        
        # 1. Active Order Management Mode
        if current_mode == "ORDER_MGMT":
            # Check if we have state
            if "order_state" not in session_state:
                # Should not happen if logic is correct, but safe fallback
                response, new_state = self.order_manager.start_conversation()
                session_state["order_state"] = new_state
                return response
            
            # Delegate to OrderManager
            response, updated_state = self.order_manager.process_input(user_input, session_state["order_state"])
            session_state["order_state"] = updated_state
            
            # Check if flow finished
            if not updated_state.get("active", False):
                session_state["mode"] = "GENERAL"
                # session_state["order_state"] = None # clean up if desired, or keep history
            
            return response

        # 2. General Mode - Check Routing
        else:
            intent = route_query(user_input)
            
            if intent == "ORDER_MGMT":
                # Switch to Order Management
                session_state["mode"] = "ORDER_MGMT"
                response, start_state = self.order_manager.start_conversation()
                session_state["order_state"] = start_state
                
                # Check if the initial message contains data (not just "log order" or similar)
                # If it does, process it for extraction before returning
                if len(user_input.split()) > 5:  # More than just a trigger phrase
                    # Process the initial message to extract any data it contains
                    response, updated_state = self.order_manager.process_input(user_input, session_state["order_state"])
                    session_state["order_state"] = updated_state
                    return f"I can help with that. {response}"
                else:
                    return f"I can help with that. {response}"
            
            else:
                # General Chat - Static Refusal
                # "acknowledge the question and say we dont support it"
                return "I'm sorry, I'm only capable of helping with order management and O2C process reporting. Please let me know if you'd like to report an order."
