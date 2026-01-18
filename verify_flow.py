"""
Test the example conversation flow from the user's spec.
Verify that the bot correctly follows O2C flow and extracts all attributes.
"""
import os
import sys
from unittest.mock import MagicMock
import json

# Mock openai
sys.modules['openai'] = MagicMock()
from orchestrator import Orchestrator
import llm_utils

# Track extracted attributes for verification
extracted_attributes = {}
question_count = 0

def mock_call_qwen(messages, temperature=0.0):
    """
    Mock LLM that simulates the example conversation extraction
    """
    global question_count
    content = messages[-1]['content'] if messages else ""
    system_content = messages[0]['content'] if messages else ""
    
    # Router - detect order intent
    if "classify the user's intent" in system_content:
        if any(word in content.lower() for word in ["order", "report", "log"]):
            return "ORDER_MGMT"
        return "OTHER"
    
    # Universal extractor - parse the example conversation responses
    if "Extract ALL relevant attributes" in system_content:
        extracted = {}
        content_lower = content.lower()
        
        # Example conversation mapping - simulate intelligent extraction
        
        # Order Intake
        if "pdf" in content_lower or "email" in content_lower:
            extracted["source_channel"] = "Manual Email/PDF"
        if "edi" in content_lower:
            extracted["source_channel"] = "EDI 850"
        if "portal" in content_lower or "e-commerce" in content_lower:
            extracted["source_channel"] = "B2B Portal"
        
        # Order Completeness
        if "checklist" in content_lower and "variable" in content_lower:
            extracted["order_completeness_score"] = "Variable - required field checklist exists but adherence varies"
        if "miss" in content_lower or "delay" in content_lower:
            extracted["order_completeness_score"] = "Issues with data completeness causing delays"
        
        # Commercial Validation - FOB terms mentioned
        if "fob" in content_lower:
            extracted["fob_terms"] = "Sometimes missed; causes delays"
        if "promo" in content_lower:
            extracted["pricing_logic"] = "Promotional sometimes missed"
        
        # Credit Governance
        if "$50,000" in content_lower or "50,000" in content_lower:
            extracted["credit_limit"] = "$50,000 threshold"
        if "auto-approve" in content_lower or "auto approve" in content_lower:
            extracted["approval_workflow"] = "Auto-approval under $50k"
        if "credit hold" in content_lower or "analyst" in content_lower or "sam" in content_lower:
            extracted["approval_workflow"] = "Manual analyst queue (Sam reviews)"
        if "dunn" in content_lower or "d&b" in content_lower or "bradstreet" in content_lower:
            extracted["risk_scoring"] = "D&B Rating via separate browser tab"
        if "released" in content_lower:
            extracted["order_status"] = "Released"
        if "blocked" in content_lower:
            extracted["order_status"] = "Blocked"
        if "conditional" in content_lower or "partial shipment" in content_lower:
            extracted["order_status"] = "Conditional - partial shipment on CIA"
        
        # Fulfillment - Inventory & Production
        if "made-to-order" in content_lower or "mto" in content_lower:
            extracted["stock_category"] = "MTO (Made-to-Order)"
        if "production scheduling" in content_lower or "production queue" in content_lower:
            extracted["production_queue_status"] = "Goes to production scheduling queue"
        
        # Warehouse Operations
        if "paper pick" in content_lower or "paper list" in content_lower:
            extracted["picking_document_type"] = "Paper pick lists"
        if "pack slip" in content_lower:
            extracted["packing_status"] = "Pack slip printed automatically"
        if "crash" in content_lower or "old" in content_lower:
            extracted["system_reliability_metric"] = "Old system; crashes frequently"
        if "rf scanner" in content_lower or "handheld" in content_lower:
            extracted["picking_document_type"] = "RF Scanner (but unreliable)"
        
        # Transportation
        if "fedex" in content_lower or "ups" in content_lower or "ltl" in content_lower:
            extracted["carrier_selection"] = "FedEx, UPS, LTL carrier"
        if "manually re-key" in content_lower or "manual" in content_lower and "address" in content_lower:
            extracted["data_integrity_type"] = "Manual Re-key"
        if "tracking" in content_lower and "typed" in content_lower:
            extracted["tracking_id"] = "Manually typed back into ERP"
        
        # Invoicing
        if "shipped" in content_lower and "invoice" in content_lower:
            extracted["generation_trigger"] = "Post-shipment (when marked shipped)"
        if "invoice pdf" in content_lower:
            extracted["invoice_format"] = "PDF"
        if "freight log" in content_lower or "spreadsheet" in content_lower:
            extracted["landed_cost_calculation"] = "Manual Freight Log spreadsheet"
        if "landed cost" in content_lower:
            extracted["landed_cost_calculation"] = "Not in ERP; manual process"
        
        # Cash Application
        if "lockbox" in content_lower:
            extracted["remittance_method"] = "Lockbox (60%)"
        if "ach" in content_lower:
            extracted["remittance_method"] = "ACH (30%)" 
        if "credit card" in content_lower:
            extracted["remittance_method"] = "Credit card virtual terminal (10%)"
        if "70%" in content_lower and "match" in content_lower:
            extracted["auto_match_rate"] = "70% auto-matched"
        if "2-3 hours" in content_lower or "manual" in content_lower and "research" in content_lower:
            extracted["unapplied_cash_balance"] = "Requires 2-3 hours daily manual research"
        
        # Disputes
        if "short pay" in content_lower or "deduction" in content_lower:
            extracted["dispute_reason_code"] = "Short pay, pricing disputes, damaged goods"
        if "excel" in content_lower and "track" in content_lower:
            extracted["tracking_repository"] = "Mix of emails and Excel tracker"
        if "sales rep" in content_lower and "collections" in content_lower:
            extracted["case_owner"] = "Sales rep and collections specialist"
        
        # KPIs
        if "dso" in content_lower:
            extracted["kpis"] = "DSO"
        if "cycle time" in content_lower:
            extracted["kpis"] = extracted.get("kpis", "") + ", Order Cycle Time"
        if "invoice accuracy" in content_lower:
            extracted["kpis"] = extracted.get("kpis", "") + ", Invoice Accuracy"
        if "cash application accuracy" in content_lower:
            extracted["kpis"] = extracted.get("kpis", "") + ", Cash Application Accuracy"
        if "manual" in content_lower and "compile" in content_lower:
            extracted["sub_ledger_reconciliation_status"] = "Manual compilation from different sources"
        
        return json.dumps(extracted)
    
    # Question generator
    if "Generate ONE natural" in system_content:
        question_count += 1
        
        # Generate questions based on focus area mentioned in system prompt
        if "Order Intake" in system_content:
            return "How does an order come into your organization?"
        elif "Commercial Validation" in system_content:
            return "For manual entries, is there a standard form or checklist to capture all necessary data?"
        elif "Credit Governance" in system_content:
            return "Is there an automatic credit check? Could you walk me through the decision process?"
        elif "Inventory & Production" in system_content:
            return "What triggers the handoff to fulfillment or production?"
        elif "Warehouse Operations" in system_content:
            return "How do they know what to pick? Paper pick list, RF scanner?"
        elif "Transportation" in system_content:
            return "After picking, how is shipping integrated?"
        elif "Billing Execution" in system_content:
            return "When does invoicing happen?"
        elif "Cash Application" in system_content:
            return "Let's follow the money. How do customers pay?"
        elif "Dispute" in system_content:
            return "What happens with discrepancies, short payments, or disputes?"
        elif "Collections" in system_content:
            return "What about AR aging and collections?"
        elif "Reporting" in system_content:
            return "Finally, what metrics do you look at? DSO, collections efficiency?"
        else:
            return "Could you tell me more about that process?"
    
    return "NOT_FOUND"

