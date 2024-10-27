# LineLoginMicroService

## Setup

### build image


```sh
docker compose build
```

### Initialize database


```sh
sh setup_pocketbase.sh
```

## Serve


```sh
docker compose up
```


## Flow diagram

```mermaid

sequenceDiagram
  actor user as User
  participant app as Your App
  participant llms as LineLoginMicroService
  participant line as LINE

  %% 初回閲覧
  Note right of user: First Time Login

  user ->>+ app: Open First Time

  app ->> app: no session
  app -->>- user: 307 redirect to `LineLoginMicroService/login`
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

  %% 2回目以降
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
