import os
import datetime

LOG_FILE = "honeypot_security.log"
OUTPUT_HTML = "index.html"

def generate_web_dashboard():
    if not os.path.exists(LOG_FILE):
        print(f"[-] Error: {LOG_FILE} missing! Run the honeypot first.")
        return

    # Counter variables to display on our dashboard metrics
    total_conns = 0
    cred_entries = ""
    malware_entries = ""

    with open(LOG_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            total_conns += 1
            
            # Highlight credentials dynamically
            if "ACTION:CRED_CAPTURE" in line:
                # Extract the core data details cleanly
                details = line.split("DATA:")[-1].strip()
                cred_entries += f"<tr><td>⚠️ Credential Intercepted</td><td><code>{details}</code></td></tr>"
                
            # Highlight malware staging links
            elif "ACTION:MALWARE_STAGING" in line:
                details = line.split("DATA:")[-1].strip()
                malware_entries += f"<tr class='threat-row'><td>🔥 Malware Download Triggered</td><td><code>{details}</code></td></tr>"

    # The HTML/CSS Visual Interface Structure
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
            <div>{total_conns}</div>
        </div>
        <div class="card" style="border-left: 4px solid #ff7b72;">
            <h3>Active Target Status</h3>
            <div style="color: #56d364;">ONLINE / MONITORING</div>
        </div>
    </div>

    <h2> Active Network Alerts</h2>
    <table>
        <thead>
            <tr>
                <th>Event Severity / Classification</th>
                <th>Extracted Log Telemetry & Payloads</th>
            </tr>
        </thead>
        <tbody>
            {malware_entries}
            {cred_entries}
        </tbody>
    </table>

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as out:
        out.write(html_template)
    print(f"[+] Live Web Interface Compiled successfully -> {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_web_dashboard()