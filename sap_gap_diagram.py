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
    Generate SAP Standard diagram with color-coding based on As-Is gaps.
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
            return "fill:#6c757d,stroke:#545b62,color:#fff"  # Default gray
    
    def get_label(attr_key, default_label):
        if attr_key in collected_data:
            val = str(collected_data[attr_key])[:20]
            return val
        return default_label
    
    # Track nodes and their styles
    node_styles = []
    
    diagram = '''graph TD
'''
    
    # 1. Order Channels
    diagram += '    Start((Order Received)) --> IntakeChannel\n'
    diagram += '    IntakeChannel{"Order Channels"}\n'
    node_styles.append(("IntakeChannel", get_style("order_origin_channels")))
    
    # Manual intake
    manual_label = get_label("manual_intake_method", "Email/PDF/Fax")
    diagram += f'    IntakeChannel -- Manual --> ManualIntake["{manual_label}"]\n'
    node_styles.append(("ManualIntake", get_style("manual_intake_method")))
    
    # Automated
    diagram += '    IntakeChannel -- Automated --> AutoChannel["Portal / EDI"]\n'
    node_styles.append(("AutoChannel", "fill:#28a745,stroke:#1e7e34,color:#fff"))
    
    # Order receiver
    receiver_label = get_label("order_receiver", "Order Desk Team")
    diagram += f'    ManualIntake --> Receiver["{receiver_label}"]\n'
    node_styles.append(("Receiver", get_style("order_receiver")))
    
    diagram += '    AutoChannel --> SystemEntry\n'
    diagram += '    Receiver --> SystemEntry\n'
    
    # System Entry
    system_label = get_label("primary_order_system", "ERP System")
    diagram += f'    SystemEntry["{system_label}"]\n'
    node_styles.append(("SystemEntry", get_style("primary_order_system")))
    
    # Data capture
    diagram += '    SystemEntry --> DataCapture{"Data Capture"}\n'
    node_styles.append(("DataCapture", get_style("captured_data_fields")))
    
    # Verification
    diagram += '    DataCapture --> Verification{"Order Verification"}\n'
    node_styles.append(("Verification", get_style("required_verification_fields")))
    
    diagram += '    Verification --> ManualVerify["Manual Check"]\n'
    node_styles.append(("ManualVerify", get_style("manual_data_verification")))
    
    diagram += '    Verification --> AutoVerify["System Validation"]\n'
    node_styles.append(("AutoVerify", get_style("automated_data_capture")))
    
    success_label = get_label("verification_success_rate", "Success Rate")
    diagram += f'    ManualVerify --> SuccessRate["{success_label}"]\n'
    diagram += '    AutoVerify --> SuccessRate\n'
    node_styles.append(("SuccessRate", get_style("verification_success_rate")))
    
    owner_label = get_label("verification_owner", "Verification Owner")
    diagram += f'    SuccessRate --> Owner["{owner_label}"]\n'
    node_styles.append(("Owner", get_style("verification_owner")))
    
    diagram += '    Owner --> CreditCheck\n'
    
    # Credit Governance
    diagram += '    CreditCheck{"Credit Governance"}\n'
    node_styles.append(("CreditCheck", get_style("credit_approval_type")))
    
    auto_limit_label = get_label("auto_approval_limit", "< Threshold")
    diagram += f'    CreditCheck -- "{auto_limit_label}" --> AutoApprove["Auto-Approve"]\n'
    node_styles.append(("AutoApprove", get_style("auto_approval_limit")))
    
    approver_label = get_label("manual_credit_approver", "Credit Analyst")
    diagram += f'    CreditCheck -- "Above Limit" --> ManualApprover["{approver_label}"]\n'
    node_styles.append(("ManualApprover", get_style("manual_credit_approver")))
    
    factors_label = get_label("credit_decision_factors", "Credit Factors")
    diagram += f'    ManualApprover --> Factors["{factors_label}"]\n'
    node_styles.append(("Factors", get_style("credit_decision_factors")))
    
    diagram += '    Factors --> Decision\n'
    diagram += '    Decision{"Decision"}\n'
    
    diagram += '    Decision --> NotifySales["Notify Sales"]\n'
    node_styles.append(("NotifySales", get_style("credit_decision_to_sales")))
    
    diagram += '    Decision --> NotifyCustomer["Notify Customer"]\n'
    node_styles.append(("NotifyCustomer", get_style("credit_decision_to_customer")))
    
    diagram += '    AutoApprove --> Released((Order Released))\n'
    diagram += '    NotifySales --> Released\n'
    diagram += '    NotifyCustomer --> Released\n'
    node_styles.append(("Released", "fill:#28a745,stroke:#1e7e34,color:#fff"))
    
    # Add style statements
    diagram += '\n'
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
