import asyncio
from argparse import ArgumentParser
from pathlib import Path

from dependency_injector.wiring import Provide, inject

from tracking.containers import ApplicationContainer
from tracking.settings import Settings
from tracking.usecases import SyncWorklogsUsecase


@inject
async def _main(
    sync_worklogs_usecase: SyncWorklogsUsecase = Provide[ApplicationContainer.sync_worklogs_usecase],
) -> None:
    argument_parser = ArgumentParser()
    argument_parser.add_argument("track_path", type=Path)

    namespace = argument_parser.parse_args()

    await sync_worklogs_usecase.run(namespace.track_path)


async def main():
    APPLICATION_CONTAINER = ApplicationContainer()
    APPLICATION_CONTAINER.config.from_pydantic(Settings())
    APPLICATION_CONTAINER.wire([__name__])

    await APPLICATION_CONTAINER.init_resources()

    await _main()

    await APPLICATION_CONTAINER.shutdown_resources()


if __name__ == "__main__":
    asyncio.run(main())
