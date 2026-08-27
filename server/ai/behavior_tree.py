"""Modular Behavior Tree framework for NPC tactical decision-making."""
from __future__ import annotations
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional


class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


class BTNode:
    """Base class for all Behavior Tree nodes."""
    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        raise NotImplementedError


class Sequence(BTNode):
    """Executes children in order until one fails or runs."""
    def __init__(self, children: List[BTNode]) -> None:
        self.children = children

    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        for child in self.children:
            status = child.tick(context)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


class Selector(BTNode):
    """Executes children in order until one succeeds or runs."""
    def __init__(self, children: List[BTNode]) -> None:
        self.children = children

    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        for child in self.children:
            status = child.tick(context)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE


class ActionNode(BTNode):
    """Leaf node that runs an action callable."""
    def __init__(self, action_fn: Callable[[Dict[str, Any]], NodeStatus]) -> None:
        self.action_fn = action_fn

    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        return self.action_fn(context)


class ConditionNode(BTNode):
    """Leaf node that checks a boolean condition."""
    def __init__(self, condition_fn: Callable[[Dict[str, Any]], bool]) -> None:
        self.condition_fn = condition_fn

    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        return NodeStatus.SUCCESS if self.condition_fn(context) else NodeStatus.FAILURE
