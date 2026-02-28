# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Addison Kline

from fastapi import Response
from pydantic import BaseModel


class GetRootResponse(BaseModel):
    """
    HTTP response body for `GET /`.
    """
    name: str
    version: str
    status: str
