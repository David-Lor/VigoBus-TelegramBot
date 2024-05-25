import abc

from vigobusbot.utils import Type, T

__all__ = ["BaseRepository"]


class BaseRepository(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def get_repository(cls: Type[T]) -> Type[T]:
        """Returns one usable class of this repository, based on the persistence backend enabled in telegram_settings.
        """
        raise NotImplementedError
