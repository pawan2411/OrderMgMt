"""
Theory of Constraints (ToC) Analysis Module

Analyzes the captured O2C process data to identify:
- Undesirable Effects (UDEs): Visible negative outcomes
- Intermediate Effects: Mid-level symptoms
- Root Causes: Underlying system/process issues

Generates a Current Reality Tree (CRT) Mermaid diagram showing
causal relationships from root causes to UDEs.
"""

import json
from llm_utils import call_qwen


def analyze_toc(collected_data, conversation_history=None):
    """
    Use LLM to perform Theory of Constraints analysis on the collected process data.
    
    Returns a structured analysis with:
    - udes: List of Undesirable Effects
    - intermediate_effects: List of intermediate symptoms
    - root_causes: List of root causes
    - connections: List of (from_id, to_id) tuples showing causal links
    """
    
    if not collected_data:
        return None
    
    # Build context from collected data
    data_summary = "\n".join([
        f"- {key}: {value}" 
        for key, value in collected_data.items()
        if not key.startswith("has_") and not key.startswith("uses_")
    ])
    
    system_prompt = """You are a Theory of Constraints (ToC) expert analyzing an Order-to-Cash (O2C) process.

Based on the captured process data, identify:
1. UDEs (Undesirable Effects): Observable negative outcomes in the process
2. Intermediate Effects: Mid-level symptoms that connect root causes to UDEs
3. Root Causes: Underlying system/process issues causing the problems

Follow these rules:
- Identify 3-5 UDEs based on process gaps and inefficiencies
- Identify 3-5 Intermediate Effects that explain the causal chain
- Identify 2-4 Root Causes that are the fundamental issues
- Create logical cause-effect connections (from root causes UP to UDEs)

Return your analysis as JSON in this exact format:
{
    "udes": [
        {"id": "UDE1", "label": "Short description of negative outcome"},
        {"id": "UDE2", "label": "..."}
    ],
    "intermediate_effects": [
        {"id": "I1", "label": "Short description of symptom"},
        {"id": "I2", "label": "..."}
    ],
    "root_causes": [
        {"id": "RC1", "label": "Short description of root cause"},
        {"id": "RC2", "label": "..."}
    ],
    "connections": [
        {"from": "RC1", "to": "I1"},
        {"from": "I1", "to": "UDE1"},
        ...
    ]
}

Focus on issues like:
- Manual data entry errors and missing fields
- Credit approval bottlenecks
- Communication delays between teams
- System bypasses and workarounds
- Single points of failure in the process"""

    user_message = f"""Analyze this Order-to-Cash process data and identify the Theory of Constraints Current Reality Tree:

CAPTURED PROCESS DATA:
{data_summary}

Return ONLY valid JSON with udes, intermediate_effects, root_causes, and connections."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    response = call_qwen(messages, temperature=0.3)
    
    if not response:
        return get_default_toc_analysis(collected_data)
    
    # Parse JSON from response
    try:
        response = response.strip()
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        if "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
            result = json.loads(json_str)
            return result
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: ToC JSON parse error: {e}")
    
    return get_default_toc_analysis(collected_data)


def get_default_toc_analysis(collected_data):
    """
    Generate a default ToC analysis based on common O2C patterns
    when LLM parsing fails.
    """
    analysis = {
        "udes": [],
        "intermediate_effects": [],
        "root_causes": [],
        "connections": []
    }
    
    # Check for manual intake issues
    has_manual = collected_data.get("has_manual_intake") == "Yes"
    if has_manual:
        analysis["udes"].append({
            "id": "UDE1", 
            "label": "Downstream delays due to missing order data"
        })
        analysis["udes"].append({
            "id": "UDE2", 
            "label": "Inconsistent order entry quality across channels"
        })
        analysis["intermediate_effects"].append({
            "id": "I1", 
            "label": "Manual orders often lack necessary specific info"
        })
        analysis["intermediate_effects"].append({
            "id": "I2", 
            "label": "Sales Reps prioritize speed over checklist adherence"
        })
        analysis["root_causes"].append({
            "id": "RC1", 
            "label": "ERP checklist is bypassable for non-core fields"
        })
        analysis["root_causes"].append({
            "id": "RC2", 
            "label": "Sales Reps handle manual data entry and verification"
        })
        analysis["connections"].extend([
            {"from": "RC1", "to": "I2"},
            {"from": "RC2", "to": "I2"},
            {"from": "I2", "to": "I1"},
            {"from": "I1", "to": "UDE1"},
            {"from": "I1", "to": "UDE2"}
        ])
    
    # Check for credit approval issues
    has_manual_credit = collected_data.get("has_manual_credit") == "Yes"
    if has_manual_credit:
        analysis["udes"].append({
            "id": "UDE3", 
            "label": "High manual effort for credit approvals"
        })
        analysis["udes"].append({
            "id": "UDE4", 
            "label": "Delayed notification to customer on order status"
        })
        analysis["intermediate_effects"].append({
            "id": "I3", 
            "label": "Credit approval bottlenecks during high volume"
        })
        analysis["intermediate_effects"].append({
            "id": "I4", 
            "label": "Sales Reps act as information relay between teams"
        })
        analysis["root_causes"].append({
            "id": "RC3", 
            "label": "Credit approvals rely on manual review"
        })
        analysis["root_causes"].append({
            "id": "RC4", 
            "label": "No automated notification for non-EDI customers"
        })
        analysis["connections"].extend([
            {"from": "RC3", "to": "I3"},
            {"from": "I3", "to": "UDE3"},
            {"from": "RC3", "to": "I4"},
            {"from": "RC4", "to": "I4"},
            {"from": "I4", "to": "UDE4"}
        ])
    
    # Always add generic issues if no specific ones were identified
    if not analysis["udes"]:
        analysis["udes"].append({
            "id": "UDE1", 
            "label": "Process variability across order channels"
        })
        analysis["udes"].append({
            "id": "UDE2", 
            "label": "Potential for data inconsistencies"
        })
        analysis["intermediate_effects"].append({
            "id": "I1", 
            "label": "Varying process maturity across channels"
        })
        analysis["root_causes"].append({
            "id": "RC1", 
            "label": "Multiple intake channels with different workflows"
        })
        analysis["root_causes"].append({
            "id": "RC2", 
            "label": "Manual touchpoints in order processing"
        })
        analysis["connections"].extend([
            {"from": "RC1", "to": "I1"},
            {"from": "RC2", "to": "I1"},
            {"from": "I1", "to": "UDE1"},
            {"from": "I1", "to": "UDE2"}
        ])
    
    return analysis


def generate_crt_diagram(toc_analysis):
    """
    Generate a Mermaid Current Reality Tree diagram.
    
    The diagram flows bottom-to-top (graph BT) showing:
    - Root Causes at the bottom
    - Intermediate Effects in the middle
    - UDEs at the top
    """
    
    if not toc_analysis:
        return None
    
    # Check if there's actually any content to display
    udes = toc_analysis.get("udes", [])
    intermediate = toc_analysis.get("intermediate_effects", [])
    root_causes = toc_analysis.get("root_causes", [])
    connections = toc_analysis.get("connections", [])
    
    # Return None if there's nothing to show
    if not udes and not root_causes:
        return None
    
    def sanitize_label(label):
        """Sanitize label for Mermaid diagram - escape special characters."""
        if not label:
            return "Unknown"
        label = str(label)
        # Replace characters that break Mermaid syntax
        label = label.replace('"', "'")
        label = label.replace('[', '(')
        label = label.replace(']', ')')
        label = label.replace('{', '(')
        label = label.replace('}', ')')
        label = label.replace('<', 'lt')
        label = label.replace('>', 'gt')
        label = label.replace('#', '')
        label = label.replace('&', 'and')
        label = label.replace('\n', ' ')
        label = label.replace('\r', '')
        # Limit length to prevent overflow
        if len(label) > 60:
            label = label[:57] + "..."
        return label
    
    # Build the Mermaid diagram
    diagram = """graph BT
    %% Define styles
    classDef ude fill:#ffcccc,stroke:#ff0000,stroke-width:2px,color:black,font-weight:bold;
    classDef rootcause fill:#e1ecf4,stroke:#74a9cf,stroke-width:1px,color:black;
    classDef intermediate fill:#ffffff,stroke:#333333,stroke-width:1px,color:black;

    %% --- Undesirable Effects (UDEs) ---
