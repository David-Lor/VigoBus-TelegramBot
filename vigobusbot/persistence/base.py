import abc

from vigobusbot.utils import Type, T


class BaseRepository(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def get_repository(cls: Type[T]) -> Type[T]:
        raise NotImplementedError
