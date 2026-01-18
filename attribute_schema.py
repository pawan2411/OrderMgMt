"""
Attribute Schema for Order-to-Cash PROCESS DISCOVERY
These attributes describe HOW a company manages orders, NOT a single order's data.
"""

# Define the natural O2C flow order for subclasses
SUBCLASS_FLOW_ORDER = [
    ("Order Demand & Validation", "Order Intake"),
    ("Order Demand & Validation", "Commercial Validation"),
    ("Order Demand & Validation", "Credit Governance"),
    ("Fulfillment & Distribution", "Inventory & Production"),
    ("Fulfillment & Distribution", "Warehouse Operations"),
    ("Fulfillment & Distribution", "Transportation Management"),
    ("Revenue Realization & Invoicing", "Billing Execution"),
    ("Revenue Realization & Invoicing", "Revenue Accounting"),
    ("Financial Settlements & Recovery", "Cash Application"),
    ("Financial Settlements & Recovery", "Dispute & Deduction Management"),
    ("Financial Settlements & Recovery", "Collections & Dunning"),
    ("Master Data & Lifecycle Support", "Customer Master & Onboarding"),
    ("Master Data & Lifecycle Support", "Reverse Logistics"),
    ("Master Data & Lifecycle Support", "Reporting & Audit Controls"),
]

