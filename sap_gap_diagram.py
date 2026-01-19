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
    
    This is the SAP standard process, but nodes are colored to show:
    - What has been captured (vs not captured)
    - Where gaps exist vs aligned
    """
    gaps_set = {g["attribute"] for g in gap_analysis.get("gaps", [])}
    missing_set = {m["attribute"] for m in gap_analysis.get("missing", [])}
    strengths_set = {s["attribute"] for s in gap_analysis.get("strengths", [])}
    
    def get_class(attr_key):
        """Get color class for an attribute"""
        if attr_key in gaps_set:
            return "red"  # Captured but has gap
        elif attr_key in strengths_set:
            return "green"  # Captured and aligned
        elif attr_key in missing_set:
            return "gray"  # Not yet captured
        else:
            return "default"
    
    # Get actual captured values for labels
    def get_label(attr_key, default_label):
        if attr_key in collected_data:
            val = str(collected_data[attr_key])[:25]
            return f"{val}..."[:25] if len(val) >= 25 else val
        return default_label
    
    diagram = '''graph TD
    %% SAP Standard O2C - Color-coded by As-Is GAP Analysis
    %% Green = Aligned | Red = Gap | Yellow = Partial | Gray = Not Captured
    
    classDef green fill:#28a745,stroke:#1e7e34,color:#fff
    classDef red fill:#dc3545,stroke:#c82333,color:#fff
    classDef yellow fill:#ffc107,stroke:#d39e00,color:#000
    classDef gray fill:#6c757d,stroke:#545b62,color:#fff
    classDef default fill:#6c757d,stroke:#545b62,color:#fff
    
    Start((Order Received)) --> IntakeChannel
'''
    
    # 1. Order Intake Section
    channel_class = get_class("order_origin_channels")
    diagram += f'    IntakeChannel{{{{"Order Channels"}}}}:::{channel_class}\n'
    
    # Manual intake
    manual_class = get_class("manual_intake_method")
    manual_label = get_label("manual_intake_method", "Email/PDF/Fax")
    diagram += f'    IntakeChannel -- Manual --> ManualIntake["{manual_label}"]:::{manual_class}\n'
    
    # Automated channels
    diagram += f'    IntakeChannel -- Automated --> AutoChannel["Portal / EDI"]:::green\n'
    
    # Order receiver
    receiver_class = get_class("order_receiver")
    receiver_label = get_label("order_receiver", "Order Desk Team")
    diagram += f'    ManualIntake --> Receiver["{receiver_label}"]:::{receiver_class}\n'
    diagram += f'    AutoChannel --> SystemEntry\n'
    diagram += f'    Receiver --> SystemEntry\n'
    
    # 2. System Entry
    system_class = get_class("primary_order_system")
    system_label = get_label("primary_order_system", "ERP System")
    diagram += f'    SystemEntry["{system_label}"]:::{system_class}\n'
    
    # Data capture
    data_class = get_class("captured_data_fields")
    diagram += f'    SystemEntry --> DataCapture{{{{"Data Capture"}}}}:::{data_class}\n'
    
    # 3. Order Verification Section
    verify_class = get_class("required_verification_fields")
    diagram += f'    DataCapture --> Verification{{{{"Order Verification"}}}}:::{verify_class}\n'
    
    # Verification methods
    manual_verify_class = get_class("manual_data_verification")
    auto_verify_class = get_class("automated_data_capture")
    diagram += f'    Verification --> ManualVerify["Manual Check"]:::{manual_verify_class}\n'
    diagram += f'    Verification --> AutoVerify["System Validation"]:::{auto_verify_class}\n'
    
    # Success rate
    success_class = get_class("verification_success_rate")
    success_label = get_label("verification_success_rate", "Success Rate")
    diagram += f'    ManualVerify --> SuccessRate["{success_label}"]:::{success_class}\n'
    diagram += f'    AutoVerify --> SuccessRate\n'
    
    # Owner
    owner_class = get_class("verification_owner")
    owner_label = get_label("verification_owner", "Verification Owner")
    diagram += f'    SuccessRate --> Owner["{owner_label}"]:::{owner_class}\n'
    diagram += f'    Owner --> CreditCheck\n'
    
    # 4. Credit Governance Section
    credit_class = get_class("credit_approval_type")
    diagram += f'    CreditCheck{{{{"Credit Governance"}}}}:::{credit_class}\n'
    
    # Auto approval
    auto_limit_class = get_class("auto_approval_limit")
    auto_limit_label = get_label("auto_approval_limit", "< Threshold")
    diagram += f'    CreditCheck -- "{auto_limit_label}" --> AutoApprove["Auto-Approve"]:::{auto_limit_class}\n'
    
    # Manual approval
    approver_class = get_class("manual_credit_approver")
    approver_label = get_label("manual_credit_approver", "Credit Analyst")
    diagram += f'    CreditCheck -- "Above Limit" --> ManualApprover["{approver_label}"]:::{approver_class}\n'
    
    # Decision factors
    factors_class = get_class("credit_decision_factors")
    factors_label = get_label("credit_decision_factors", "Credit Factors")
    diagram += f'    ManualApprover --> Factors["{factors_label}"]:::{factors_class}\n'
    diagram += f'    Factors --> Decision\n'
    
    # Notifications
    notify_sales_class = get_class("credit_decision_to_sales")
    notify_cust_class = get_class("credit_decision_to_customer")
    diagram += f'    Decision{{{{"Decision"}}}} --> NotifySales["Notify Sales"]:::{notify_sales_class}\n'
    diagram += f'    Decision --> NotifyCustomer["Notify Customer"]:::{notify_cust_class}\n'
    
    # End
    diagram += f'    AutoApprove --> Released((Order Released)):::green\n'
    diagram += f'    NotifySales --> Released\n'
    diagram += f'    NotifyCustomer --> Released\n'
    
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
