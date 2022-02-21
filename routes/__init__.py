from fastapi import APIRouter, Depends

import crud
import database
import external
from .v1 import v1router

__all__ = ['v1router']


