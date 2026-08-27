from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="The financial research query")
    session_history: Optional[List[str]] = Field(
        default=[], description="Previous queries in this session (for PSE recurrence)"
    )


class BenchmarkRequest(BaseModel):
    query: str = Field(..., description="Query to benchmark")
    runs: int = Field(default=1, ge=1, le=5, description="Number of benchmark runs")
    include_static: bool = Field(default=True, description="Also run static baseline for comparison")
