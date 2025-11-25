"""Base agent class for all agents in the system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"


class AgentResult:
    """Standard result object for agent execution."""

    def __init__(
        self,
        status: AgentStatus,
        output: Any,
        metrics: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.status = status
        self.output = output
        self.metrics = metrics or {}
        self.errors = errors or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'status': self.status.value,
            'output': self.output,
            'metrics': self.metrics,
            'errors': self.errors,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == AgentStatus.SUCCESS


class ValidationResult:
    """Result of input validation."""

    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    @classmethod
    def success(cls) -> 'ValidationResult':
        """Create successful validation result."""
        return cls(is_valid=True)

    @classmethod
    def failure(cls, errors: List[str]) -> 'ValidationResult':
        """Create failed validation result."""
        return cls(is_valid=False, errors=errors)


class BaseAgent(ABC):
    """
    Base class for all agents.

    All agents must inherit from this class and implement:
    - _execute(): Core execution logic
    - validate_inputs(): Input validation
    """

    def __init__(
        self,
        name: str,
        description: str,
        tools: Optional[List[Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            description: Agent description
            tools: List of tools available to agent
            config: Agent configuration
        """
        self.name = name
        self.description = description
        self.tools = tools or []
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.execution_history: List[AgentResult] = []

        logger.info(f"Initialized agent: {self.name}")

    def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute agent with given context.

        Args:
            context: Execution context with inputs

        Returns:
            AgentResult with status and output
        """
        logger.info(f"[{self.name}] Starting execution")
        self.status = AgentStatus.RUNNING

        try:
            # Step 1: Validate inputs
            validation_result = self.validate_inputs(context)
            if not validation_result.is_valid:
                logger.error(f"[{self.name}] Input validation failed: {validation_result.errors}")
                result = AgentResult(
                    status=AgentStatus.FAILED,
                    output=None,
                    errors=validation_result.errors
                )
                self.status = AgentStatus.FAILED
                self.execution_history.append(result)
                return result

            # Step 2: Execute core logic
            logger.info(f"[{self.name}] Executing core logic")
            output = self._execute(context)

            # Step 3: Create success result
            result = AgentResult(
                status=AgentStatus.SUCCESS,
                output=output,
                metadata={
                    'agent_name': self.name,
                    'context': context
                }
            )
            self.status = AgentStatus.SUCCESS
            logger.info(f"[{self.name}] Execution completed successfully")

        except Exception as e:
            logger.exception(f"[{self.name}] Execution failed: {str(e)}")
            result = AgentResult(
                status=AgentStatus.FAILED,
                output=None,
                errors=[str(e)]
            )
            self.status = AgentStatus.FAILED

        # Store result in history
        self.execution_history.append(result)
        return result

    @abstractmethod
    def _execute(self, context: Dict[str, Any]) -> Any:
        """
        Core execution logic (must be implemented by subclass).

        Args:
            context: Execution context

        Returns:
            Execution output
        """
        pass

    @abstractmethod
    def validate_inputs(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate input context (must be implemented by subclass).

        Args:
            context: Input context to validate

        Returns:
            ValidationResult object
        """
        pass

    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status

    def get_execution_history(self) -> List[AgentResult]:
        """Get execution history."""
        return self.execution_history

    def reset(self):
        """Reset agent to initial state."""
        self.status = AgentStatus.IDLE
        self.execution_history = []
        logger.info(f"[{self.name}] Reset to initial state")
