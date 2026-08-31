import requests
import time
import json
import csv
import os
from datetime import datetime

# ── Config ────────────────────────────────────────────────────
API_URL     = "http://localhost:8000/api/v1/benchmark"
DELAY_SEC   = 3          # Groq free tier rate limit buffer
CSV_OUTPUT  = "benchmark_results.csv"   # local fallback — always saved

# ── Queries (your 16 Simple-tier queries) ────────────────────
EVALUATION_QUERIES = [
    "Explain what a credit rating is and how agencies like Moody's and CRISIL assign ratings.",
    "What is the difference between fiscal policy and monetary policy, and which institutions control each in India?",
    "Explain the concept of sector rotation in equity markets and which sectors typically lead in each cycle.",
    "What does the NIFTY 50 index represent and how are its constituent stocks selected?",
    "Explain what short selling is and the risk it poses to investors who use it.",
    "What are the main business segments of Reliance Industries?",
    "Explain what the Price-to-Book (P/B) ratio measures and why it is widely used for bank stocks.",
    "What is the difference between systematic risk and unsystematic risk in portfolio theory?",
    "Explain the concept of asset allocation and why it matters more than individual stock selection.",
    "What is a repo rate and how does an RBI repo rate hike affect bank lending and equity markets?",
    "Define beta in the context of equity investing and what a beta above 1.0 implies.",
    "Explain what a Non-Performing Asset (NPA) is and why it is the key risk metric for Indian banks."
]

# ── CSV columns — these are the IEEE benchmark metrics ────────
CSV_HEADERS = [
    "run_id", "timestamp", "query", "tier",
    "policy_selected", "agents_spawned", "static_agents",
    "dynamic_tokens", "static_tokens", "token_savings_pct",
    "dynamic_latency_ms", "static_latency_ms", "latency_improvement_pct",
    "status"
]

def write_csv_header():
    """Write header only if file doesn't exist yet."""
    if not os.path.exists(CSV_OUTPUT):
        with open(CSV_OUTPUT, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_HEADERS).writeheader()

def save_to_csv(row: dict):
    """Append one result row to the CSV."""
    with open(CSV_OUTPUT, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=CSV_HEADERS).writerow(row)

def run_batch_evaluations(tier_label: str = "Simple"):
    print(f"\n⚡ DYNAMO Benchmark Runner")
    print(f"   Queries   : {len(EVALUATION_QUERIES)}")
    print(f"   Tier      : {tier_label}")
    print(f"   Endpoint  : {API_URL}")
    print(f"   Output    : {CSV_OUTPUT}")
    print(f"{'─'*60}\n")

    write_csv_header()
    successful, failed = 0, 0

    for index, query in enumerate(EVALUATION_QUERIES, 1):
        run_id    = f"{tier_label.upper()}-{index:03d}"
        timestamp = datetime.utcnow().isoformat()

        print(f"[{index:02d}/{len(EVALUATION_QUERIES)}] {run_id}")
        print(f"   Query: {query[:70]}...")

        payload = {
            "query": query,
            "include_static": True      # runs both dynamic + static baseline
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=300)

            if response.status_code == 200:
                data = response.json()  # ← BenchmarkResult from backend

                row = {
                    "run_id":                   run_id,
                    "timestamp":                timestamp,
                    "query":                    query,
                    "tier":                     tier_label,
                    "policy_selected":          data.get("policy_selected", "unknown"),
                    "agents_spawned":           data.get("agents_spawned", 0),
                    "static_agents":            data.get("static_agents", 5),
                    "dynamic_tokens":           data.get("dynamic_tokens", 0),
                    "static_tokens":            data.get("static_tokens", 0),
                    "token_savings_pct":        data.get("token_savings_pct", 0),
                    "dynamic_latency_ms":       data.get("dynamic_latency_ms", 0),
                    "static_latency_ms":        data.get("static_latency_ms", 0),
                    "latency_improvement_pct":  data.get("latency_improvement_pct", 0),
                    "status":                   "success",
                }

                save_to_csv(row)
                successful += 1

                # ── Print live metrics ─────────────────────────────
                print(f"   ✅ Policy   : {row['policy_selected'].upper()}")
                print(f"   🤖 Agents   : {row['agents_spawned']} dynamic  vs  {row['static_agents']} static")
                print(f"   🪙 Tokens   : {row['dynamic_tokens']}  vs  {row['static_tokens']}  ({row['token_savings_pct']:.1f}% saved)")
                print(f"   ⏱  Latency  : {row['dynamic_latency_ms']:.0f}ms  vs  {row['static_latency_ms']:.0f}ms  ({row['latency_improvement_pct']:.1f}% faster)")

            else:
                # ── Non-200 response ───────────────────────────────
                error_msg = response.json().get("detail", response.text)[:120]
                print(f"   ❌ HTTP {response.status_code}: {error_msg}")
                save_to_csv({
                    "run_id": run_id, "timestamp": timestamp,
                    "query": query, "tier": tier_label,
                    "policy_selected": "error", "agents_spawned": 0,
                    "static_agents": 5, "dynamic_tokens": 0,
                    "static_tokens": 0, "token_savings_pct": 0,
                    "dynamic_latency_ms": 0, "static_latency_ms": 0,
                    "latency_improvement_pct": 0, "status": f"http_{response.status_code}",
                })
                failed += 1

        except requests.exceptions.Timeout:
            print(f"   ⚠️  Timeout (>300s) — query may be too complex for current model")
            failed += 1
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  Connection refused — is uvicorn running on port 8000?")
            failed += 1

        print()
        if index < len(EVALUATION_QUERIES):
            time.sleep(DELAY_SEC)

    # ── Summary ───────────────────────────────────────────────
    print("═" * 60)
    print(f"✅ Completed : {successful}/{len(EVALUATION_QUERIES)}")
    print(f"❌ Failed    : {failed}/{len(EVALUATION_QUERIES)}")
    print(f"📄 Results   : {os.path.abspath(CSV_OUTPUT)}")
    print("═" * 60)
    print("\nNext: open benchmark_results.csv and paste into your")
    print("IEEE Results section tables (Tables II–VI).\n")


if __name__ == "__main__":
    run_batch_evaluations(tier_label="Simple")