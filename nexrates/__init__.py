from importlib import metadata

from fastapi import FastAPI

from .data import db
from .routes import router
from .utils import settings

TITLE = 'Naira Exchange Rates API'
DESC = 'API service for current and historic Naira exchange rates published by CBN'


app = FastAPI(title=TITLE, description=DESC, docs_url=None, redoc_url='/api/docs', version='v1')
app.include_router(router)


def get_version():
    """Returns the package version details."""
    return metadata.version('nexrates')


@app.on_event('startup')
async def on_startup():
    await db.set_bind(settings.DATABASE_URL)
