import streamlit as st
import time
from llm_utils import set_api_key, set_model, AVAILABLE_MODELS

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
    from toc_analysis import analyze_toc, generate_crt_diagram, generate_toc_summary
    import streamlit_mermaid as stmd
    
    collected = st.session_state.get("order_state", {}).get("collected_data", {})
    
    # Run GAP analysis
    gap_result = analyze_gaps(collected)
    gap_summary = generate_gap_summary(gap_result)
    
    # Generate color-coded SAP diagram based on gaps
    sap_gap_diagram = generate_sap_gap_diagram(collected, gap_result)
    
    # Run ToC analysis
    toc_result = analyze_toc(collected)
    crt_diagram = generate_crt_diagram(toc_result)
    toc_summary = generate_toc_summary(toc_result)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Process GAP View", "📝 GAP Summary", "🔗 ToC Analysis"])
    
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
        
        # Add CSS for light background diagram container
        st.markdown("""
        <style>
            iframe[title="streamlit_mermaid.st_mermaid"] {
                background-color: #f8f9fa !important;
                border-radius: 10px;
                padding: 10px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # The color-coded SAP diagram
        stmd.st_mermaid(sap_gap_diagram, height=600)
    
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
    
    with tab3:
        st.subheader("🔗 Theory of Constraints - Current Reality Tree")
        
        st.markdown("""
        The **Current Reality Tree (CRT)** is a Theory of Constraints tool that identifies the 
        **core problems** in your process by linking visible symptoms (Undesirable Effects) 
        to their underlying root causes.
        """)
        
        # Legend
        st.markdown("""
        **Legend:** 🔴 UDE (Undesirable Effect) | 🔵 Root Cause | ⚪ Intermediate Effect
        """)
        
        # Add CSS for light background diagram container
        st.markdown("""
        <style>
            iframe[title="streamlit_mermaid.st_mermaid"] {
                background-color: #f8f9fa !important;
                border-radius: 10px;
                padding: 10px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # The CRT diagram
        if crt_diagram:
            try:
                stmd.st_mermaid(crt_diagram, height=700)
            except Exception as e:
                st.error(f"Failed to render CRT diagram: {e}")
                with st.expander("Debug: Diagram Code"):
                    st.code(crt_diagram, language="mermaid")
        else:
            st.warning("Unable to generate Current Reality Tree. Please complete more of the conversation.")
            # Debug: Show what toc_result contains
            with st.expander("Debug: ToC Analysis Result"):
                st.json(toc_result if toc_result else {"error": "No ToC result"})
        
        st.divider()
        
        # ToC Summary
        st.markdown(toc_summary)
    
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
