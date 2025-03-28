from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
import jwt

import config


@dataclass
class AuthResult:
    access_token: str
    refresh_token: str
    user_id: str
    expire: datetime
    name: str
    picture: Optional[str] = None


@dataclass
class TokenRefreshResult:
    access_token: str
    refresh_token: str
    expire: datetime


class MyLineLogin:
    @staticmethod
    def get_line_login_location(redirect_url: str, random_state: str) -> str:
        channel_id = config.LINE_CHANNEL_ID
        location = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={channel_id}&redirect_uri={redirect_url}&state={random_state}&scope=openid%20profile"
        return location

    @staticmethod
    async def authentication(redirect_url: str, code: str) -> AuthResult:
        channel_id = config.LINE_CHANNEL_ID
        client_secret = config.LINE_CHANNEL_SECRET

        # ref https://developers.line.biz/ja/reference/line-login/
        uri_access_token = "https://api.line.me/oauth2/v2.1/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data_params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_url,
            "client_id": channel_id,
            "client_secret": client_secret
        }
        async with httpx.AsyncClient() as client:
            response_post = await client.post(uri_access_token, headers=headers, data=data_params)

        token_response = response_post.json()
        # dict_keys(['access_token', 'token_type', 'refresh_token', 'expires_in', 'scope', 'id_token'])

        decoded_id_token = jwt.decode(token_response["id_token"],
                                      client_secret,
                                      audience=channel_id,
                                      issuer='https://access.line.me',
                                      algorithms=['HS256'],
                                      options={'verify_iat': False})

        return AuthResult(
            access_token=token_response["access_token"],
            refresh_token=token_response["refresh_token"],
            user_id=decoded_id_token["sub"],
            expire=datetime.fromtimestamp(decoded_id_token["exp"], tz=timezone.utc),
            name=decoded_id_token["name"],
            picture=decoded_id_token["picture"] if "picture" in decoded_id_token else None,
        )

    @staticmethod
    async def refresh_token(refresh_token: str) -> TokenRefreshResult:
        channel_id = config.LINE_CHANNEL_ID
        client_secret = config.LINE_CHANNEL_SECRET

        # ref https://developers.line.biz/ja/reference/line-login/
        uri_access_token = "https://api.line.me/oauth2/v2.1/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data_params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": channel_id,
            "client_secret": client_secret
        }
        async with httpx.AsyncClient() as client:
            response_post = await client.post(uri_access_token, headers=headers, data=data_params)

        response = response_post.json()
        # dict_keys(['access_token', 'expires_in', 'refresh_token', 'scope', 'token_type'])

        return TokenRefreshResult(
            access_token=response["access_token"],
            refresh_token=response["refresh_token"],
            expire=datetime.now(tz=timezone.utc) + timedelta(seconds=response["expires_in"]),
        )
