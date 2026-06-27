import os
import json
import datetime

LOG_FILE = "honeypot_security.log"
OUTPUT_JSON = "threat_intelligence_report.json"
OUTPUT_HTML = "index.html"

def parse_raw_log_file():
    """
    Reads the persistent security log file and extracts raw text lines
    into structured data objects for threat intelligence analytics.
    """
    if not os.path.exists(LOG_FILE):
        print(f"[-] Error: {LOG_FILE} does not exist yet. Run the honeypot to generate logs first!")
        return []

    parsed_events = []
    
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            try:
                # Split by the main pipe delimiter
                parts = line.split(" | ")
                if len(parts) < 4:
                    continue
                    
                # Extract Timestamp and ID
                timestamp_id = parts[0].split("] ")
                timestamp = timestamp_id[0].replace("[", "")
                attacker_id = timestamp_id[1].replace("ID:", "")
                
                # Extract Location, Action, and Data payloads
                location = parts[1].replace("LOC:", "")
                action = parts[2].replace("ACTION:", "")
                raw_data = parts[3].replace("DATA:", "")
                
                # Append structured dictionary to our list matrix
                event_obj = {
                    "timestamp": timestamp,
                    "attacker_id": attacker_id,
                    "location": location,
                    "action": action,
                    "details": raw_data
                }
                parsed_events.append(event_obj)
                
            except Exception:
                # Skip any malformed lines cleanly without crashing the parser
                continue
                
    return parsed_events


def generate_reports(parsed_events):
    """
    Analyzes structured events to compute threat metrics, exports an audit-ready 
    JSON file, and builds a dark-themed visual HTML web dashboard.
    """
    if not parsed_events:
        print("[-] No data to analyze.")
        return

    # 1. ANALYTICS & JSON GENERATION BLOCK
    metrics = {
        "total_connections": len(parsed_events),
        "unique_attackers_count": 0,
        "top_sources": {},
        "captured_credentials": [],
        "extracted_malware_urls": []
    }

    unique_ids = set()
    cred_entries_html = ""
    malware_entries_html = ""

    for event in parsed_events:
        unique_ids.add(event["attacker_id"])
        
        # Track geographic frequency
        loc = event["location"]
        metrics["top_sources"][loc] = metrics["top_sources"].get(loc, 0) + 1
        
        # Aggregate captured credentials & build HTML components
        if event["action"] == "CRED_CAPTURE":
            metrics["captured_credentials"].append({
                "timestamp": event["timestamp"],
                "attacker_id": event["attacker_id"],
                "credentials": event["details"]
            })
            cred_entries_html += f"<tr><td>⚠️ Credential Intercepted</td><td><code>{event['details']}</code></td></tr>"
            
        # Aggregate extracted malware links & build HTML components
        elif event["action"] == "MALWARE_STAGING":
            metrics["extracted_malware_urls"].append({
                "timestamp": event["timestamp"],
                "attacker_id": event["attacker_id"],
                "payload_details": event["details"]
            })
            malware_entries_html += f"<tr class='threat-row'><td>🔥 Malware Download Triggered</td><td><code>{event['details']}</code></td></tr>"

    metrics["unique_attackers_count"] = len(unique_ids)

    # Export compiled data directly to JSON format
    with open(OUTPUT_JSON, "w") as jf:
        json.dump(metrics, jf, indent=4)
    print(f"[+] Threat Intelligence Report compiled -> {OUTPUT_JSON}")

    # 2. VISUAL WEB INTERFACE GENERATION BLOCK
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Privacy-First Threat Intel Grid</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 40px; }}
        h1 {{ color: #58a6ff; border-bottom: 1px solid #21262d; padding-bottom: 10px; }}
        .metrics-container {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .card {{ background-color: #161b22; padding: 20px; border-radius: 6px; border: 1px solid #30363d; flex: 1; }}
        .card h3 {{ margin: 0 0 10px 0; color: #8b949e; font-size: 14px; text-transform: uppercase; }}
        .card div {{ font-size: 32px; font-weight: bold; color: #f0883e; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #161b22; border-radius: 6px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #30363d; }}
        th {{ background-color: #21262d; color: #58a6ff; font-weight: 600; }}
        tr:hover {{ background-color: #21262d; }}
        .threat-row {{ background-color: #2c1a1d; }}
        .threat-row:hover {{ background-color: #3c1e23; }}
        code {{ background-color: #21262d; padding: 3px 6px; border-radius: 4px; color: #ff7b72; font-family: monospace; }}
    </style>
</head>
<body>

    <h1>🛡️ Privacy-First Threat Intelligence Console</h1>
    <p>Live Monitoring Environment Matrix Logs Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="metrics-container">
        <div class="card">
            <h3>Total Aggregated Attacks</h3>
            <div>{len(parsed_events)}</div>
        </div>
        <div class="card">
            <h3>Unique Threat Actors</h3>
            <div>{len(unique_ids)}</div>
        </div>
        <div class="card" style="border-left: 4px solid #56d364;">
            <h3>Active Target Status</h3>
            <div style="color: #56d364;">ONLINE / MONITORING</div>
        </div>
    </div>

    <h2>🚨 Active Network Alerts</h2>
    <table>
        <thead>
            <tr>
                <th>Event Severity / Classification</th>
                <th>Extracted Log Telemetry & Payloads</th>
            </tr>
        </thead>
        <tbody>
            {malware_entries_html}
            {cred_entries_html}
        </tbody>
    </table>

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as out:
        out.write(html_template)
    print(f"[+] Live Web Dashboard compiled -> {OUTPUT_HTML}")


if __name__ == "__main__":
    # Execute the full processing loop
    events = parse_raw_log_file()
    generate_reports(events)