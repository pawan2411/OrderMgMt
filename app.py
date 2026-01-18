import streamlit as st
import time
from llm_utils import set_api_key

# Page config
st.set_page_config(page_title="O2C Process Discovery", page_icon="📋", layout="wide")

# Sidebar: API Key and Progress
with st.sidebar:
    st.header("🔑 Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Together AI API Key",
        type="password",
        placeholder="Enter your Together AI API key",
        help="Get your API key from https://api.together.xyz"
    )
    
    if api_key:
        set_api_key(api_key)
        st.success("✅ API Key set!")
    else:
        st.warning("⚠️ Please enter your API key to start")
    
    st.divider()
    st.header("📊 Process Discovery Progress")
    
    if "order_state" in st.session_state:
        order_state = st.session_state["order_state"]
        collected = order_state.get("collected_data", {})
        
        # Progress bar using new hierarchical schema
        from attribute_schema import get_progress, get_next_question_info
        answered, total = get_progress(collected)
        progress = answered / total if total > 0 else 0
        
        st.progress(progress)
        st.caption(f"**{answered}/{total}** questions answered")
        
        # Current question
        current_q_id = order_state.get("current_question_id")
        if current_q_id:
            st.subheader("🎯 Current Question")
            st.write(f"**Q{current_q_id}**")
        
        # Captured data (collapsible)
        if collected:
            with st.expander("✅ Captured Data", expanded=False):
                for attr, value in collected.items():
                    display_val = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                    st.write(f"**{attr}:** {display_val}")
    else:
        st.info("Start the conversation to begin process discovery.")

# Main content
st.title("📋 Order-to-Cash Process Discovery")
st.markdown("I'm a consultant here to understand your end-to-end Order-to-Cash process.")

# Initialize Orchestrator only after API key is set
if api_key:
    from orchestrator import Orchestrator
    
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = Orchestrator()

    # Initialize Chat History with opening message
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Start the conversation with opening message
        from order_mgmt import OrderManager
        mgr = OrderManager()
        opening, state = mgr.start_conversation()
        st.session_state.messages.append({"role": "assistant", "content": opening})
        st.session_state["order_state"] = state
        st.session_state["mode"] = "ORDER_MGMT"

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Describe your order process..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Call Orchestrator
            response = st.session_state.orchestrator.handle_message(prompt, st.session_state)
            
            # Simulate typing effect
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.02)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Rerun to update sidebar
        st.rerun()
else:
    st.info("👈 Please enter your Together AI API key in the sidebar to start the conversation.")
