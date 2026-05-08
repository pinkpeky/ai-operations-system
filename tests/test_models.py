"""ORM 模型测试模块。

该模块验证 Phase 2 三张核心表都具备统一字段，并可被 SQLAlchemy metadata 正确识别。
"""

from app.models.account import Account
from app.models.publish_log import PublishLog
from app.models.task import Task


def test_core_models_have_required_fields() -> None:
    """核心模型必须包含 id、created_at、updated_at、status。"""

    required_fields = {"id", "created_at", "updated_at", "status"}
    for model in (Account, Task, PublishLog):
        column_names = set(model.__table__.columns.keys())
        assert required_fields.issubset(column_names)
