from dataclasses import dataclass, field
from typing import Dict, Optional, Set, List
from .events import EventEmitter
from ..core.settings import settings

@dataclass
class Node:
    node_id: int
    capacity: int
    sessions: Set[str] = field(default_factory=set)

    @property
    def utilization(self) -> float:
        return len(self.sessions) / self.capacity if self.capacity else 0.0

class Cluster:
    def __init__(self, emitter: EventEmitter):
        self.emitter = emitter
        self.nodes: Dict[int, Node] = {}
        self.next_node_id = 1
        self.scale_up_count = 0
        self.scale_down_count = 0
        self._low_util_since: Optional[float] = None
        # start with one node
        self.add_node()

    def add_node(self) -> Node:
        node = Node(node_id=self.next_node_id, capacity=settings.NODE_CAPACITY)
        self.nodes[node.node_id] = node
        self.next_node_id += 1
        self.scale_up_count += 1
        self.emitter.emit({"event": "scale_up", "node_id": node.node_id})
        return node

    def remove_node(self, node_id: int):
        node = self.nodes.get(node_id)
        if not node or node.sessions:
            return False
        del self.nodes[node_id]
        self.scale_down_count += 1
        self.emitter.emit({"event": "scale_down", "node_id": node_id})
        return True

    def pick_node_for_new_session(self) -> Optional[Node]:
        # try to place on least utilized node first
        if not self.nodes:
            self.add_node()
        nodes_sorted = sorted(self.nodes.values(), key=lambda n: (n.utilization, len(n.sessions)))
        candidate = nodes_sorted[0]
        if candidate.utilization >= settings.SCALE_UP_THRESHOLD:
            candidate = self.add_node()
        return candidate

    def assign(self, session_id: str) -> int:
        node = self.pick_node_for_new_session()
        node.sessions.add(session_id)
        return node.node_id

    def release(self, session_id: str):
        for node in self.nodes.values():
            if session_id in node.sessions:
                node.sessions.remove(session_id)
                return node.node_id
        return -1

    def autoscale_once(self, now_ts: float):
        # scale up handled on placement; here focus on scale down
        total_capacity = sum(n.capacity for n in self.nodes.values()) or 1
        total_sessions = sum(len(n.sessions) for n in self.nodes.values())
        global_util = total_sessions / total_capacity

        import time
        if global_util < settings.SCALE_DOWN_THRESHOLD:
            if self._low_util_since is None:
                self._low_util_since = now_ts
            elif now_ts - self._low_util_since >= settings.SCALE_DOWN_COOLDOWN_S:
                # try remove an empty tail node (highest id first)
                for nid in sorted(self.nodes.keys(), reverse=True):
                    if not self.nodes[nid].sessions and len(self.nodes) > 1:
                        self.remove_node(nid)
                        self._low_util_since = None
                        break
        else:
            self._low_util_since = None

    def node_snapshot(self) -> List[dict]:
        return [
            {
                "node_id": n.node_id,
                "capacity": n.capacity,
                "active_sessions": len(n.sessions),
                "utilization": n.utilization,
            }
            for n in sorted(self.nodes.values(), key=lambda x: x.node_id)
        ]