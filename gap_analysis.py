"""
GAP Analysis Module

Compares captured As-Is process against SAP best practices.
Generates:
1. Color-coded Mermaid diagram showing gaps
2. Summary text explaining gaps and recommendations
"""

from sap_standard import SAP_BEST_PRACTICES


def analyze_gaps(collected_data):
    """
    Analyze gaps between captured data and SAP best practices.
    
    Score = % of required attributes captured AND aligned.
    Missing attributes count as gaps.
    """
    if not collected_data:
        return {"gaps": [], "strengths": [], "score": 0, "missing": list(SAP_BEST_PRACTICES.keys())}
    
    gaps = []
    strengths = []
    missing = []
    
    # Check ALL attributes in best practices (not just collected ones)
    for attr_key, best_practice in SAP_BEST_PRACTICES.items():
        if attr_key not in collected_data:
            # Missing attribute = gap
            missing.append({
                "attribute": attr_key,
                "standard": best_practice["standard"],
                "risk": best_practice["risk_if_missing"],
                "issue": "Not yet captured"
            })
            continue
        
        current_value = collected_data[attr_key]
        std = best_practice["standard"].lower()
        current = str(current_value).lower()
        
        # Analyze alignment
        gap_info = {
            "attribute": attr_key,
            "current": current_value,
            "standard": best_practice["standard"],
            "risk": best_practice["risk_if_missing"]
        }
        
        # Gap detection heuristics
        is_gap = False
        
        # Check for manual/paper processes
        if any(word in current for word in ["manual", "paper", "email", "spreadsheet", "excel"]):
            if "automated" in std or "system" in std or "real-time" in std:
                is_gap = True
                gap_info["issue"] = "Manual process vs automated standard"
        
        # Check for low success rates
        if attr_key == "verification_success_rate":
            try:
                rate = int(''.join(filter(str.isdigit, current[:3])))
                if rate < 90:
                    is_gap = True
                    gap_info["issue"] = f"Success rate {rate}% below 95% target"
            except:
                pass
        
        # Check for missing integration
        if any(word in current for word in ["separate", "different system", "re-key", "manual entry"]):
            is_gap = True
            gap_info["issue"] = "System fragmentation vs integrated approach"
        
        # Check credit governance
        if attr_key in ["credit_decision_to_sales", "credit_decision_to_customer"]:
            if any(word in current for word in ["phone", "calls", "email"]):
                if "automated" in std or "dashboard" in std:
                    is_gap = True
                    gap_info["issue"] = "Manual notification vs automated alerts"
        
        if is_gap:
            gaps.append(gap_info)
        else:
            strengths.append({
                "attribute": attr_key,
                "current": current_value,
                "aligned": True
            })
    
    # Calculate alignment score: strengths / total required attributes
    total_required = len(SAP_BEST_PRACTICES)
    score = int((len(strengths) / total_required * 100)) if total_required > 0 else 0
    
    return {
        "gaps": gaps,
        "strengths": strengths,
        "missing": missing,
        "score": score,
        "captured_count": len(strengths) + len(gaps),
        "total_required": total_required
    }


