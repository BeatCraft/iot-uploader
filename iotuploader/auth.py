import logging
import secrets

from fastapi import FastAPI, Depends, Request, File, UploadFile, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import get_settings

settings = get_settings()
logger = logging.getLogger("gunicorn.error")

REALM = "Tools"
security = HTTPBasic(realm=REALM)

def auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.tools_user)
    correct_password = secrets.compare_digest(credentials.password, settings.tools_pass)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth error",
            headers={"WWW-Authenticate": f"Basic realm={REALM}"}
        )

    return credentials.username


