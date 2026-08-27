import streamlit as st
import requests
import json
import time
import plotly.graph_objects as go

API_BASE = "http://localhost:8000"
API_V1   = f"{API_BASE}/api/v1"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DYNAMO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ───────────────────────────────────────────────────
if "history"        not in st.session_state: st.session_state.history = []
if "total_queries"  not in st.session_state: st.session_state.total_queries = 0
if "total_tokens"   not in st.session_state: st.session_state.total_tokens = 0
if "total_saved"    not in st.session_state: st.session_state.total_saved = 0
if "results_log"    not in st.session_state: st.session_state.results_log = []

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ DYNAMO")
    st.caption("Dynamic Network of Agents\nfor Multi-Task Orchestration")
    st.divider()

    # Backend status
    try:
        r = requests.get(f"{API_BASE}/health", timeout=2)
        h = r.json()
        if h.get("groq_connected"):
            st.success(f"Backend Online ✓")
            st.caption(f"Model: `{h.get('model','')}`")
        else:
            st.warning("Backend up — Groq key missing")
    except Exception:
        st.error("Backend Offline ✗")
        st.caption("Run: `uvicorn backend.main:app --reload`")

    st.divider()
    st.subheader("📊 Session Stats")
    st.metric("Queries Run",   st.session_state.total_queries)
    st.metric("Total Tokens",  st.session_state.total_tokens)

    if st.button("🔄 Reset Session", use_container_width=True):
        for k in ["history","total_queries","total_tokens","total_saved","results_log"]:
            del st.session_state[k]
        st.rerun()

    st.divider()
    st.subheader("⚙️ Settings")
    show_trace  = st.toggle("Show Agent Trace",  value=True)
    show_slices = st.toggle("Show Memory Slices", value=False)
    show_bench  = st.toggle("Run Benchmark Mode", value=False)

# ── Main UI ──────────────────────────────────────────────────────────────────
st.title("⚡ DYNAMO")
st.caption("**D**ynamic **N**etwork of **A**gents for **M**ulti-task **O**rchestration — Policy-Selective Execution")
st.divider()

# Query input
query = st.text_area(
    "**Enter your research query**",
    placeholder=(
        "e.g.  'What is the current price of AAPL?'\n"
        "      'Analyze Tesla's Q4 performance and 2025 outlook'\n"
        "      'Comprehensive investment analysis of NIFTY 50 IT sector'"
    ),
    height=110,
    key="query_input",
)

col_btn, col_space = st.columns([2, 8])
with col_btn:
    run_btn = st.button("🚀 Run DYNAMO", type="primary", use_container_width=True)

