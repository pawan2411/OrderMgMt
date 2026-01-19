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
        """Get inline style for an attribute"""
        if attr_key in gaps_set:
            return "fill:#dc3545,stroke:#c82333,color:#fff"  # Red
        elif attr_key in strengths_set:
            return "fill:#28a745,stroke:#1e7e34,color:#fff"  # Green
        elif attr_key in missing_set:
            return "fill:#6c757d,stroke:#545b62,color:#fff"  # Gray
        else:
            return "fill:#6c757d,stroke:#545b62,color:#fff"
    
    def get_label(attr_key, default_label):
        if attr_key in collected_data:
            val = str(collected_data[attr_key])[:18]
            return val
        return default_label
    
    node_styles = []
    
    manual_label = get_label("manual_intake_method", "Email/PDF")
    receiver_label = get_label("order_receiver", "Order Desk")
    system_label = get_label("primary_order_system", "ERP System")
    approver_label = get_label("manual_credit_approver", "Credit Analyst")
    
    diagram = '''graph TB
    %% BPMN-style O2C Process with Swim Lanes
    
    subgraph Customer["🧑‍💼 Customer"]
        C_Start((Start)) --> C_Order["Place Order"]
        C_Order --> C_Method{"Channel"}
    end
    
    subgraph SalesTeam["👥 Sales Team"]
        S_Manual["Receive " + ''' + f'"{manual_label}"' + ''']
        S_Enter["Enter Order"]
        S_Notify["Receive Decision"]
    end
    
    subgraph System["💻 ''' + system_label + '''"]
        SYS_Portal["Portal Order"]
        SYS_EDI["EDI Order"]
        SYS_Create["Create Sales Order"]
        SYS_Validate{"Data Validation"}
        SYS_Credit{"Credit Check"}
        SYS_Auto["Auto-Approve"]
        SYS_Release((Order Released))
    end
    
    subgraph CreditTeam["🏦 Credit Team"]
        CR_Queue["Credit Queue"]
        CR_Review["''' + approver_label + ''' Review"]
        CR_Decision{"Approve?"}
        CR_Notify["Notify Customer"]
    end
    
    %% Flow connections
    C_Method -- "Manual" --> S_Manual
    C_Method -- "Portal" --> SYS_Portal
    C_Method -- "EDI" --> SYS_EDI
    
    S_Manual --> S_Enter
    S_Enter --> SYS_Create
    SYS_Portal --> SYS_Create
    SYS_EDI --> SYS_Create
    
    SYS_Create --> SYS_Validate
    SYS_Validate -- "Pass" --> SYS_Credit
    SYS_Validate -- "Fail" --> S_Enter
    
    SYS_Credit -- "Under Limit" --> SYS_Auto
    SYS_Credit -- "Over Limit" --> CR_Queue
    
    CR_Queue --> CR_Review
    CR_Review --> CR_Decision
    CR_Decision -- "Yes" --> S_Notify
    CR_Decision -- "No" --> CR_Notify
    
    SYS_Auto --> SYS_Release
    S_Notify --> SYS_Release
    CR_Notify --> C_Order
    
'''
    
    # Add styles
    node_styles = [
        ("C_Method", get_style("order_origin_channels")),
        ("S_Manual", get_style("manual_intake_method")),
        ("S_Enter", get_style("order_receiver")),
        ("SYS_Create", get_style("primary_order_system")),
        ("SYS_Validate", get_style("required_verification_fields")),
        ("SYS_Credit", get_style("credit_approval_type")),
        ("SYS_Auto", get_style("auto_approval_limit")),
        ("CR_Review", get_style("manual_credit_approver")),
        ("CR_Decision", get_style("credit_decision_factors")),
        ("S_Notify", get_style("credit_decision_to_sales")),
        ("CR_Notify", get_style("credit_decision_to_customer")),
        ("SYS_Release", "fill:#28a745,stroke:#1e7e34,color:#fff"),
    ]
    
    for node_id, style in node_styles:
        diagram += f'    style {node_id} {style}\n'
    
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
