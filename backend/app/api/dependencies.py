from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends

from ..core.db import get_session

# * Asyn database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]
