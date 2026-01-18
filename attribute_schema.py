"""
Hierarchical Order Management Checklist Schema

Attributes are structured as:
- (M) Mandatory: Directly asked to user
- (I) Inferred: Derived internally from previous answers

Conditional flow ensures questions are asked in order,
skipping conditional ones if their trigger condition is not met.
"""

# Question flow order - each entry has:
# - id: Question identifier (matches checklist numbering)
# - key: Attribute key to store the answer
# - question: The actual question to ask
# - type: "M" (mandatory) or "I" (inferred)
# - condition: Function name to check if question should be asked (None = always)
# - inference_from: For type "I", which key to infer from

QUESTION_FLOW = [
    {
        "id": "1",
        "key": "order_origin_channels",
        "question": "How does an order originate? What channels do orders come through?",
        "type": "M",
        "condition": None,
        "examples": ["EDI from retailers", "B2B Portal", "Manual entry from email/PDF", "Phone orders"]
    },
    {
        "id": "1.1",
        "key": "has_manual_intake",
        "question": None,  # Inferred, not asked
        "type": "I",
        "inference_from": "order_origin_channels",
        "inference_logic": "infer_has_manual"
    },
    {
        "id": "1.1.1",
        "key": "manual_intake_method",
        "question": "You mentioned manual order intake. How do you receive these orders - by Emails, Digital Documents (PDF), or Physical Documents?",
        "type": "M",
        "condition": "has_manual_intake_yes",
        "examples": ["Email with attached PO", "Scanned PDFs", "Faxed orders", "Physical mail"]
    },
    {
        "id": "2",
        "key": "order_receiver",
        "question": "Who receives the order? Which team or role handles incoming orders?",
        "type": "M",
        "condition": None,
        "examples": ["Sales team", "Customer service", "Order desk", "Shared inbox"]
    },
    {
        "id": "3",
        "key": "captured_data_fields",
        "question": "What data do you capture when an order comes in?",
        "type": "M",
        "condition": None,
        "examples": ["Customer ID, SKU, Quantity, Price", "Ship-to address, PO number", "Requested delivery date"]
    },
    {
        "id": "4",
        "key": "primary_order_system",
        "question": "What is the primary system where the sales order is formally created and recorded?",
        "type": "M",
        "condition": None,
        "examples": ["SAP", "Oracle EBS", "NetSuite", "Custom ERP", "Spreadsheets"]
    },
    {
        "id": "4.1",
        "key": "uses_erp",
        "question": None,  # Inferred
        "type": "I",
        "inference_from": "primary_order_system",
        "inference_logic": "infer_uses_erp"
    },
    {
        "id": "5",
        "key": "manual_data_verification",
        "question": "For manual orders, how do you verify that all necessary data is captured? Do you use a Form or Checklist?",
        "type": "M",
        "condition": "has_manual_intake_yes",
        "examples": ["Required field checklist in ERP", "Paper form", "No formal verification"]
    },
    {
        "id": "6",
        "key": "automated_data_capture",
        "question": "For portal or EDI orders, does the system capture all necessary data before creating an order entry?",
        "type": "M",
        "condition": "has_automated_channel",
        "examples": ["Yes, all fields required", "Partial - some fields optional", "No validation"]
    },
    {
        "id": "7",
        "key": "required_verification_fields",
        "question": "What are all the necessary data fields that need to be verified before creating an order entry?",
        "type": "M",
        "condition": None,
        "examples": ["Customer ID, SKU validity, Quantity, Price, Ship-to address", "Credit status", "PO number"]
    },
    {
        "id": "8",
        "key": "verification_success_rate",
        "question": "How successfully does this data verification happen? What percentage of orders pass on first try?",
        "type": "M",
        "condition": None,
        "examples": ["90% pass first time", "Variable - depends on channel", "Often need to follow up"]
    },
    {
        "id": "9",
        "key": "verification_owner",
        "question": "Who is responsible for this data verification step?",
        "type": "M",
        "condition": None,
        "examples": ["Sales rep who entered", "Order desk team", "System auto-validates", "Quality team"]
    },
    {
        "id": "10",
        "key": "credit_approval_type",
        "question": "What kind of credit approval mechanism do you have?",
        "type": "M",
        "condition": None,
        "examples": ["Auto-approval under threshold", "Manual review for all", "Combination of both"]
    },
    {
        "id": "10.1",
        "key": "has_auto_approval",
        "question": None,  # Inferred
        "type": "I",
        "inference_from": "credit_approval_type",
        "inference_logic": "infer_has_auto_approval"
    },
    {
        "id": "10.1.1",
        "key": "auto_approval_limit",
        "question": "What is the credit amount threshold for auto-approval?",
        "type": "M",
        "condition": "has_auto_approval_yes",
        "examples": ["$50,000", "$10,000", "Depends on customer credit rating"]
    },
    {
        "id": "10.2",
        "key": "has_manual_credit",
        "question": None,  # Inferred
        "type": "I",
        "inference_from": "credit_approval_type",
        "inference_logic": "infer_has_manual_credit"
    },
    {
        "id": "10.2.1",
        "key": "manual_credit_approver",
        "question": "Who does the manual credit approval?",
        "type": "M",
        "condition": "has_manual_credit_yes",
        "examples": ["Credit analyst", "Finance manager", "AR team", "Sales manager"]
    },
    {
        "id": "10.2.2",
        "key": "credit_decision_factors",
        "question": "What data points are looked at to make the credit decision?",
        "type": "M",
        "condition": "has_manual_credit_yes",
        "examples": ["AR balance", "Payment history", "D&B rating", "Open orders value"]
    },
    {
        "id": "10.2.3",
        "key": "credit_decision_to_sales",
        "question": "How is the final credit decision conveyed to the sales rep?",
        "type": "M",
        "condition": "has_manual_credit_and_manual_channel",
        "examples": ["Email notification", "ERP status update", "Phone call", "Dashboard alert"]
    },
    {
        "id": "10.2.4",
        "key": "credit_decision_to_customer",
        "question": "How is the final credit decision conveyed to the customer?",
        "type": "M",
        "condition": "has_manual_credit_yes",
        "examples": ["Sales rep informs", "Automated email", "Order confirmation shows status"]
    },
]