"""
    
    # Add UDE nodes
    for ude in udes:
        node_id = ude.get("id", "UDE")
        label = sanitize_label(ude.get("label", "Undesirable Effect"))
        diagram += f'    {node_id}["{node_id}: {label}"]:::ude\n'
    
    diagram += "\n    %% --- Intermediate Effects ---\n"
    
    # Add Intermediate Effect nodes
    for ie in intermediate:
        node_id = ie.get("id", "I")
        label = sanitize_label(ie.get("label", "Intermediate Effect"))
        diagram += f'    {node_id}("{label}"):::intermediate\n'
    
    diagram += "\n    %% --- Root Causes ---\n"
    
    # Add Root Cause nodes
    for rc in root_causes:
        node_id = rc.get("id", "RC")
        label = sanitize_label(rc.get("label", "Root Cause"))
        diagram += f'    {node_id}["{node_id}: {label}"]:::rootcause\n'
    
    diagram += "\n    %% --- Causal Connections ---\n"
    
    # Add connections
    for conn in connections:
        from_id = conn.get("from", "")
        to_id = conn.get("to", "")
        if from_id and to_id:
            diagram += f'    {from_id} --> {to_id}\n'
    
    return diagram


def generate_toc_summary(toc_analysis):
    """
    Generate a text summary of the ToC analysis.
    """
    if not toc_analysis:
        return "No ToC analysis available."
    
    udes = toc_analysis.get("udes", [])
    root_causes = toc_analysis.get("root_causes", [])
    
    summary = "## Current Reality Tree Analysis\n\n"
    summary += "Based on the Theory of Constraints methodology, we've analyzed your Order-to-Cash process.\n\n"
    
    summary += "### 🔴 Identified Undesirable Effects (UDEs)\n\n"
    summary += "These are the observable negative outcomes in your current process:\n\n"
    for ude in udes:
        summary += f"- **{ude['id']}**: {ude['label']}\n"
    
    summary += "\n### 🔵 Root Causes Identified\n\n"
    summary += "These are the fundamental issues driving the UDEs:\n\n"
    for rc in root_causes:
        summary += f"- **{rc['id']}**: {rc['label']}\n"
    
    summary += "\n### 💡 Core Problem\n\n"
    summary += "The Current Reality Tree reveals that **Process Variability and Manual Hand-offs** "
    summary += "are the core constraints. Addressing the root causes will have a cascading positive effect "
    summary += "on the intermediate symptoms and ultimately eliminate or reduce the UDEs.\n"
    
    return summary
