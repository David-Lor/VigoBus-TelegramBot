import abc

import tenacity
import aiocouch

from vigobusbot.utils import Type, T

__all__ = ["BaseRepository", "BaseCouchDBRepository"]


class BaseRepository(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def get_repository(cls: Type[T]) -> Type[T]:
        """Returns one usable class of this repository, based on the persistence backend enabled in telegram_settings.
        """
        raise NotImplementedError


# noinspection bad-argument-type
class BaseCouchDBRepository(abc.ABC):
    _conflict_retry = tenacity.retry_if_exception_type(aiocouch.exception.ConflictError)
    _retry_stop = tenacity.stop_after_attempt(5)
