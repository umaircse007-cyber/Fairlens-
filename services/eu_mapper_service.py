from services.claude_service import interpret_eu_clauses

def map_eu_clauses(metrics, flip_rate, primary_findings):
    triggered_clauses = []
    
    # 1. Article 10(2)(f): Disparate Impact < 0.8
    triggered = False
    for sc, result in metrics.get("disparate_impact_ratio", {}).items():
        if result < 0.8:
            triggered = True
            break
            
    if triggered:
        triggered_clauses.append({
            "clause": "Article 10(2)(f)",
            "title": "Data Governance",
            "trigger_reason": "Disparate Impact Ratio < 0.8",
            "severity": "High Risk"
        })
        
    # 2. Article 5(1)(b): Prohibited Practices
    if flip_rate > 25:
        triggered_clauses.append({
            "clause": "Article 5(1)(b)",
            "title": "Prohibited Practices",
            "trigger_reason": f"Counterfactual flip rate > 25% ({flip_rate:.1f}%)",
            "severity": "High Risk"
        })
        
    # 3. Article 13: Transparency (proxy columns)
    proxy_found = any(f.get("type") == "proxy" for f in primary_findings)
    if proxy_found:
        triggered_clauses.append({
            "clause": "Article 13",
            "title": "Transparency",
            "trigger_reason": "Proxy variables detected mimicking sensitive attributes",
            "severity": "Limited Risk"
        })
        
    # 4. Article 9: Risk Management (single feature dominates the disparity)
    # E.g. feature influence > 0.5
    feature_influence = list(metrics.get("feature_influence", {}).values())
    if feature_influence and feature_influence[0] > 0.5:
        triggered_clauses.append({
            "clause": "Article 9",
            "title": "Risk Management",
            "trigger_reason": "Single feature heavily dominates disparity in outcome",
            "severity": "Limited Risk"
        })
        
    # Send triggered to Claude for explanations
    audit_context = "Audited a dataset with potential demographic bias issues. Needs simple legal interpretation."
    explanations = interpret_eu_clauses(triggered_clauses, audit_context)
    
    for tc in triggered_clauses:
        tc["explanation"] = explanations.get(tc["clause"], "No explanation provided.")
        
    return triggered_clauses
