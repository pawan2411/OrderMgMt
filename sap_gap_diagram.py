"""
SAP Standard Order-to-Cash (O2C) Process Diagram
Dynamically color-coded based on As-Is captured data to show gaps.

Color coding:
- Green: Captured and aligned with standard
- Red: Captured but has gap
- Yellow: Partially aligned
- Gray: Not yet captured
"""


def generate_sap_gap_diagram(collected_data, gap_analysis):
    """
    Generate BPMN-style SAP diagram with swim lanes, color-coded by gaps.
    """
    gaps_set = {g["attribute"] for g in gap_analysis.get("gaps", [])}
    missing_set = {m["attribute"] for m in gap_analysis.get("missing", [])}
    strengths_set = {s["attribute"] for s in gap_analysis.get("strengths", [])}
    
    def get_style(attr_key):
        if attr_key in gaps_set:
            return "fill:#dc3545,stroke:#c82333,color:#fff"
        elif attr_key in strengths_set:
            return "fill:#28a745,stroke:#1e7e34,color:#fff"
        else:
            return "fill:#6c757d,stroke:#545b62,color:#fff"
    
    def get_label(attr_key, default_label):
        if attr_key in collected_data:
            return str(collected_data[attr_key])[:15]
        return default_label
    
    manual_label = get_label("manual_intake_method", "Email/PDF")
    system_label = get_label("primary_order_system", "ERP System")
    approver_label = get_label("manual_credit_approver", "Credit Analyst")
    
    diagram = f'''%%{{init: {{'theme': 'base', 'themeVariables': {{ 'lineColor': '#FFFFFF', 'primaryTextColor': '#000000', 'secondaryTextColor': '#FFFFFF', 'tertiaryTextColor': '#FFFFFF' }}}}}}%%
graph TB
    subgraph Customer["Customer"]
        C_Start((Start)) --> C_Order["Place Order"]
        C_Order --> C_Method{{"Channel"}}
    end
    
    subgraph Sales["Sales Team"]
        S_Manual["Receive {manual_label}"]
        S_Enter["Enter Order"]
        S_Notify["Receive Decision"]
    end
    
    subgraph System["{system_label}"]
        SYS_Portal["Portal Order"]
        SYS_EDI["EDI Order"]
        SYS_Create["Create Sales Order"]
        SYS_Validate{{"Data Validation"}}
        SYS_Credit{{"Credit Check"}}
        SYS_Auto["Auto-Approve"]
        SYS_Release((Released))
    end
    
    subgraph Credit["Credit Team"]
        CR_Queue["Credit Queue"]
        CR_Review["{approver_label} Review"]
        CR_Decision{{"Approve?"}}
        CR_Notify["Notify Customer"]
    end
    
    C_Method -- Manual --> S_Manual
    C_Method -- Portal --> SYS_Portal
    C_Method -- EDI --> SYS_EDI
    
    S_Manual --> S_Enter
    S_Enter --> SYS_Create
    SYS_Portal --> SYS_Create
    SYS_EDI --> SYS_Create
    
    SYS_Create --> SYS_Validate
    SYS_Validate -- Pass --> SYS_Credit
    SYS_Validate -- Fail --> S_Enter
    
    SYS_Credit -- Under_Limit --> SYS_Auto
    SYS_Credit -- Over_Limit --> CR_Queue
    
    CR_Queue --> CR_Review
    CR_Review --> CR_Decision
    CR_Decision -- Yes --> S_Notify
    CR_Decision -- No --> CR_Notify
    
    SYS_Auto --> SYS_Release
    S_Notify --> SYS_Release
    CR_Notify --> C_Order

    style C_Method {get_style("order_origin_channels")}
    style S_Manual {get_style("manual_intake_method")}
    style S_Enter {get_style("order_receiver")}
    style SYS_Create {get_style("primary_order_system")}
    style SYS_Validate {get_style("required_verification_fields")}
    style SYS_Credit {get_style("credit_approval_type")}
    style SYS_Auto {get_style("auto_approval_limit")}
    style CR_Review {get_style("manual_credit_approver")}
    style CR_Decision {get_style("credit_decision_factors")}
    style S_Notify {get_style("credit_decision_to_sales")}
    style CR_Notify {get_style("credit_decision_to_customer")}
    style SYS_Release fill:#28a745,stroke:#1e7e34,color:#fff
'''
    
    return diagram


def get_legend():
    """Returns a legend explaining the color coding"""
    return """
**Legend:**
- 🟢 **Green**: Captured and aligned with SAP best practice
- 🔴 **Red**: Captured but deviates from best practice (GAP)
- 🟡 **Yellow**: Partially aligned
- ⚫ **Gray**: Not yet captured - complete the interview
"""
