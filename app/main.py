import json
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config
from database import MyPbDb
from line import MyLineLogin

app = FastAPI()
app.mount(path="/static", app=StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger("uvicorn")

db = MyPbDb()


def get_host_url(request: Request) -> str:
    return f"{request.base_url.scheme}://{request.base_url.netloc}"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    context = {
        "request": request,
        "title": config.APP_TITLE,
        "name": "World",
        "debug": json.dumps({
            "base/url": request.query_params.__dict__,
        }),
    }
    return templates.TemplateResponse("index.html", context)


@app.get(config.ENDPOINT_LOGIN, response_class=HTMLResponse)
async def line_login(request: Request, nonce: str = "__none__", redirect_url: str = None):
    db.clear_existing_nonce(nonce)
    r = db.create_new_login_nonce(nonce, redirect_url)
    logger.info(f"pb inserted {r.id}")

    location = MyLineLogin.get_line_login_location(
        f"{get_host_url(request)}{config.ENDPOINT_AUTH}", nonce)

    context = {
        "request": request,
        "title": config.APP_TITLE,
        "location": location,
    }
    return templates.TemplateResponse("login.html", context)


@app.get(config.ENDPOINT_AUTH, response_class=HTMLResponse)
async def authentication(request: Request, code: str, state: str):
    auth = await MyLineLogin.authentication(f"{get_host_url(request)}{config.ENDPOINT_AUTH}", code)

    new_session = db.create_session(**auth.__dict__)

    # update nonce record
    nonce_record = db.get_nonce(state)
    nonce_record.session = new_session.id
    db.update_login_nonce(nonce_record)

    # TODO: cookie書き込みも対応する？

    redirect_url = nonce_record.redirect_url
    if redirect_url:
        url = f'{redirect_url}{"?" if redirect_url.find("?") == -1 else "&"}success={new_session.id}'
        return RedirectResponse(url=url)

    context = {
        "request": request,
        "title": config.APP_TITLE,
        "name": "Auth!",
        "debug": json.dumps({
            "user_id": auth.user_id,
            "name": auth.name,
            "picture": auth.picture,
            "session": new_session.__repr__(),
        }, indent=2, ensure_ascii=False),
    }
    return templates.TemplateResponse("index.html", context)


logger.info(f"Valid endpoints: [{config.ENDPOINT_LOGIN}, {config.ENDPOINT_AUTH}]")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=(not config.PRODUCTION))
