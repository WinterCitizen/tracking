from datetime import datetime
from functools import partial
from pathlib import Path
from typing import AsyncGenerator
from zoneinfo import ZoneInfo

import aiohttp
import aiosqlite
from dependency_injector import containers, providers

from tracking.jira import JiraClient
from tracking.saved_worklog_repository import SavedWorklogRepository
from tracking.usecases import SyncWorklogsUsecase
from tracking.worklog_repository import WorklogRepository


async def sqlite_connection_resource(
    sqlite_db_path: Path,
) -> AsyncGenerator[aiosqlite.Connection, None]:
    connection = await aiosqlite.connect(sqlite_db_path)

    yield connection

    await connection.close()


async def client_session_resource(
    auth: aiohttp.BasicAuth,
) -> AsyncGenerator[aiohttp.ClientSession, None]:
    client_session = aiohttp.ClientSession(auth=auth)

    yield client_session

    await client_session.close()


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    sqlite_connection = providers.Resource(sqlite_connection_resource, sqlite_db_path=config.sqlite_db_path)
    basic_auth = providers.Factory(aiohttp.BasicAuth, login=config.jira_login, password=config.jira_password)
    session = providers.Resource(client_session_resource, auth=basic_auth)

    timezone = providers.Factory(ZoneInfo, key=config.timezone)

    saved_worklog_repository = providers.Factory(
        SavedWorklogRepository,
        connection=sqlite_connection,
        timezone=timezone,
    )

    worklog_repository = providers.Factory(WorklogRepository, timezone=timezone)

    now = providers.Factory(partial, datetime.now, tz=timezone)

    jira_client = providers.Factory(
        JiraClient,
        session=session,
        now=now,
    )

    sync_worklogs_usecase = providers.Factory(
        SyncWorklogsUsecase,
        saved_worklog_repository=saved_worklog_repository,
        worklog_repository=worklog_repository,
        jira_client=jira_client,
        timezone=timezone,
    )
