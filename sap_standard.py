"""
SAP Standard Order-to-Cash (O2C) Process Diagram
Limited to scope covered by chatbot:
1. Order Intake/Capturing
2. Order Verification (Commercial Validation)
3. Credit Governance
"""

# Pre-stored SAP Standard diagram - matches chatbot scope
SAP_STANDARD_O2C_DIAGRAM = '''graph TD
    %% SAP Standard: Order Intake, Verification, Credit Governance
    
    subgraph "1. Order Intake"
    Start((Order Received)) --> Channel{Order Channel}
    
    Channel -- EDI --> EDIProcess[EDI Processing - IDOC]
    Channel -- Portal --> PortalOrder[B2B Web Order]
    Channel -- Manual --> ManualEntry[Manual Entry - VA01]
    
    EDIProcess --> OrderCreate[Sales Order Created]
    PortalOrder --> OrderCreate
    ManualEntry --> OrderCreate
    
    OrderCreate --> Timestamp[Timestamp Recorded]
    Timestamp --> Confirmation[Order Confirmation Sent]
    end
    
    subgraph "2. Order Verification"
    OrderCreate --> SKUCheck{SKU Validation}
    SKUCheck -- Valid --> QtyCheck{Quantity Available - ATP}
    SKUCheck -- Invalid --> SKUError[Error: Invalid Material]
    
    QtyCheck -- Available --> PriceCheck{Pricing Validation}
    QtyCheck -- Not Available --> BackOrder[Backorder Created]
    
    PriceCheck -- Valid --> FOBCheck[FOB Terms Verified]
    PriceCheck -- Error --> PriceError[Price Discrepancy Alert]
    
    FOBCheck --> VerificationComplete[Order Data Complete]
    end
    
    subgraph "3. Credit Governance"
    VerificationComplete --> CreditCheck{Credit Check - VKM1}
    
    CreditCheck -- "Under Limit" --> AutoApprove[Auto-Approve & Release]
    CreditCheck -- "Over Limit" --> CreditQueue[Credit Block Queue]
    
    CreditQueue --> CreditAnalyst[Credit Analyst Review]
    CreditAnalyst --> CheckDB[Check D&B / Credit Score]
    CheckDB --> ReviewAR[Review AR Balance & History]
    ReviewAR --> CreditDecision{Decision}
    
    CreditDecision -- Approve --> ManualRelease[Release Order]
    CreditDecision -- Reject --> Reject[Order Rejected]
    CreditDecision -- Conditional --> Conditional[Conditional Approval]
    
    ManualRelease --> NotifySales[Notify Sales Rep]
    Conditional --> NotifySales
    Reject --> NotifySales
    
    NotifySales --> NotifyCustomer[Notify Customer]
    
    AutoApprove --> Released((Order Released))
    ManualRelease --> Released
    Conditional --> Released
    end
'''

# Simplified version for smaller displays
SAP_STANDARD_SIMPLE = '''graph LR
    A[Order Received] --> B{Channel}
    B --> C[EDI/Portal/Manual]
    C --> D[Order Created]
    D --> E{SKU Valid?}
    E --> F{Qty Available?}
    F --> G{Price Valid?}
    G --> H{Credit Check}
    H -- Auto --> I[Released]
    H -- Manual --> J[Credit Review]
    J --> K{Decision}
    K --> L[Notify Customer]
'''


def get_sap_standard_diagram(detailed=True):
    """
    Returns the SAP standard O2C process diagram.
    Pre-stored, not generated on the fly.
    """
    if detailed:
        return SAP_STANDARD_O2C_DIAGRAM
    return SAP_STANDARD_SIMPLE


# Best practices for each area (used in GAP analysis)
SAP_BEST_PRACTICES = {
    "order_origin_channels": {
        "standard": "Multi-channel: EDI for large accounts, B2B portal for mid-market, Manual entry as exception",
        "risk_if_missing": "Delayed order processing, manual data entry errors"
    },
    "manual_intake_method": {
        "standard": "Digitized intake via scanning/OCR, auto-create from email attachments",
        "risk_if_missing": "Manual transcription errors, slow processing"
    },
    "order_receiver": {
        "standard": "Dedicated Order Desk team with SLA-based queues",
        "risk_if_missing": "Orders lost in shared inboxes, unclear ownership"
    },
    "captured_data_fields": {
        "standard": "Customer ID, Material, Quantity, Price, Delivery Date, Ship-to, Payment Terms, PO Number",
        "risk_if_missing": "Incomplete orders requiring follow-up"
    },
    "primary_order_system": {
        "standard": "Integrated ERP (SAP S/4HANA) with real-time validation",
        "risk_if_missing": "Data silos, manual reconciliation needed"
    },
    "manual_data_verification": {
        "standard": "Required field validation in ERP before save",
        "risk_if_missing": "Incomplete orders progressing to fulfillment"
    },
    "automated_data_capture": {
        "standard": "100% validation - all required fields enforced before submission",
        "risk_if_missing": "Downstream errors and exceptions"
    },
    "required_verification_fields": {
        "standard": "Customer, Material, Qty, Price, Delivery Date, Ship-to, Credit Status",
        "risk_if_missing": "Invalid orders reaching fulfillment"
    },
    "verification_success_rate": {
        "standard": ">95% first-pass success rate",
        "risk_if_missing": "High rework and exception handling costs"
    },
    "verification_owner": {
        "standard": "System auto-validates, exceptions to Order Desk",
        "risk_if_missing": "Undefined accountability, delays"
    },
    "credit_approval_type": {
        "standard": "Automated credit scoring with rule-based limits",
        "risk_if_missing": "Inconsistent credit decisions"
    },
    "auto_approval_limit": {
        "standard": "Customer-specific based on credit score and history",
        "risk_if_missing": "One-size-fits-all limits may be too conservative or risky"
    },
    "manual_credit_approver": {
        "standard": "Credit Analyst with defined authority matrix",
        "risk_if_missing": "Approval bottlenecks, unclear escalation"
    },
    "credit_decision_factors": {
        "standard": "AR balance, DSO, Payment history, Credit score, Open orders value",
        "risk_if_missing": "Incomplete risk assessment"
    },
    "credit_decision_to_sales": {
        "standard": "Real-time dashboard notification + email",
        "risk_if_missing": "Sales unaware of order status"
    },
    "credit_decision_to_customer": {
        "standard": "Automated notification via preferred channel",
        "risk_if_missing": "Poor customer experience, no visibility"
    }
}
