from importlib import metadata

from fastapi import FastAPI

from .data import db
from .routes import router
from .utils import settings

app = FastAPI(title='NEXRATES API')
app.include_router(router, prefix='/api')


def get_version():
    """Returns the package version details."""
    return metadata.version('nexrates')


@app.on_event('startup')
async def on_startup():
    await db.set_bind(settings.DATABASE_URL)
