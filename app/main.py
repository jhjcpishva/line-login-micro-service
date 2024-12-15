import logging
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import config
from database import MyPbDb
from line import MyLineLogin
import Models

STATIC_PATH = f"{config.APP_PAGE_CONTEXT_PATH}/static"
ENDPOINT_AUTH = f"{config.APP_PAGE_CONTEXT_PATH}/auth"
DEFAULT_NONCE = "__nonce__"


app = FastAPI()
app.mount(path=f"{STATIC_PATH}", app=StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[s.strip() for s in config.APP_ALLOW_ORIGINS.split(',')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger("uvicorn")

db = MyPbDb(logger=logger)


def get_host_url(request: Request) -> str:
    if config.APP_PUBLIC_URL is None:
        return f"{request.base_url.scheme}://{request.base_url.netloc}"
    return config.APP_PUBLIC_URL.rstrip('/')


@app.get(f"{config.APP_PAGE_CONTEXT_PATH}/", response_class=HTMLResponse)
async def read_root(request: Request):
    context = {
        "request": request,
        "title": config.APP_TITLE,
    }
    return templates.TemplateResponse("index.html", context)


@app.get(f"{config.APP_PAGE_CONTEXT_PATH}/login", response_class=HTMLResponse)
async def line_login(request: Request, nonce: str = DEFAULT_NONCE, redirect_url: str = None):
    db.clear_existing_nonce(nonce)
    r = db.create_new_login_nonce(nonce, redirect_url)
    logger.info(f"pb inserted {r.id}")

    location = MyLineLogin.get_line_login_location(
        f"{get_host_url(request)}{ENDPOINT_AUTH}", nonce)

    context = {
        "request": request,
        "title": config.APP_TITLE,
        "static_path": STATIC_PATH,
        "location": location,
    }
    return templates.TemplateResponse("login.html", context)


@app.get(f"{ENDPOINT_AUTH}", response_class=HTMLResponse)
async def authentication(request: Request, code: str, state: str):
    auth = await MyLineLogin.authentication(f"{get_host_url(request)}{ENDPOINT_AUTH}", code)

    new_session = db.create_session(**auth.__dict__)

    # update nonce record
    nonce_record = db.get_nonce(state)
    nonce_record.session = new_session.id
    db.update_login_nonce(nonce_record)

    redirect_url = nonce_record.redirect_url
    if redirect_url:
        _nonce = "" if state == DEFAULT_NONCE else f"&nonce={state}"
        url = f'{redirect_url}{"?" if redirect_url.find("?") == -1 else "&"}success={nonce_record.id}{_nonce}'
        return RedirectResponse(url=url)

    context = {
        "request": request,
        "title": config.APP_TITLE,
        "code": nonce_record.id,
        "nonce": state,
    }
    return templates.TemplateResponse("authenticate.html", context)


@app.post(f"{config.APP_API_CONTEXT_PATH}/v1/auth/collect", response_class=JSONResponse)
async def api_auth_collect(body: Models.AuthCollectRequest) -> Models.AuthCollectResponse:
    r = db.get_nonce_by_id_or_none(body.code)
    if r is None:
        raise HTTPException(status_code=400, detail="nonce not found")
    db.clear_existing_nonce(r.nonce)
    return Models.AuthCollectResponse(session=r.session)


@app.get(f"{config.APP_API_CONTEXT_PATH}/v1/sessions/{{session_id}}/", response_class=JSONResponse)
async def api_session_get(session_id: str) -> Models.GetSessionResponse:
    r = db.get_session_or_none(session_id)
    if r is None:
        raise HTTPException(status_code=400, detail="session not found")

    now = datetime.now(tz=timezone.utc)
    if r.expire < now:
        # session expired
        raise HTTPException(status_code=400, detail="session is expired")

    should_refresh_token = (r.expire - now) < timedelta(minutes=15)

    return Models.GetSessionResponse(
        name=r.name,
        user_id=r.user_id,
        picture=r.picture,
        expireAt=r.expire.isoformat(),
        shouldRefreshToken=should_refresh_token,
    )


@app.post(f"{config.APP_API_CONTEXT_PATH}/v1/sessions/{{session_id}}/refresh", status_code=204)
async def api_session_refresh(session_id: str) -> Response:
    r = db.get_session_or_none(session_id)
    if r is None:
        raise HTTPException(status_code=400, detail="session not found")

    refresh_result = await MyLineLogin.refresh_token(r.refresh_token)

    r.access_token = refresh_result.access_token
    r.refresh_token = refresh_result.refresh_token
    r.expire = refresh_result.expire
    db.update_session(r)

    return Response(status_code=204)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.APP_PORT, reload=(not config.PRODUCTION))