# Build attribute schema from flow
REQUIRED_ATTRIBUTES = {}
for q in QUESTION_FLOW:
    REQUIRED_ATTRIBUTES[q["key"]] = {
        "id": q["id"],
        "question": q.get("question"),
        "type": q["type"],
        "condition": q.get("condition"),
        "examples": q.get("examples", []),
        "inference_from": q.get("inference_from"),
        "inference_logic": q.get("inference_logic"),
    }


# ============ INFERENCE FUNCTIONS ============

def infer_has_manual(channels_value):
    """Infer if manual intake exists from order_origin_channels."""
    if not channels_value:
        return None
    lower = channels_value.lower()
    manual_keywords = ["manual", "email", "pdf", "phone", "fax", "physical", "paper", "mail", "scan"]
    return "Yes" if any(kw in lower for kw in manual_keywords) else "No"


def infer_uses_erp(system_value):
    """Infer if client uses ERP from primary_order_system."""
    if not system_value:
        return None
    lower = system_value.lower()
    erp_keywords = ["erp", "sap", "oracle", "netsuite", "dynamics", "jd edwards", "infor", "epicor", "sage"]
    return "ERP" if any(kw in lower for kw in erp_keywords) else "Non-ERP"


def infer_has_auto_approval(credit_type_value):
    """Infer if auto-approval exists from credit_approval_type."""
    if not credit_type_value:
        return None
    lower = credit_type_value.lower()
    auto_keywords = ["auto", "automatic", "threshold", "under $", "below"]
    return "Yes" if any(kw in lower for kw in auto_keywords) else "No"


