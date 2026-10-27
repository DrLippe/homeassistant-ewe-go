"""Cognito SRP authentication and token renewal."""
import asyncio
from pycognito import Cognito
from .const import COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID

def _user(email, **tokens):
    return Cognito(COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID, username=email, **tokens)

def _tokens(user):
    return {"access_token": user.access_token, "id_token": user.id_token, "refresh_token": user.refresh_token}

def _login(email, password):
    user = _user(email)
    user.authenticate(password=password)
    return _tokens(user)

async def login(email, password):
    return await asyncio.to_thread(_login, email, password)

def _renew(email, tokens):
    user = _user(email, **tokens)
    user.check_token()
    result = _tokens(user)
    result["refresh_token"] = result["refresh_token"] or tokens["refresh_token"]
    return result

async def renew(email, tokens):
    return await asyncio.to_thread(_renew, email, tokens)
