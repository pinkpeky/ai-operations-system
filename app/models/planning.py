"""Agent Planning ORM 模型。

Phase 16 只建立可观测、可执行的计划基础层，不实现 autonomous planner、ReAct 或递归规划。
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PlanStatus, PlanStepStatus


class Plan(Base):
    """用户目标对应的一份结构化执行计划。"""

    __tablename__ = "plans"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Plan ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    session_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), index=True, nullable=True, comment="Memory session ID")
    root_goal: Mapped[str] = mapped_column(Text, nullable=False, comment="用户根目标")
    planner_agent: Mapped[str] = mapped_column(String(128), nullable=False, default="simple_planner", comment="规划 Agent")
    status: Mapped[str] = mapped_column(
        String(32),
        default=PlanStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="计划状态",
    )
    plan_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False, comment="计划元数据")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    steps: Mapped[list["PlanStep"]] = relationship(back_populates="plan", cascade="save-update, merge")
    reviews: Mapped[list["PlanReview"]] = relationship(back_populates="plan", cascade="save-update, merge")


class PlanStep(Base):
    """计划中的单个可执行步骤。"""

    __tablename__ = "plan_steps"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Plan step ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), index=True, nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False, comment="步骤顺序")
    agent_name: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="目标 Agent")
    tool_name: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="目标 Tool")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="步骤标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="步骤说明")
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="步骤输入")
    output_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True, comment="步骤输出")
    status: Mapped[str] = mapped_column(
        String(32),
        default=PlanStepStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="步骤状态",
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="步骤错误")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="步骤耗时毫秒")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plan: Mapped[Plan] = relationship(back_populates="steps")


class PlanReview(Base):
    """计划执行后的轻量 review 记录。"""

    __tablename__ = "plan_reviews"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Plan review ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="工作区 ID")
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), index=True, nullable=False)
    reviewer_agent: Mapped[str] = mapped_column(String(128), nullable=False, default="review_agent", comment="Review Agent")
    review_result: Mapped[str] = mapped_column(String(64), nullable=False, comment="review 结果")
    score: Mapped[float | None] = mapped_column(Float, nullable=True, comment="人工或规则评分")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="review 说明")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    plan: Mapped[Plan] = relationship(back_populates="reviews")