# All process attributes - these describe HOW the company handles each aspect
REQUIRED_ATTRIBUTES = {
    # Class 1: Order Demand & Validation - Order Intake
    "source_channel": {
        "description": "What channels do orders come through",
        "process_question": "How do orders come into your organization?",
        "examples": ["EDI 850 from retailers", "B2B Portal", "Manual Email/PDF entry by sales team"],
        "class": "Order Demand & Validation",
        "subclass": "Order Intake",
        "order": 1
    },
    "intake_timestamp": {
        "description": "How order receipt time is tracked",
        "process_question": "How do you track when orders are received?",
        "examples": ["ERP timestamp on entry", "Email receipt time", "Manual logging"],
        "class": "Order Demand & Validation",
        "subclass": "Order Intake",
        "order": 2,
        "optional": True
    },
    "order_completeness_score": {
        "description": "How order data completeness is measured",
        "process_question": "How do you ensure orders have all necessary data? Is there a checklist?",
        "examples": ["Required field checklist in ERP", "Variable adherence", "No formal process"],
        "class": "Order Demand & Validation",
        "subclass": "Order Intake",
        "order": 3
    },
    
    # Commercial Validation
    "sku_validity": {
        "description": "How SKU validity is checked",
        "process_question": "How do you validate that the SKU/product exists and is valid?",
        "examples": ["ERP auto-validates", "Manual lookup", "No validation"],
        "class": "Order Demand & Validation",
        "subclass": "Commercial Validation",
        "order": 4,
        "optional": True
    },
    "quantity_availability": {
        "description": "How inventory availability is checked",
        "process_question": "How do you check if the quantity is available?",
        "examples": ["Real-time ATP check", "Warehouse confirms", "Separate inventory system"],
        "class": "Order Demand & Validation",
        "subclass": "Commercial Validation",
        "order": 5,
        "optional": True
    },
    "pricing_logic": {
        "description": "How pricing is determined and validated",
        "process_question": "How is pricing determined - contractual, promotional, or list price?",
        "examples": ["Contractual pricing in master", "Manual promo code entry", "Price lists"],
        "class": "Order Demand & Validation",
        "subclass": "Commercial Validation",
        "order": 6
    },
    "fob_terms": {
        "description": "How FOB/shipping terms are captured",
        "process_question": "How are FOB terms and shipping instructions captured?",
        "examples": ["Customer master default", "Order-specific entry", "Often missed"],
        "class": "Order Demand & Validation",
        "subclass": "Commercial Validation",
        "order": 7,
        "optional": True
    },
    
    # Credit Governance
    "credit_limit": {
        "description": "How credit limits are managed",
        "process_question": "What credit limits exist and how are they managed?",
        "examples": ["$50,000 threshold for auto-approval", "Customer-specific limits", "No limits"],
        "class": "Order Demand & Validation",
        "subclass": "Credit Governance",
        "order": 8
    },
    "risk_scoring": {
        "description": "How credit risk is assessed",
        "process_question": "How do you assess credit risk? Any external ratings used?",
        "examples": ["D&B Rating checked manually", "Internal scoring", "No formal scoring"],
        "class": "Order Demand & Validation",
        "subclass": "Credit Governance",
        "order": 9
    },
    "approval_workflow": {
        "description": "How credit approval workflow operates",
        "process_question": "Walk me through the credit approval process. Auto-approval vs manual?",
        "examples": ["Auto-approve under threshold", "Manual analyst queue", "Manager approval required"],
        "class": "Order Demand & Validation",
        "subclass": "Credit Governance",
        "order": 10
    },
    "order_status": {
        "description": "What order statuses exist after validation",
        "process_question": "What happens after credit review - what are the possible outcomes?",
        "examples": ["Released, Blocked, Conditional", "Approved with conditions", "Reject or accept only"],
        "class": "Order Demand & Validation",
        "subclass": "Credit Governance",
        "order": 11
    },
    
    # Fulfillment & Distribution - Inventory & Production
    "stock_category": {
        "description": "How stock types are managed (MTS vs MTO)",
        "process_question": "Is this make-to-stock or make-to-order? How does that work?",
        "examples": ["MTS for standard items", "MTO goes to production queue", "Mixed"],
        "class": "Fulfillment & Distribution",
        "subclass": "Inventory & Production",
        "order": 12
    },
    "warehouse_assignment": {
        "description": "How warehouse/DC is assigned",
        "process_question": "How is the fulfilling warehouse determined?",
        "examples": ["Customer region-based", "Inventory availability", "Single warehouse"],
        "class": "Fulfillment & Distribution",
        "subclass": "Inventory & Production",
        "order": 13
    },
    "production_queue_status": {
        "description": "How production scheduling works for MTO",
        "process_question": "For made-to-order items, how does production scheduling work?",
        "examples": ["Goes to production queue", "Scheduler reviews daily", "Not applicable - all MTS"],
        "class": "Fulfillment & Distribution",
        "subclass": "Inventory & Production",
        "order": 14
    },
    
    # Warehouse Operations
    "picking_document_type": {
        "description": "How pick lists are generated and used",
        "process_question": "How does the warehouse know what to pick? Paper lists or RF scanners?",
        "examples": ["Paper pick lists", "RF Scanner Task", "WMS-directed picking"],
        "class": "Fulfillment & Distribution",
        "subclass": "Warehouse Operations",
        "order": 15
    },
    "packing_status": {
        "description": "How packing process works",
        "process_question": "How does packing work? Pack slips, verification?",
        "examples": ["Pack slip printed automatically", "Scan to verify", "Manual paper process"],
        "class": "Fulfillment & Distribution",
        "subclass": "Warehouse Operations",
        "order": 16,
        "optional": True
    },
    "system_reliability_metric": {
        "description": "Reliability of warehouse systems",
        "process_question": "How reliable are the warehouse systems? Any issues?",
        "examples": ["Scanner uptime 95%", "Old system crashes frequently", "Reliable"],
        "class": "Fulfillment & Distribution",
        "subclass": "Warehouse Operations",
        "order": 17,
        "optional": True
    },
    
    # Transportation Management
    "carrier_selection": {
        "description": "How carriers are selected",
        "process_question": "How is the carrier selected? LTL, small parcel, etc.?",
        "examples": ["FedEx/UPS for small parcel", "LTL for larger", "Rate shopping"],
        "class": "Fulfillment & Distribution",
        "subclass": "Transportation Management",
        "order": 18
    },
    "tracking_id": {
        "description": "How tracking numbers are managed",
        "process_question": "How are tracking numbers generated and communicated?",
        "examples": ["Carrier portal generates", "Manually typed into ERP", "API integration"],
        "class": "Fulfillment & Distribution",
        "subclass": "Transportation Management",
        "order": 19
    },
    "shipping_mode": {
        "description": "Shipping modes available",
        "process_question": "What shipping modes do you offer?",
        "examples": ["Ground, Express, 2-day", "Customer-specified", "Standard only"],
        "class": "Fulfillment & Distribution",
        "subclass": "Transportation Management",
        "order": 20,
        "optional": True
    },
    "data_integrity_type": {
        "description": "How shipping data flows between systems",
        "process_question": "How does shipping data flow - manual re-key or API integration?",
        "examples": ["Manual re-key to carrier portals", "API integration", "EDI"],
        "class": "Fulfillment & Distribution",
        "subclass": "Transportation Management",
        "order": 21
    },
    
    # Revenue Realization - Billing Execution
    "generation_trigger": {
        "description": "What triggers invoice generation",
        "process_question": "When does invoicing happen? What triggers it?",
        "examples": ["Post-Goods Issue", "When marked shipped", "Manual trigger"],
        "class": "Revenue Realization & Invoicing",
        "subclass": "Billing Execution",
        "order": 22
    },
    "invoice_format": {
        "description": "Invoice format and delivery method",
        "process_question": "What format are invoices - EDI 810, PDF, email?",
        "examples": ["EDI 810 for large customers", "PDF emailed", "Paper mailed"],
        "class": "Revenue Realization & Invoicing",
        "subclass": "Billing Execution",
        "order": 23
    },
    "landed_cost_calculation": {
        "description": "How freight/landed costs are calculated",
        "process_question": "How are freight and landed costs calculated and added to invoices?",
        "examples": ["Automated via TM", "Manual freight log spreadsheet", "Not included"],
        "class": "Revenue Realization & Invoicing",
        "subclass": "Billing Execution",
        "order": 24
    },
    
    # Revenue Accounting
    "revenue_recognition_event": {
        "description": "When revenue is recognized",
        "process_question": "When is revenue recognized - on shipment, delivery, or invoice?",
        "examples": ["On shipment", "On delivery", "On invoice"],
        "class": "Revenue Realization & Invoicing",
        "subclass": "Revenue Accounting",
        "order": 25
    },
    "tax_jurisdiction_vat_code": {
        "description": "How tax is determined",
        "process_question": "How is tax/VAT determined for orders?",
        "examples": ["Based on ship-to address", "Tax engine integration", "Manual"],
        "class": "Revenue Realization & Invoicing",
        "subclass": "Revenue Accounting",
        "order": 26
    },
    "gl_account_mapping": {
        "description": "How GL accounts are assigned",
        "process_question": "How are GL accounts mapped for revenue?",
        "examples": ["Product category-based", "Standard mapping", "Manual assignment"],
        "class": "Revenue Realization & Invoicing",
        "subclass": "Revenue Accounting",
        "order": 27
    },
    
    # Financial Settlements - Cash Application
    "remittance_method": {
        "description": "How customers pay",
        "process_question": "How do customers pay? What are the remittance methods?",
        "examples": ["60% lockbox/check", "30% ACH", "10% credit card"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Cash Application",
        "order": 28
    },
    "auto_match_rate": {
        "description": "How payments are matched to invoices",
        "process_question": "How are payments matched to invoices? Automated or manual?",
        "examples": ["70% auto-matched by invoice number", "AI/ML matching", "All manual"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Cash Application",
        "order": 29
    },
    "unapplied_cash_balance": {
        "description": "How unapplied payments are handled",
        "process_question": "How do you handle payments that can't be matched? Unapplied cash?",
        "examples": ["Research queue", "2-3 hours daily manual work", "Minimal unapplied"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Cash Application",
        "order": 30
    },
    
    # Dispute & Deduction Management
    "dispute_reason_code": {
        "description": "Common dispute/deduction reasons",
        "process_question": "What are the common reasons for disputes or deductions?",
        "examples": ["Pricing disputes", "Damaged goods", "Short-ship", "Promo deductions"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Dispute & Deduction Management",
        "order": 31,
        "optional": True
    },
    "case_owner": {
        "description": "Who handles disputes",
        "process_question": "Who owns the dispute resolution process?",
        "examples": ["Sales rep contacts customer", "Collections specialist", "Finance team"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Dispute & Deduction Management",
        "order": 32,
        "optional": True
    },
    "tracking_repository": {
        "description": "Where disputes are tracked",
        "process_question": "How are disputes tracked? ERP, Excel, email?",
        "examples": ["ERP case management", "Excel tracker", "Mix of emails"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Dispute & Deduction Management",
        "order": 33,
        "optional": True
    },
    
    # Collections & Dunning
    "ar_aging_bucket": {
        "description": "How AR aging is managed",
        "process_question": "How do you manage AR aging? What buckets do you use?",
        "examples": ["Current, 30, 60, 90+ days", "Weekly aging report", "Real-time dashboard"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Collections & Dunning",
        "order": 34
    },
    "dunning_level": {
        "description": "How dunning/collection process works",
        "process_question": "What's your dunning process for overdue accounts?",
        "examples": ["Automated dunning letters", "Collector call scripts", "Manual outreach"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Collections & Dunning",
        "order": 35
    },
    "bad_debt_provision_status": {
        "description": "How bad debt is managed",
        "process_question": "How is bad debt provisioned and written off?",
        "examples": ["Quarterly review", "Trigger at 120 days", "Case-by-case"],
        "class": "Financial Settlements & Recovery",
        "subclass": "Collections & Dunning",
        "order": 36
    },
    
    # Master Data - Customer Master
    "legal_entity_name": {
        "description": "How customer master is structured",
        "process_question": "How is customer master data structured - by legal entity?",
        "examples": ["Legal entity with ship-to hierarchy", "Single account", "Complex hierarchy"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Customer Master & Onboarding",
        "order": 37
    },
    "tax_id": {
        "description": "How tax IDs are managed",
        "process_question": "How are customer tax IDs captured and validated?",
        "examples": ["Required at setup", "W-9 process", "Not validated"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Customer Master & Onboarding",
        "order": 38
    },
    "payment_terms": {
        "description": "How payment terms are set",
        "process_question": "How are payment terms established for customers?",
        "examples": ["Standard Net 30", "Negotiated by sales", "Credit-based"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Customer Master & Onboarding",
        "order": 39
    },
    "credit_threshold": {
        "description": "How credit limits are established",
        "process_question": "How are credit limits established for new customers?",
        "examples": ["Credit application process", "D&B-based", "Sales discretion"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Customer Master & Onboarding",
        "order": 40
    },
    "setup_workflow_status": {
        "description": "Customer onboarding workflow",
        "process_question": "What's the customer onboarding/setup workflow?",
        "examples": ["Formal workflow with approvals", "Sales enters directly", "Paper forms"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Customer Master & Onboarding",
        "order": 41
    },
    
    # Reverse Logistics
    "return_authorization_number": {
        "description": "How RMAs are handled",
        "process_question": "How are returns authorized? RMA process?",
        "examples": ["Formal RMA required", "Sales approves", "No formal process"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Reverse Logistics",
        "order": 42,
        "optional": True
    },
    "inspection_result": {
        "description": "How returned items are inspected",
        "process_question": "How are returned items inspected and dispositioned?",
        "examples": ["Warehouse inspects", "Automatic restock", "Destroy on receipt"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Reverse Logistics",
        "order": 43,
        "optional": True
    },
    "restocking_fee_logic": {
        "description": "Restocking fee policies",
        "process_question": "Are there restocking fees? How are they applied?",
        "examples": ["15% restocking fee", "No fees", "Customer-specific"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Reverse Logistics",
        "order": 44,
        "optional": True
    },
    "credit_memo_status": {
        "description": "How credit memos are issued",
        "process_question": "How are credit memos issued for returns?",
        "examples": ["Auto on inspection", "Manual approval", "AR issues"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Reverse Logistics",
        "order": 45,
        "optional": True
    },
    
    # Reporting & Audit
    "kpis": {
        "description": "Key metrics tracked",
        "process_question": "What KPIs do you track for O2C? DSO, cycle time?",
        "examples": ["DSO, Order Cycle Time, Invoice Accuracy", "Cash Application Accuracy"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Reporting & Audit Controls",
        "order": 46
    },
    "sod_flags": {
        "description": "Segregation of duties controls",
        "process_question": "How do you manage segregation of duties?",
        "examples": ["ERP roles enforced", "Manual review", "Audit flags"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Reporting & Audit Controls",
        "order": 47
    },
    "sub_ledger_reconciliation_status": {
        "description": "How sub-ledger reconciliation works",
        "process_question": "How do you reconcile sub-ledger to GL?",
        "examples": ["Daily automated", "Monthly manual", "Separate sources compiled"],
        "class": "Master Data & Lifecycle Support",
        "subclass": "Reporting & Audit Controls",
        "order": 48
    }
}

def get_missing_attributes(collected_data):
    """Returns list of attributes not yet captured, in flow order."""
    missing = []
    for attr_name, attr_info in REQUIRED_ATTRIBUTES.items():
        if attr_info.get("optional", False):
            continue
        if attr_name not in collected_data or collected_data[attr_name] is None:
            missing.append((attr_name, attr_info.get("order", 999)))
    missing.sort(key=lambda x: x[1])
    return [name for name, _ in missing]

def get_missing_by_subclass(collected_data):
    """Returns missing attributes grouped by subclass in flow order."""
    missing = {}
    for attr_name, attr_info in REQUIRED_ATTRIBUTES.items():
        if attr_info.get("optional", False):
            continue
        if attr_name not in collected_data or collected_data[attr_name] is None:
            key = (attr_info["class"], attr_info["subclass"])
            if key not in missing:
                missing[key] = []
            missing[key].append((attr_name, attr_info.get("order", 999)))
    
    for key in missing:
        missing[key].sort(key=lambda x: x[1])
        missing[key] = [name for name, _ in missing[key]]
    
    result = []
    for class_subclass in SUBCLASS_FLOW_ORDER:
        if class_subclass in missing:
            result.append({
                "class": class_subclass[0],
                "subclass": class_subclass[1],
                "attributes": missing[class_subclass]
            })
    return result

def get_attribute_info(attr_name):
    return REQUIRED_ATTRIBUTES.get(attr_name, {})

def is_complete(collected_data):
    return len(get_missing_attributes(collected_data)) == 0

def get_current_focus_area(collected_data):
    missing_by_subclass = get_missing_by_subclass(collected_data)
    return missing_by_subclass[0] if missing_by_subclass else None
