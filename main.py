import json
import logging

import httpx
import jwt
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config

app = FastAPI()
app.mount(path="/static", app=StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger("uvicorn")

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
async def line_login(request: Request):
    random_state = "random_state"
    channel_id = config.LINE_CHANNEL_ID
    redirect_url = f"{get_host_url(request)}{config.ENDPOINT_AUTH}"
    location = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={channel_id}&redirect_uri={redirect_url}&state={random_state}&scope=openid%20profile"

    context = {
        "request": request,
        "title": config.APP_TITLE,
        "location": location,
    }
    return templates.TemplateResponse("login.html", context)


@app.get(config.ENDPOINT_AUTH, response_class=HTMLResponse)
async def authentication(request: Request):
    request_code = request.query_params.get("code")
    channel_id = config.LINE_CHANNEL_ID
    client_secret = config.LINE_CHANNEL_SECRET
    redirect_url = f"{get_host_url(request)}{config.ENDPOINT_AUTH}"

    # ref https://developers.line.biz/ja/reference/line-login/
    uri_access_token = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data_params = {
        "grant_type": "authorization_code",
        "code": request_code,
        "redirect_uri": redirect_url,
        "client_id": channel_id,
        "client_secret": client_secret
    }
    async with httpx.AsyncClient() as client:
        response_post = await client.post(uri_access_token, headers=headers, data=data_params)

    token_response = response_post.json()
    # dict_keys(['access_token', 'token_type', 'refresh_token', 'expires_in', 'scope', 'id_token'])

    # 今回は"id_token"のみを使用する
    line_id_token = token_response["id_token"]

    # ここからおまけ。id_tokenからプロフィールを取得する
    channel_id = config.LINE_CHANNEL_ID
    # ペイロード部分をデコードすることで、ユーザ情報を取得する
    decoded_id_token = jwt.decode(line_id_token,
                                  client_secret,
                                  audience=channel_id,
                                  issuer='https://access.line.me',
                                  algorithms=['HS256'])
    print(decoded_id_token)
    # aud .. 認証日
    # exp .. トークン期限切れ時間 (iat + 1h)
    # iat .. トークン取得時間
    # sub .. ユーザーID U123...
    # name, picture

    # end of ここからおまけ

    context = {
        "request": request,
        "title": config.APP_TITLE,
        "name": "Auth!",
        "debug": json.dumps({
            "token_response": token_response,
            "decoded_id_token": decoded_id_token
        }, indent=2, ensure_ascii=False),
    }
    return templates.TemplateResponse("index.html", context)

logger.info(f"Valid endpoints: [{config.ENDPOINT_LOGIN}, {config.ENDPOINT_AUTH}]")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=(not config.PRODUCTION))
