from pathlib import Path
from zoneinfo import ZoneInfo

from syrupy.assertion import SnapshotAssertion

from tracking.worklog_repository import WorklogRepository


async def test_worklog_repository_read(snapshot: SnapshotAssertion) -> None:
    repo = WorklogRepository(timezone=ZoneInfo("Asia/Bishkek"))

    assert await repo.read(Path("tests/test_tracks/08-05-2022.yml")) == snapshot
