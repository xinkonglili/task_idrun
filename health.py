#import logging
import os

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse


#log = logging.getLogger(__name__)

router = APIRouter()
#app_name = os.environ.get("APP_NAME", "task-idrun")

app_name = "task-idrun"


@router.get("/health")
def health(request: Request):
    #log.info(f"health! client:{request.client}")
    return JSONResponse(content={"health": True})


@router.get(f"/{app_name}/healthcheck")
def healthcheck(request: Request):
    #log.info(f"healthcheck! client:{request.client}")
    # https://notes.dingtalk.com/doc/Y7kmblNWEMZnqzLq
    return JSONResponse(content={"ret": 200, "data": None, "msg": "ok"})
