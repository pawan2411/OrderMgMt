import streamlit as st
import time
from llm_utils import set_api_key, set_model, AVAILABLE_MODELS

# Page config
st.set_page_config(page_title="O2C Process Discovery", page_icon="📋", layout="wide")

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f3460 0%, #1a1a2e 100%);
        border-right: 1px solid #e94560;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e94560 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #edf2f4 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    
    h1 {
        background: linear-gradient(90deg, #e94560, #0f3460);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cards and containers */
    .stExpander {
        background-color: rgba(15, 52, 96, 0.5) !important;
        border: 1px solid #e94560 !important;
        border-radius: 10px !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 52, 96, 0.3);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(233, 69, 96, 0.2);
        border-radius: 8px;
        color: #edf2f4;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #e94560 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #e94560 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #e94560, #0f3460);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: rgba(15, 52, 96, 0.4) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(233, 69, 96, 0.3) !important;
        padding: 15px !important;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: rgba(15, 52, 96, 0.5);
        border: 1px solid #e94560;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* Success/Warning/Error alerts */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.2) !important;
        border-left: 4px solid #28a745 !important;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.2) !important;
        border-left: 4px solid #ffc107 !important;
    }
    
    .stError {
        background-color: rgba(220, 53, 69, 0.2) !important;
        border-left: 4px solid #dc3545 !important;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(233, 69, 96, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

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
    
    # Model selection dropdown
    selected_model = st.selectbox(
        "LLM Model",
        options=list(AVAILABLE_MODELS.keys()),
        index=0,
        help="72B is more accurate, 7B is faster"
    )
    set_model(AVAILABLE_MODELS[selected_model])
    
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
        
        # View Process Diagram button
        if len(collected) >= 3:
            st.divider()
            if st.button("📊 View Process Diagram", use_container_width=True):
                st.session_state["show_diagram"] = True
    else:
        st.info("Start the conversation to begin process discovery.")

# Main content
st.title("📋 Order-to-Cash Process Discovery")
st.markdown("I'm a consultant here to understand your end-to-end Order-to-Cash process.")

# Show Process Diagram if requested
if st.session_state.get("show_diagram", False):
    from sap_gap_diagram import generate_sap_gap_diagram, get_legend
    from gap_analysis import analyze_gaps, generate_gap_summary
    import streamlit_mermaid as stmd
    
    collected = st.session_state.get("order_state", {}).get("collected_data", {})
    
    # Run GAP analysis
    gap_result = analyze_gaps(collected)
    gap_summary = generate_gap_summary(gap_result)
    
    # Generate color-coded SAP diagram based on gaps
    sap_gap_diagram = generate_sap_gap_diagram(collected, gap_result)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📊 Process GAP View", "📝 GAP Summary"])
    
    with tab1:
        st.subheader("SAP Standard Process - Color-Coded by As-Is GAPs")
        
        # Show score and legend
        score = gap_result.get("score", 0)
        captured = gap_result.get("captured_count", 0)
        total_req = gap_result.get("total_required", 16)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if score >= 80:
                st.success(f"🟢 Alignment: {score}%")
            elif score >= 50:
                st.warning(f"🟡 Alignment: {score}%")
            else:
                st.error(f"🔴 Alignment: {score}%")
        with col2:
            st.caption(f"**{captured}/{total_req}** process areas captured")
        
        # Legend inline
        st.markdown("**Legend:** 🟢 Aligned | 🔴 Gap | ⚫ Not Captured")
        
        # The color-coded SAP diagram with white background
        st.markdown("""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; margin: 10px 0;">
        """, unsafe_allow_html=True)
        stmd.st_mermaid(sap_gap_diagram, height=600)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📝 GAP Analysis Summary")
        
        # Score display
        score = gap_result.get("score", 0)
        captured = gap_result.get("captured_count", 0)
        total_req = gap_result.get("total_required", 16)
        
        st.caption(f"**{captured}/{total_req}** process areas captured")
        
        if score >= 80:
            st.success(f"🟢 Alignment Score: {score}%")
        elif score >= 50:
            st.warning(f"🟡 Alignment Score: {score}%")
        else:
            st.error(f"🔴 Alignment Score: {score}%")
        
        st.divider()
        
        # GAP Summary
        st.markdown(gap_summary)
    
    st.divider()
    if st.button("🔙 Back to Chat", use_container_width=True):
        st.session_state["show_diagram"] = False
        st.rerun()
else:
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