def infer_has_manual_credit(credit_type_value):
    """Infer if manual credit approval exists from credit_approval_type."""
    if not credit_type_value:
        return None
    lower = credit_type_value.lower()
    manual_keywords = ["manual", "analyst", "review", "approve", "manager", "above", "over $"]
    # Also check if it's not purely auto
    if "only auto" in lower or "all auto" in lower:
        return "No"
    return "Yes" if any(kw in lower for kw in manual_keywords) else "No"


INFERENCE_FUNCTIONS = {
    "infer_has_manual": infer_has_manual,
    "infer_uses_erp": infer_uses_erp,
    "infer_has_auto_approval": infer_has_auto_approval,
    "infer_has_manual_credit": infer_has_manual_credit,
}


# ============ CONDITION FUNCTIONS ============

def check_condition(condition_name, collected_data):
    """Check if a condition is met based on collected data."""
    if condition_name is None:
        return True
    
    if condition_name == "has_manual_intake_yes":
        return collected_data.get("has_manual_intake") == "Yes"
    
    if condition_name == "has_automated_channel":
        channels = collected_data.get("order_origin_channels", "").lower()
        return "edi" in channels or "portal" in channels or "b2b" in channels
    
    if condition_name == "has_auto_approval_yes":
        return collected_data.get("has_auto_approval") == "Yes"
    
    if condition_name == "has_manual_credit_yes":
        return collected_data.get("has_manual_credit") == "Yes"
    
    if condition_name == "has_manual_credit_and_manual_channel":
        has_manual_credit = collected_data.get("has_manual_credit") == "Yes"
        has_manual_channel = collected_data.get("has_manual_intake") == "Yes"
        return has_manual_credit and has_manual_channel
    
    return True


# ============ FLOW HELPER FUNCTIONS ============

def run_inferences(collected_data):
    """Run all applicable inferences based on collected data."""
    for q in QUESTION_FLOW:
        if q["type"] == "I" and q.get("inference_from"):
            source_key = q["inference_from"]
            if source_key in collected_data and q["key"] not in collected_data:
                inference_func = INFERENCE_FUNCTIONS.get(q.get("inference_logic"))
                if inference_func:
                    inferred_value = inference_func(collected_data[source_key])
                    if inferred_value:
                        collected_data[q["key"]] = inferred_value
    return collected_data


def get_next_question_info(collected_data):
    """Get the next question to ask based on collected data and conditions."""
    # First, run inferences
    collected_data = run_inferences(collected_data)
    
    # Find first unanswered mandatory question that meets its condition
    for q in QUESTION_FLOW:
        if q["type"] != "M":
            continue  # Skip inferred questions
        
        if q["key"] in collected_data:
            continue  # Already answered
        
        if not check_condition(q.get("condition"), collected_data):
            continue  # Condition not met, skip
        
        return {
            "id": q["id"],
            "key": q["key"],
            "question": q["question"],
            "examples": q.get("examples", [])
        }
    
    return None  # All questions answered


def get_missing_attributes(collected_data):
    """Get list of mandatory attributes not yet collected (that meet conditions)."""
    collected_data = run_inferences(collected_data)
    missing = []
    
    for q in QUESTION_FLOW:
        if q["type"] != "M":
            continue
        if q["key"] in collected_data:
            continue
        if not check_condition(q.get("condition"), collected_data):
            continue
        missing.append(q["key"])
    
    return missing


def get_all_attribute_keys():
    """Get all attribute keys in order."""
    return [q["key"] for q in QUESTION_FLOW]


def is_complete(collected_data):
    """Check if all required questions are answered."""
    return len(get_missing_attributes(collected_data)) == 0


def get_progress(collected_data):
    """Get progress as (answered, total_applicable)."""
    collected_data = run_inferences(collected_data)
    
    total = 0
    answered = 0
    
    for q in QUESTION_FLOW:
        if q["type"] != "M":
            continue
        if not check_condition(q.get("condition"), collected_data):
            continue
        total += 1
        if q["key"] in collected_data:
            answered += 1
    
    return answered, total
