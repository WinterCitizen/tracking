from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from aiohttp import BasicAuth, ClientSession
from syrupy.assertion import SnapshotAssertion

from tracking.jira import JiraClient
from tracking.values import SavedWorklogValue, WorklogValue


@pytest.mark.vcr
async def test_create(snapshot: SnapshotAssertion) -> None:
    now = datetime(2022, 5, 9, 12, 0, 0, 0, tzinfo=ZoneInfo("Asia/Bishkek"))

    session = ClientSession(auth=BasicAuth("user", "password"))

    jira = JiraClient(session=session, now=lambda: now)

    worklog = WorklogValue(
        issue="TRAC-137",
        started_at=now,
        spent=timedelta(minutes=1),
        comment="test",
    )

    assert await jira.create(worklog) == snapshot


@pytest.mark.vcr
async def test_delete() -> None:
    now = datetime(2022, 5, 9, 12, 0, 0, 0, tzinfo=ZoneInfo("Asia/Bishkek"))

    session = ClientSession(auth=BasicAuth("user", "password"))

    jira = JiraClient(session=session, now=lambda: now)

    saved_worklog = SavedWorklogValue(
        id=57396,
        created_at=datetime.now(tz=ZoneInfo("Asia/Bishkek")),
        worklog=WorklogValue(
            issue="TRAC-137",
            started_at=datetime.now(),
            spent=timedelta(minutes=1),
            comment="test",
        ),
    )

    await jira.delete(saved_worklog)
