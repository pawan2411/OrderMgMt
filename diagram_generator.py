"""
Generates Mermaid diagrams from captured O2C process data.
"""

def generate_process_diagram(collected_data):
    """
    Generate a Mermaid diagram based on captured process data.
    Returns a Mermaid graph definition string.
    """
    if not collected_data:
        return None
    
    # Extract key data points with defaults
    channels = collected_data.get("order_origin_channels", "Unknown channels")
    manual_method = collected_data.get("manual_intake_method", "")
    receiver = collected_data.get("order_receiver", "Order Team")
    system = collected_data.get("primary_order_system", "System")
    uses_erp = collected_data.get("uses_erp", "Unknown")
    
    has_manual = collected_data.get("has_manual_intake", "No") == "Yes"
    has_portal = "portal" in channels.lower() or "b2b" in channels.lower()
    has_edi = "edi" in channels.lower()
    
    credit_type = collected_data.get("credit_approval_type", "")
    has_auto = collected_data.get("has_auto_approval", "No") == "Yes"
    has_manual_credit = collected_data.get("has_manual_credit", "No") == "Yes"
    auto_limit = collected_data.get("auto_approval_limit", "$50k")
    credit_approver = collected_data.get("manual_credit_approver", "Credit Analyst")
    credit_factors = collected_data.get("credit_decision_factors", "AR balance, history")
    
    # Build the diagram
    diagram = '''graph TD
    %% Start
    Start((Order Received)) --> IntakeType{Intake Channel}
'''
    
    # Intake channels
    if has_manual:
        manual_desc = f"Receive {manual_method}" if manual_method else "Manual Entry"
        diagram += f'''
    %% Manual Lane
    subgraph "{receiver} Lane"
    IntakeType -- Manual --> ManEntry["{manual_desc}"]
    ManEntry --> SystemEntry
    InformCust[Inform Customer]
    end
'''
    
    if has_portal or has_edi:
        diagram += '''
    %% Automated Channels
    subgraph "Customer Pool"
'''
        if has_portal:
            diagram += '    Portal[Submit via B2B Portal]\n'
        if has_edi:
            diagram += '    EDI[Send EDI Order]\n'
        diagram += '    end\n'
        
        if has_portal:
            diagram += '    IntakeType -- Portal --> Portal\n'
            diagram += '    Portal --> SystemEntry\n'
        if has_edi:
            diagram += '    IntakeType -- EDI --> EDI\n'
            diagram += '    EDI --> SystemEntry\n'
    
    # ERP/System processing
    system_label = f"{system}" if uses_erp == "ERP" else f"{system}"
    diagram += f'''
    %% System Processing
    subgraph "{system_label} Lane"
    SystemEntry[Create Order Record]
    CreditGate{{Credit Check}}
    SystemEntry --> CreditGate
'''
    
    # Credit logic
    if has_auto:
        diagram += f'    CreditGate -- "< {auto_limit}" --> AutoApprove[Auto-Approve]\n'
    
    if has_manual_credit:
        diagram += f'    CreditGate -- "Above threshold" --> FlagQueue[Flag for Review]\n'
        diagram += '    UpdateStatus[Update Status]\n'
        diagram += '    end\n'
        
        # Credit analyst lane
        diagram += f'''
    %% Credit Review Lane
    subgraph "{credit_approver} Lane"
    FlagQueue --> Review[Review Dashboard]
    Review --> CheckData[Check {credit_factors[:20]}...]
    CheckData --> Decision{{Decision}}
    Decision -- Approve --> UpdateStatus
    Decision -- Reject --> UpdateStatus
    Decision -- Conditional --> UpdateStatus
    end
'''
    else:
        diagram += '    end\n'
    
    # End flow
    if has_auto:
        diagram += '    AutoApprove --> EndProcess((Continue to Fulfillment))\n'
    if has_manual_credit:
        diagram += '    UpdateStatus --> EndProcess\n'
    elif not has_auto:
        diagram += '    CreditGate --> EndProcess((Continue to Fulfillment))\n'
    
    return diagram


def get_simple_diagram(collected_data):
    """
    Returns a simpler overview diagram when limited data is available.
    """
    if len(collected_data) < 3:
        return None
    
    diagram = '''graph LR
    A[Order Received] --> B{Channel}
'''
    
    channels = collected_data.get("order_origin_channels", "")
    if "manual" in channels.lower() or "email" in channels.lower() or "pdf" in channels.lower():
        diagram += '    B --> C[Manual Entry]\n'
    if "portal" in channels.lower() or "b2b" in channels.lower():
        diagram += '    B --> D[Portal]\n'
    if "edi" in channels.lower():
        diagram += '    B --> E[EDI]\n'
    
    system = collected_data.get("primary_order_system", "")
    if system:
        diagram += f'    C --> F[{system}]\n'
        diagram += f'    D --> F\n'
        diagram += f'    E --> F\n'
    
    credit = collected_data.get("credit_approval_type", "")
    if credit:
        diagram += '    F --> G{Credit Check}\n'
        if "auto" in credit.lower():
            diagram += '    G --> H[Auto-Approve]\n'
        if "manual" in credit.lower():
            diagram += '    G --> I[Manual Review]\n'
        diagram += '    H --> J((Fulfillment))\n'
        diagram += '    I --> J\n'
    else:
        diagram += '    F --> J((Fulfillment))\n'
    
    return diagram
