import os
import sys
import ollama  # pip install ollama
from pathlib import Path

# ----------------------------
# CONFIGURATION
# ----------------------------
MODEL_NAME = "llama3"  # Ensure this model is available in Ollama
CHUNK_SIZE = 50        # Number of log lines per request
MAX_LOG_SIZE_MB = 50   # Safety limit for huge logs

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------

## MCP Server
### log files        - scans logs files (write a memory intensive app)
### resource monitor - polls memory


def read_log_file(file_path):
    """Read log file safely with size limit."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {file_path}")
    if path.stat().st_size > MAX_LOG_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Log file exceeds {MAX_LOG_SIZE_MB} MB limit.")
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()

def analyze_chunk(chunk):
    """Send a chunk of logs to LLaMA for analysis."""
    prompt = (
        "You are a log analysis assistant. "
        "Given the following log lines, identify any potential errors, warnings, "
        "security issues, or anomalies. Respond in JSON with fields: "
        "`issues_found` (true/false) and `details` (list of strings).\n\n"
        f"Log lines:\n{''.join(chunk)}"
    )
    
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error analyzing chunk: {e}"

def scan_logs(file_path):
    """Main scanning function."""
    lines = read_log_file(file_path)
    results = []
    
    for i in range(0, len(lines), CHUNK_SIZE):
        chunk = lines[i:i + CHUNK_SIZE]
        print(f"Analyzing lines {i+1} to {i+len(chunk)}...")
        analysis = analyze_chunk(chunk)
        results.append({
            "start_line": i + 1,
            "end_line": i + len(chunk),
            "analysis": analysis
        })
    
    return results

# ----------------------------
# MAIN EXECUTION
# ----------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <log_file_path>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    try:
        scan_results = scan_logs(log_file)
        print("\n=== SCAN RESULTS ===")
        for res in scan_results:
            print(f"Lines {res['start_line']}-{res['end_line']}:")
            print(res["analysis"])
            print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

 

#llama_log_scanner.py /path/to/your/logfile.log 