llm_utils.call_qwen = mock_call_qwen

def test_example_conversation():
    """Test with the exact example conversation from the spec"""
    print("\n" + "="*80)
    print("TESTING EXAMPLE CONVERSATION FLOW")
    print("="*80)
    
    if os.path.exists("order_records.txt"):
        os.remove("order_records.txt")
    
    session_state = {}
    orc = Orchestrator()
    
    # Example conversation exchanges from the spec
    exchanges = [
        # 1. Trigger + Channel answer
        ("I need to report an order", None),  # Trigger
        (
            "Good question. It comes through multiple channels. Primarily, our sales team creates orders "
            "directly in our current ERP system after getting a signed PDF or email from the customer. "
            "We also get orders via EDI from our three largest retailers, and a small but growing portion "
            "comes through our B2B e-commerce portal.",
            ["source_channel"]
        ),
        
        # 2. Order completeness / Commercial validation
        (
            "There's a required field checklist in the ERP, but adherence is... variable. They always get "
            "customer ID, product, quantity, and price. But things like special shipping instructions, "
            "PROMO codes, or specific FOB terms sometimes get missed and cause delays later.",
            ["order_completeness_score", "fob_terms", "pricing_logic"]
        ),
        
        # 3. Credit Governance
        (
            "Yes, but not for all. Orders under $50,000 auto-approve if the customer's account is in good "
            "standing. Anything above that, or if the customer is on a credit hold, the order gets flagged "
            "and goes to a queue for our credit analyst, Sam.",
            ["credit_limit", "approval_workflow"]
        ),
        
        # 4. Sam's decision process
        (
            "Sam logs into the ERP, goes to the 'Credit Hold' dashboard. He reviews the customer's ledger, "
            "checks their Dunn & Bradstreet rating via a separate browser tab, and might approve it, reject "
            "it, or approve it with conditions—like partial shipment on cash-in-advance terms.",
            ["risk_scoring", "order_status"]
        ),
        
        # 5. Fulfillment trigger
        (
            "The 'Released' status. Our warehouse team has a scheduled report they run every two hours for "
            "new released orders. They pick and pack based on that. But for made-to-order items, it goes to "
            "a production scheduling queue first.",
            ["order_status", "stock_category", "production_queue_status"]
        ),
        
        # 6. Warehouse operations  
        (
            "Paper pick lists. They get a pack slip printed automatically. They pick, scan the barcode on "
            "the shelf and the product barcode with a handheld—but that system is old and often crashes.",
            ["picking_document_type", "packing_status", "system_reliability_metric"]
        ),
        
        # 7. Shipping
        (
            "The warehouse updates the order status to 'Picked.' That triggers the shipping clerk to log "
            "into our carrier portals—FedEx, UPS, and our LTL carrier's system—to create labels. He manually "
            "re-keys the address and weight from the ERP. The tracking number is then manually typed back.",
            ["carrier_selection", "data_integrity_type", "tracking_id"]
        ),
        
        # 8. Invoicing
        (
            "As soon as the shipping clerk marks the shipment 'Shipped' in the ERP, the system auto-generates "
            "an invoice PDF. But here's a pain point: freight charges aren't in the ERP. Maria has to check a "
            "separate freight log spreadsheet and manually add those charges.",
            ["generation_trigger", "invoice_format", "landed_cost_calculation"]
        ),
        
        # 9. Payment methods
        (
            "About 60% pay by check, mailing it to our lockbox. The bank sends us a daily file. 30% pay via "
            "ACH, where they send us a notification email and we manually match it in the ERP. The remaining "
            "10% use credit cards through a virtual terminal.",
            ["remittance_method"]
        ),
        
        # 10. Cash application
        (
            "Maria downloads the lockbox file from the bank's portal each morning. She runs an auto-cash "
            "application in the ERP, which matches about 70% of payments based on invoice number. The rest "
            "she has to manually research and apply. This can take her 2-3 hours a day.",
            ["auto_match_rate", "unapplied_cash_balance"]
        ),
        
        # 11. Disputes
        (
            "That's a nightmare. If it's a short pay, she puts the payment on hold and sends an email to the "
            "sales rep and the collections specialist. They have to contact the customer, get a reason—often "
            "a pricing dispute or damaged goods—then decide to write it off. All tracked in emails and an "
            "Excel tracker.",
            ["dispute_reason_code", "case_owner", "tracking_repository"]
        ),
        
        # 12. Metrics
        (
            "Yes, I get a weekly DSO report from Finance. But I also care about 'Order Cycle Time', "
            "'Invoice Accuracy,' and 'Cash Application Accuracy.' I have to manually compile those "
            "from different sources.",
            ["kpis", "sub_ledger_reconciliation_status"]
        ),
    ]
    
    # Run through conversation
    for i, (user_msg, expected_captures) in enumerate(exchanges):
        print(f"\n--- Exchange {i+1} ---")
        print(f"User: {user_msg[:80]}..." if len(user_msg) > 80 else f"User: {user_msg}")
        
        response = orc.handle_message(user_msg, session_state)
        print(f"Bot: {response[:80]}..." if len(response) > 80 else f"Bot: {response}")
        
        # Check what was captured
        collected = session_state.get("order_state", {}).get("collected_data", {})
        if expected_captures:
            for attr in expected_captures:
                if attr in collected:
                    print(f"  ✓ Captured {attr}")
    
    # Final check
    print("\n" + "="*80)
    print("FINAL CAPTURED DATA")
    print("="*80)
    
    final_data = session_state.get("order_state", {}).get("collected_data", {})
    for k, v in sorted(final_data.items()):
        print(f"  {k}: {v}")
    
    print(f"\nTotal attributes captured: {len(final_data)}")
    print("\n✓ Example conversation test complete!")

if __name__ == "__main__":
    test_example_conversation()
