from pydantic import BaseModel, Field
from typing import Optional, Literal, List

class ConnectRequest(BaseModel):
    session_id: str
    user_id: str
    video_id: str
    position: Optional[float] = Field(0, ge=0)

class ConnectResponse(BaseModel):
    ok: bool = True
    node_id: int
    assigned: bool = True

class ActionRequest(BaseModel):
    session_id: str
    type: Literal["play", "pause", "seek", "stop"]
    position: Optional[float] = Field(None, ge=0)
    to_position: Optional[float] = Field(None, ge=0)

class DisconnectRequest(BaseModel):
    session_id: str

class NodeInfo(BaseModel):
    node_id: int
    capacity: int
    active_sessions: int

class Metrics(BaseModel):
    active_sessions: int
    nodes: int
    scale_up_count: int
    scale_down_count: int
    events_emitted: int
    ticks_running: int

class NodesResponse(BaseModel):
    nodes: List[NodeInfo]