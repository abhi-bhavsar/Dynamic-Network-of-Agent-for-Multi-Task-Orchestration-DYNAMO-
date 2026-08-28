from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class AgentResult(BaseModel):
    agent_name: str
    findings: str
    confidence: float
    tokens_used: int
    error: str = ""


class QueryResponse(BaseModel):
    query: str
    policy: str
    agents_used: List[str]
    feature_vector: Dict[str, float]
    report: str
    confidence: float
    tokens_used: int
    latency_ms: float
    agent_outputs: Dict[str, Any]
    errors: List[str] = []


class BenchmarkResult(BaseModel):
    query: str
    dynamic_tokens: int
    static_tokens: Optional[int] = None
    dynamic_latency_ms: float
    static_latency_ms: Optional[float] = None
    token_savings_pct: Optional[float] = None
    latency_improvement_pct: Optional[float] = None
    policy_selected: str
    agents_spawned: int
    static_agents: int = 5
    
    # ── Fields required for UI rendering in benchmark mode ────
    report: str = ""
    confidence: float = 0.0
    policy: Optional[str] = None
    agent_outputs: Dict[str, Any] = {}
    feature_vector: Dict[str, Any] = {}
    errors: List[str] = []


class HealthResponse(BaseModel):
    status: str
    model: str
    groq_connected: bool
    version: str = "1.0.0"