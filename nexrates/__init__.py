from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .data import db
from .routes import router
from .utils import BASE_DIR, settings

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


@app.get('/', include_in_schema=False)
async def index():
    filepath = str(BASE_DIR / 'templates/index.html')
    return FileResponse(filepath, media_type='text/html')
