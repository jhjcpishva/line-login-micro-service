# line-login-micro-service

## Overview

Simple micro-service to provide wrapper for LINE Login service

## Flow

```mermaid

sequenceDiagram
  actor user as User
  participant app as Your App
  participant llms as line-login-micro-service
  participant line as LINE

  %% first visit
  Note right of user: First Time Login

  user ->>+ app: Open First Time

  app ->> app: no session
  app -->>- user: 307 redirect to `line-login-micro-service/login`
  user ->>+ llms: `/login`
  llms ->> llms: Line Login URL
  llms -->>- user: Line Login Page entrance

  user ->>+ line: navigate to line login page
  line -->>- user: 
  user ->>+ line: approve
  line -->>- user: go to `/auth?code...`

  user ->>+ llms: redirect to `/auth?code=...`
  llms ->> llms: get code
  llms ->>+ line: authorize token
  line -->>- llms: access_token, profile, etc...
  llms -->>- user: 307 redirect to `app?success=...`

  user ->>+ app: redirect to `app?success=...`
  app ->>+ llms: call `/api/v1/collect`
  llms -->>- app: session

  app ->>+ llms: GET `/api/v1/sessions/{session}/`
  llms -->>- app: profile
  app -->>- user: login complete. store session

  %% second+ visit
  Note right of user: Revisit
  user ->>+ app: Reopen app

  app ->>+ llms: GET `/api/v1/sessions/{session}/`
  llms -->>- app: session is valid, return profile

  alt `shouldRefreshToken` ?
    app ->>+ llms: POST `api/v1/sessions/{session}/refresh`
    llms ->>+ line: refresh token
    line ->>- llms: new access_token, refresh token
    llms -->>- app: HTTP 204
  end 

  app -->>- user: profile

```

## .env

Reference `env.sample`.

## Documentation

- API documentation is available at `/docs` or `/redoc`.

## Run

### Docker

```sh
docker run \
  -env-file .env \
  -p 8000:8000 \
  -v "./docker/app/db:/db"
  ghcr.io/jhjcpishva/line-login-micro-service:latest
```

### Docker Compose

```sh
docker compose up
```
