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
        
        # Progress bar
        from attribute_schema import REQUIRED_ATTRIBUTES, get_missing_attributes
        total_required = len([a for a, info in REQUIRED_ATTRIBUTES.items() if not info.get("optional", False)])
        real_collected = {k: v for k, v in collected.items() if v != "[Not discussed]"}
        captured_count = len(real_collected)
        progress = captured_count / total_required if total_required > 0 else 0
        
        st.progress(progress)
        st.caption(f"**{captured_count}/{total_required}** process aspects captured")
        
        # Current focus area
        current_focus = order_state.get("current_focus")
        if current_focus:
            st.subheader("🎯 Current Focus")
            st.write(f"**{current_focus.get('subclass', 'N/A')}**")
            st.caption(f"Looking for: {', '.join(current_focus.get('attributes', [])[:3])}")
        
        # Captured data (collapsible)
        if real_collected:
            with st.expander("✅ Captured Data", expanded=False):
                for attr, value in real_collected.items():
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

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

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
