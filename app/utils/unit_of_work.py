from ..database import get_session
from fastapi import Depends


class UnitOfWork:
    def __init__(self, session=Depends(get_session)):
        self.session = session

    async def commit(self):
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def rollback(self):
        await self.session.rollback()