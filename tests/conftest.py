"""测试公共夹具模块。

该模块提供内存数据库会话，让 ORM、Repository、Scheduler 可以脱离真实 PostgreSQL 单独测试。
"""

from collections.abc import AsyncIterator
import sys
import types
from pathlib import Path

import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models import Account, PublishLog, Task


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """创建 SQLite 内存数据库会话。"""

    # 显式引用模型，确保 metadata 注册完整。
    _ = (Account, PublishLog, Task)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as test_session:
        yield test_session

    await engine.dispose()


@pytest.fixture
def fake_playwright(monkeypatch):  # type: ignore[no-untyped-def]
    """注入轻量 fake Playwright，避免单元测试依赖真实浏览器。"""

    class FakeMouse:
        async def wheel(self, x: int, y: int) -> None:
            self.last_wheel = (x, y)

    class FakePage:
        def __init__(self) -> None:
            self.url = ""
            self.title_text = "Blank"
            self.html = "<html><head><title>Blank</title></head><body></body></html>"
            self.mouse = FakeMouse()
            self.clicked: str | None = None
            self.filled: tuple[str, str] | None = None

        async def goto(self, url: str, timeout: int, wait_until: str) -> None:
            self.url = url
            self.title_text = "Example Domain"
            self.html = "<html><head><title>Example Domain</title></head><body><h1>Example Domain</h1><input id='name'></body></html>"

        async def title(self) -> str:
            return self.title_text

        async def content(self) -> str:
            return self.html

        async def click(self, selector: str, timeout: int) -> None:
            self.clicked = selector

        async def fill(self, selector: str, text: str, timeout: int) -> None:
            self.filled = (selector, text)

        async def screenshot(self, path: str, full_page: bool = True) -> None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(b"\x89PNG\r\n\x1a\n")

    class FakeContext:
        def __init__(self) -> None:
            self.page = FakePage()
            self.pages = [self.page]

        async def new_page(self) -> FakePage:
            return self.page

        async def close(self) -> None:
            return None

    class FakeBrowser:
        def __init__(self) -> None:
            self.context = FakeContext()

        async def new_context(self, viewport: dict[str, int]):
            self.viewport = viewport
            return self.context

        async def close(self) -> None:
            return None

    class FakeChromium:
        async def launch(self, headless: bool, **_: object) -> FakeBrowser:
            self.headless = headless
            self.launch_options = _
            return FakeBrowser()

        async def launch_persistent_context(self, user_data_dir: str, headless: bool, viewport: dict[str, int], **_: object) -> FakeContext:
            self.user_data_dir = user_data_dir
            self.headless = headless
            self.viewport = viewport
            self.launch_options = _
            return FakeContext()

    class FakePlaywright:
        def __init__(self) -> None:
            self.chromium = FakeChromium()

        async def stop(self) -> None:
            return None

    class FakeStarter:
        async def start(self) -> FakePlaywright:
            playwright = FakePlaywright()
            fake_async_api.last_playwright = playwright
            return playwright

    fake_async_api = types.ModuleType("playwright.async_api")
    fake_async_api.async_playwright = lambda: FakeStarter()
    fake_package = types.ModuleType("playwright")
    fake_package.async_api = fake_async_api
    monkeypatch.setitem(sys.modules, "playwright", fake_package)
    monkeypatch.setitem(sys.modules, "playwright.async_api", fake_async_api)
    return fake_async_api