def generate_gap_diagram(collected_data, gap_analysis):
    """
    Generate a color-coded Mermaid diagram showing gaps.
    
    - Green (:::green): Aligned with best practice
    - Red (:::red): Gap identified
    - Yellow (:::yellow): Partial alignment
    """
    
    gaps_set = {g["attribute"] for g in gap_analysis.get("gaps", [])}
    
    diagram = '''graph TD
    %% GAP Analysis: Color-coded
    %% Green = Aligned, Red = Gap, Yellow = Partial
    
    classDef green fill:#28a745,stroke:#1e7e34,color:#fff
    classDef red fill:#dc3545,stroke:#c82333,color:#fff
    classDef yellow fill:#ffc107,stroke:#d39e00,color:#000
    classDef default fill:#6c757d,stroke:#545b62,color:#fff
    
    Start((Order Received)) --> IntakeChannel
'''
    
    # Order Intake section
    has_channels = "order_origin_channels" in collected_data
    channel_class = "red" if "order_origin_channels" in gaps_set else ("green" if has_channels else "default")
    diagram += f'    IntakeChannel{{{{"Channel Type"}}}}:::{channel_class}\n'
    
    if collected_data.get("has_manual_intake") == "Yes":
        manual_class = "red" if "manual_intake_method" in gaps_set else "green"
        diagram += f'    IntakeChannel --> ManualIntake["Manual: {collected_data.get("manual_intake_method", "Email/PDF")[:20]}"]:::{manual_class}\n'
    
    has_auto = "portal" in str(collected_data.get("order_origin_channels", "")).lower() or \
               "edi" in str(collected_data.get("order_origin_channels", "")).lower()
    if has_auto:
        auto_class = "green"
        diagram += f'    IntakeChannel --> AutoIntake["Portal/EDI"]:::{auto_class}\n'
        diagram += '    ManualIntake --> OrderCreated\n' if collected_data.get("has_manual_intake") == "Yes" else ''
        diagram += '    AutoIntake --> OrderCreated\n'
    else:
        diagram += '    ManualIntake --> OrderCreated\n' if collected_data.get("has_manual_intake") == "Yes" else '    IntakeChannel --> OrderCreated\n'
    
    # System
    system_class = "green" if collected_data.get("uses_erp") == "ERP" else "yellow"
    system_name = collected_data.get("primary_order_system", "System")[:15]
    diagram += f'    OrderCreated["{system_name}"]:::{system_class}\n'
    
    # Verification
    verify_class = "red" if "verification_success_rate" in gaps_set else "green"
    verify_rate = collected_data.get("verification_success_rate", "Unknown")
    diagram += f'    OrderCreated --> Verification{{{{"Data Verification"}}}}:::{verify_class}\n'
    
    # Credit
    credit_class = "green" if collected_data.get("has_auto_approval") == "Yes" else "yellow"
    diagram += f'    Verification --> CreditCheck{{{{"Credit Check"}}}}:::{credit_class}\n'
    
    if collected_data.get("has_auto_approval") == "Yes":
        limit = collected_data.get("auto_approval_limit", "$50k")[:10]
        diagram += f'    CreditCheck -- "<{limit}" --> AutoApprove[Auto-Approve]:::green\n'
    
    if collected_data.get("has_manual_credit") == "Yes":
        manual_credit_class = "red" if "credit_decision_to_sales" in gaps_set or "credit_decision_to_customer" in gaps_set else "green"
        approver = collected_data.get("manual_credit_approver", "Analyst")[:15]
        diagram += f'    CreditCheck -- "Above limit" --> ManualReview["{approver}"]:::{manual_credit_class}\n'
        diagram += f'    ManualReview --> Decision{{{{"Decision"}}}}:::{manual_credit_class}\n'
        diagram += '    Decision --> Released\n'
    
    if collected_data.get("has_auto_approval") == "Yes":
        diagram += '    AutoApprove --> Released\n'
    
    diagram += '    Released((Order Released)):::green\n'
    
    return diagram


def generate_gap_summary(gap_analysis):
    """
    Generate a text summary of the GAP analysis.
    """
    gaps = gap_analysis.get("gaps", [])
    strengths = gap_analysis.get("strengths", [])
    missing = gap_analysis.get("missing", [])
    score = gap_analysis.get("score", 0)
    captured = gap_analysis.get("captured_count", 0)
    total_req = gap_analysis.get("total_required", 16)
    
    summary = "## GAP Analysis Summary\n\n"
    summary += f"**Progress:** {captured}/{total_req} process areas captured\n\n"
    
    if score >= 80:
        summary += "✅ **Overall: Strong alignment with SAP best practices**\n\n"
    elif score >= 50:
        summary += "⚠️ **Overall: Moderate alignment, improvement opportunities exist**\n\n"
    else:
        summary += "🔴 **Overall: Continue interview to capture more process details**\n\n"
    
    # Missing attributes (not yet captured)
    if missing:
        summary += "### ⚫ Not Yet Captured\n\n"
        summary += "*Complete the interview to capture these areas:*\n\n"
        for m in missing[:5]:  # Show first 5
            summary += f"- {m['attribute'].replace('_', ' ').title()}\n"
        if len(missing) > 5:
            summary += f"- *...and {len(missing) - 5} more*\n"
        summary += "\n"
    
    # Gaps in captured data
    if gaps:
        summary += "### 🔴 Gaps Identified\n\n"
        for i, gap in enumerate(gaps, 1):
            summary += f"**{i}. {gap['attribute'].replace('_', ' ').title()}**\n"
            summary += f"   - *Current:* {gap['current']}\n"
            summary += f"   - *Standard:* {gap['standard']}\n"
            summary += f"   - *Issue:* {gap.get('issue', 'Deviation from best practice')}\n"
            summary += f"   - *Risk:* {gap['risk']}\n\n"
    
    if strengths:
        summary += "### ✅ Areas of Strength\n\n"
        for s in strengths[:5]:  # Show top 5
            summary += f"- **{s['attribute'].replace('_', ' ').title()}**: {str(s['current'])[:50]}\n"
    
    if gaps or missing:
        summary += "\n### 💡 Recommendations\n\n"
        
        if missing:
            summary += "1. **Complete Discovery**: Continue the interview to capture all process areas\n"
        
        if any(g.get("attribute") in ["manual_intake_method", "manual_data_verification"] for g in gaps):
            summary += "2. **Automate Manual Intake**: Consider implementing OCR/email parsing\n"
        
        if any(g.get("attribute") in ["credit_decision_to_sales", "credit_decision_to_customer"] for g in gaps):
            summary += "3. **Implement Automated Notifications**: Move from phone/email to dashboard alerts\n"
    
    return summary
