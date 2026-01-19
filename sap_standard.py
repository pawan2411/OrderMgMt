"""
SAP Standard Order-to-Cash (O2C) Process Diagram

Based on SAP ERP best practices and standard O2C flow:
1. Pre-Sales Activities
2. Sales Order Processing  
3. Credit Management
4. Availability Check
5. Delivery Processing
6. Picking & Packing
7. Post Goods Issue (PGI)
8. Shipping
9. Billing
10. Accounts Receivable & Payment
"""

SAP_STANDARD_O2C_DIAGRAM = '''graph TD
    %% SAP Standard Order-to-Cash Process
    
    subgraph "1. Pre-Sales"
    Inquiry[Customer Inquiry] --> Quotation[Create Quotation]
    Quotation --> QuoteApproval{Quote Accepted?}
    end
    
    subgraph "2. Sales Order Processing"
    QuoteApproval -- Yes --> SalesOrder[Create Sales Order - VA01]
    SalesOrder --> OrderConf[Order Confirmation to Customer]
    end
    
    subgraph "3. Credit & Availability Check"
    SalesOrder --> CreditCheck{Credit Check - VKM1}
    CreditCheck -- Blocked --> CreditRelease[Credit Manager Release]
    CreditRelease --> ATPCheck
    CreditCheck -- Passed --> ATPCheck{ATP Check}
    ATPCheck -- Available --> Delivery
    ATPCheck -- Not Available --> BackOrder[Backorder Processing]
    BackOrder --> MRP[MRP/Production Planning]
    MRP --> ATPCheck
    end
    
    subgraph "4. Delivery Processing"
    Delivery[Create Outbound Delivery - VL01N]
    Delivery --> Picking[Picking - LT03]
    Picking --> Packing[Packing - VL02N]
    end
    
    subgraph "5. Goods Issue & Shipping"
    Packing --> PGI[Post Goods Issue - VL02N]
    PGI --> ShipDoc[Shipment Document - VT01N]
    ShipDoc --> CarrierLabel[Carrier Label & Tracking]
    CarrierLabel --> ASN[Send ASN to Customer]
    end
    
    subgraph "6. Billing"
    PGI --> BillingDue[Billing Due List - VF04]
    BillingDue --> Invoice[Create Invoice - VF01]
    Invoice --> OutputInv[Send Invoice to Customer]
    Invoice --> AcctDoc[Accounting Document - FI]
    end
    
    subgraph "7. Accounts Receivable"
    AcctDoc --> AR[Accounts Receivable - FBL5N]
    AR --> Payment{Payment Received?}
    Payment -- Yes --> CashApp[Cash Application - F-28]
    Payment -- No --> Dunning[Dunning Process - F150]
    Dunning --> Collections[Collections Management]
    Collections --> Payment
    CashApp --> Cleared[Invoice Cleared]
    end
    
    %% End
    Cleared --> Complete((O2C Complete))
    ASN --> Complete
'''

SAP_STANDARD_SIMPLE = '''graph LR
    A[Inquiry] --> B[Quotation]
    B --> C[Sales Order]
    C --> D{Credit Check}
    D --> E{ATP Check}
    E --> F[Delivery]
    F --> G[Picking]
    G --> H[Packing]
    H --> I[Goods Issue]
    I --> J[Shipping]
    I --> K[Billing]
    K --> L[Invoice]
    L --> M[Payment]
    M --> N[Cash Applied]
'''


def get_sap_standard_diagram(detailed=True):
    """
    Returns the SAP standard O2C process diagram.
    
    detailed: If True, returns full diagram with subgraphs.
              If False, returns simplified linear flow.
    """
    if detailed:
        return SAP_STANDARD_O2C_DIAGRAM
    return SAP_STANDARD_SIMPLE


def get_comparison_info():
    """
    Returns information about SAP standard process for comparison.
    """
    return {
        "stages": [
            "Pre-Sales (Inquiry, Quotation)",
            "Sales Order Processing (VA01)",
            "Credit Management (VKM1)",
            "Availability Check (ATP)",
            "Delivery Processing (VL01N)",
            "Picking (LT03) & Packing",
            "Post Goods Issue (PGI)",
            "Shipping (VT01N)",
            "Billing (VF01)",
            "Accounts Receivable (FBL5N)",
            "Cash Application (F-28)"
        ],
        "key_tcodes": {
            "VA01": "Create Sales Order",
            "VL01N": "Create Outbound Delivery",
            "VL02N": "Change Delivery / Post GI",
            "VF01": "Create Billing Document",
            "VKM1": "Credit Management",
            "F-28": "Incoming Payment",
            "FBL5N": "Customer Line Items"
        }
    }
