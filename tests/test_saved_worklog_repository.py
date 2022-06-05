from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import aiosqlite
import pytest
from syrupy.assertion import SnapshotAssertion

from tracking.saved_worklog_repository import SavedWorklogRepository
from tracking.values import SavedWorklogValue, WorklogValue


@pytest.fixture
async def connection() -> aiosqlite.Connection:
    async with aiosqlite.connect("test.sqlite") as conn:
        yield conn
        await conn.rollback()


async def test_saved_worklog_repository(connection: aiosqlite.Connection, snapshot: SnapshotAssertion) -> None:
    timezone = ZoneInfo("Asia/Bishkek")
    now = datetime(2022, 5, 8, 0, 0, 0, 0, tzinfo=timezone)
    repository = SavedWorklogRepository(connection=connection, timezone=ZoneInfo("Asia/Bishkek"))

    worklog = WorklogValue(
        issue="asd",
        started_at=now,
        spent=timedelta(minutes=1),
        comment="dsa",
    )
    saved_worklog = SavedWorklogValue(id="asd", created_at=now, worklog=worklog)

    await repository.write(saved_worklog_value=saved_worklog)

    day_start = datetime.combine(worklog.started_at.date(), time.min, tzinfo=timezone)
    day_end = datetime.combine(worklog.started_at.date(), time.max, tzinfo=timezone)

    saved_worklogs = await repository.list(from_started_at=day_start, to_started_at=day_end)
    assert saved_worklogs == snapshot

    deleted_count = await repository.delete(saved_worklog=saved_worklogs[0])
    assert deleted_count == 1

    assert await repository.list(from_started_at=day_start, to_started_at=day_end) == []
