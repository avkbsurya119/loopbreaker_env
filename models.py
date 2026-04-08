"""LoopBreaker Environment - Data Models

Defines the Action, Observation, and State classes for the LoopBreaker environment.
"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class LoopBreakerAction(BaseModel):
    """Action that an agent can take in the LoopBreaker environment.

    Attributes:
        action_type: The type of action to perform. Valid values are:
            - detect_repeated_search: Classify behavior as repeated searches
            - detect_revisit: Classify behavior as revisiting same content
            - detect_app_switching: Classify behavior as indecisive app switching
            - pause: Recommend the user to pause
            - decide: Recommend the user to make a decision
            - reframe: Recommend the user to reframe their approach
            - continue_monitoring: Continue observing without intervention
    """
    model_config = ConfigDict(extra="forbid")

    action_type: str = Field(
        ...,
        description="The action to perform"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata for the action"
    )


class Event(BaseModel):
    """A single user activity event."""
    type: str = Field(..., description="Type of event: search, page_visit, app_switch")
    value: str = Field(..., description="The value associated with the event")
    timestamp: Optional[int] = Field(default=None, description="Optional timestamp")


class LoopBreakerObservation(BaseModel):
    """Observation returned by the environment after each step.

    Attributes:
        recent_events: List of recent user activity events
        task_id: Identifier for the current task/scenario
        instructions: Human-readable instructions for the agent
        done: Whether the episode has ended
        reward: Reward for the previous action (if any)
        step_count: Current step number in the episode
        feedback: Optional feedback message about the last action
    """
    recent_events: list[Event] = Field(
        default_factory=list,
        description="Recent user activity events"
    )
    task_id: str = Field(default="", description="Current task identifier")
    instructions: str = Field(
        default="Analyze the user's recent activity and detect any loop patterns. "
                "If a loop is detected, recommend an appropriate intervention.",
        description="Instructions for the agent"
    )
    done: bool = Field(default=False, description="Whether the episode has ended")
    reward: Optional[float] = Field(default=None, description="Reward for the action")
    step_count: int = Field(default=0, description="Current step in the episode")
    feedback: Optional[str] = Field(default=None, description="Feedback about last action")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class LoopBreakerState(BaseModel):
    """Internal state of the LoopBreaker environment.

    Attributes:
        episode_id: Unique identifier for the current episode
        step_count: Number of steps taken in the episode
        task_id: Identifier for the current task/scenario
        history: List of all events in the scenario
        ground_truth_loop_type: The correct loop classification
        ground_truth_intervention: The correct intervention recommendation
        resolved: Whether the loop has been correctly resolved
        max_steps: Maximum number of steps allowed
        cumulative_reward: Total reward accumulated in the episode
    """
    model_config = ConfigDict(extra="allow")

    episode_id: str = Field(default="", description="Episode identifier")
    step_count: int = Field(default=0, description="Current step count")
    task_id: str = Field(default="", description="Task identifier")
    history: list[Event] = Field(default_factory=list, description="All events")
    ground_truth_loop_type: str = Field(default="", description="Correct loop type")
    ground_truth_intervention: str = Field(default="", description="Correct intervention")
    resolved: bool = Field(default=False, description="Whether resolved correctly")
    max_steps: int = Field(default=5, description="Max steps per episode")
    cumulative_reward: float = Field(default=0.0, description="Total reward")
