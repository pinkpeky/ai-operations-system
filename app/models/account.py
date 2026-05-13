"""账号 ORM 模型模块。

accounts 表用于保存外部平台账号或渠道账号，为后续自动发布任务提供账号上下文。
"""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import AccountStatus

if TYPE_CHECKING:
    from app.models.publish_log import PublishLog
    from app.models.task import Task


class Account(IdTimestampMixin, Base):
    """账号数据模型。"""

    __tablename__ = "accounts"

    status: Mapped[str] = mapped_column(
        String(32),
        default=AccountStatus.ACTIVE.value,
        index=True,
        nullable=False,
        comment="账号状态",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="账号名称",
    )
    platform: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
        comment="平台标识",
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="账号配置，敏感字段后续应接入密钥管理",
    )

    # relationship 只描述 ORM 关系，不在数据库中新增字段。
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="account",
        cascade="save-update, merge",
    )
    publish_logs: Mapped[list["PublishLog"]] = relationship(
        back_populates="account",
        cascade="save-update, merge",
    )