# ── Query Execution ──────────────────────────────────────────────────────────
if run_btn and query.strip():

    payload = {
        "query": query.strip(),
        "session_history": st.session_state.history[-10:],
    }

    with st.status("⚡ DYNAMO is orchestrating agents...", expanded=True) as status:
        st.write("🔍 Extracting feature vector F(Q)...")
        time.sleep(0.3)
        st.write("🎯 PSE selecting spawning policy Φ(F(Q))...")
        time.sleep(0.3)
        st.write("📋 Orchestrator generating Spawn Manifest...")
        time.sleep(0.3)
        st.write("🤖 Spawning agents via asyncio.gather()...")

        t_start = time.time()
        try:
            endpoint = "/benchmark" if show_bench else "/query"
            resp = requests.post(
                f"{API_V1}{endpoint}",
                json=payload if not show_bench else {**payload, "include_static": True},
                timeout=120,
            )
            resp.raise_for_status()
            result = resp.json()
            elapsed = round((time.time() - t_start) * 1000, 1)
            status.update(label="✅ DYNAMO complete!", state="complete")
        except requests.exceptions.ConnectionError:
            status.update(label="❌ Backend unreachable", state="error")
            st.error("Start the backend: `uvicorn backend.main:app --reload`")
            st.stop()
        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(str(e))
            st.stop()

    # Update session
    st.session_state.history.append(query.strip())
    st.session_state.total_queries += 1
    st.session_state.total_tokens  += result.get("tokens_used", result.get("dynamic_tokens", 0))
    st.session_state.results_log.append(result)

    # ── Metrics row ───────────────────────────────────────────
    st.divider()
    m1, m2, m3, m4, m5 = st.columns(5)

    if show_bench:
        dyn_tok  = result.get("dynamic_tokens", 0)
        stat_tok = result.get("static_tokens", 0)
        savings  = result.get("token_savings_pct", 0)
        m1.metric("Policy",        result.get("policy_selected","").replace("_"," ").title())
        m2.metric("Agents (Dyn)",  result.get("agents_spawned", 0), delta=f"-{5-result.get('agents_spawned',5)} vs static")
        m3.metric("Dyn Tokens",    dyn_tok)
        m4.metric("Token Savings", f"{savings:.1f}%")
        m5.metric("Dyn Latency",   f"{result.get('dynamic_latency_ms',0):.0f}ms")
    else:
        fv = result.get("feature_vector", {})
        m1.metric("Policy",     result.get("policy","").replace("_"," ").title())
        m2.metric("Agents",     len(result.get("agents_used", [])))
        m3.metric("Tokens",     result.get("tokens_used", 0))
        m4.metric("Latency",    f"{result.get('latency_ms',0):.0f}ms")
        m5.metric("Confidence", f"{result.get('confidence',0):.0%}")

    # ── PSE feature vector ────────────────────────────────────
    fv = result.get("feature_vector", {})
    if fv:
        with st.expander("🎯 PSE Analysis — Feature Vector F(Q)", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Novelty (N)",    f"{fv.get('N',0):.2f}",
                      help="How novel is this query vs session history? (1=completely new)")
            c2.metric("Urgency (U)",    f"{fv.get('U',0):.2f}",
                      help="How time-sensitive is this query? (1=real-time required)")
            c3.metric("Complexity (C)", f"{int(fv.get('C',1))}/5",
                      help="Predicted agent cardinality (1=single agent, 5=full suite)")
            c4.metric("Recurrence (R)", f"{fv.get('R',0):.2f}",
                      help="How often does this pattern appear in session? (1=highly recurring)")

            # Radar chart for feature vector
            categories = ["Novelty", "Urgency", "Complexity/5", "Recurrence"]
            values = [
                fv.get("N", 0),
                fv.get("U", 0),
                fv.get("C", 1) / 5,
                fv.get("R", 0),
            ]
            fig = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                line_color="#1E3A5F",
                fillcolor="rgba(30,58,95,0.25)",
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,1])),
                showlegend=False,
                height=280,
                margin=dict(l=40, r=40, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Benchmark comparison chart ────────────────────────────
    if show_bench and result.get("static_tokens"):
        with st.expander("📊 Benchmark — Dynamic vs Static", expanded=True):
            bc1, bc2 = st.columns(2)

            with bc1:
                fig_tok = go.Figure(go.Bar(
                    x=["Static Baseline", "DYNAMO (Dynamic)"],
                    y=[result["static_tokens"], result["dynamic_tokens"]],
                    marker_color=["#7FB3D3", "#1E3A5F"],
                    text=[result["static_tokens"], result["dynamic_tokens"]],
                    textposition="auto",
                ))
                fig_tok.update_layout(title="Token Consumption", height=280,
                                      margin=dict(l=10,r=10,t=40,b=10))
                st.plotly_chart(fig_tok, use_container_width=True)

            with bc2:
                if result.get("static_latency_ms"):
                    fig_lat = go.Figure(go.Bar(
                        x=["Static Baseline", "DYNAMO (Dynamic)"],
                        y=[result["static_latency_ms"], result["dynamic_latency_ms"]],
                        marker_color=["#F0A500", "#7B3F00"],
                        text=[f"{result['static_latency_ms']:.0f}ms", f"{result['dynamic_latency_ms']:.0f}ms"],
                        textposition="auto",
                    ))
                    fig_lat.update_layout(title="Execution Latency (ms)", height=280,
                                          margin=dict(l=10,r=10,t=40,b=10))
                    st.plotly_chart(fig_lat, use_container_width=True)

    # ── Agent trace ───────────────────────────────────────────
    if show_trace:
        agent_outs = result.get("agent_outputs", {})
        if agent_outs:
            with st.expander(f"🤖 Agent Trace — {len(agent_outs)} agents active", expanded=False):
                for agent_key, output in agent_outs.items():
                    label = agent_key.replace("deploy_", "").replace("_", " ").title()
                    conf  = output.get("confidence", 0.0)
                    toks  = output.get("tokens_used", 0)
                    err   = output.get("error", "")

                    col_l, col_r = st.columns([6, 2])
                    with col_l:
                        st.markdown(f"**📌 {label} Agent**")
                    with col_r:
                        st.caption(f"🎯 {conf:.0%} | 🪙 {toks} tok")

                    if err and err != "":
                        st.error(f"Agent error: {err}")
                    else:
                        st.markdown(output.get("findings", "_No output_"))

                    st.progress(conf)
                    st.divider()

    # ── Memory slices ─────────────────────────────────────────
    if show_slices and not show_bench:
        slices = result.get("agent_outputs", {})
        if slices:
            with st.expander("🔪 Memory Slices — Context partitioned per agent", expanded=False):
                st.caption("Shows M(aᵢ) ⊆ GlobalContext — what each agent actually received")
                for agent_key in slices:
                    st.code(f"{agent_key}: received targeted memory slice (filtered from global context)", language="text")

    # ── Final report ──────────────────────────────────────────
    st.divider()
    st.subheader("📄 Synthesized Research Report")

    report = result.get("report", "No report generated.")
    st.markdown(report)

    conf = result.get("confidence", 0.0)
    st.progress(conf, text=f"Overall Confidence: {conf:.0%}")

    # Download button
    st.download_button(
        label="⬇️ Download Report",
        data=f"# DYNAMO Research Report\n\n**Query:** {query}\n\n{report}",
        file_name="dynamo_report.md",
        mime="text/markdown",
    )

elif run_btn and not query.strip():
    st.warning("Please enter a query.")

# ── Query History ─────────────────────────────────────────────────────────────
if st.session_state.results_log:
    with st.expander(f"📜 Session History ({len(st.session_state.history)} queries)", expanded=False):
        for i, q in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"`{i}.` {q}")
