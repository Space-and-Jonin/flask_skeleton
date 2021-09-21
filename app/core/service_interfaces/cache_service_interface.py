import abc


class CacheServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            (hasattr(subclass, "set"))
            and callable(subclass.set)
            and hasattr(subclass, "get")
            and callable(subclass.get)
        )

    @abc.abstractmethod
    def set(self, name, data):
        """

        :param name: key of redis object that should be saved
        :param data: the data of that should be saved
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, name):
        """

        :param name: key of object that should be retrieved
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, name):
        """

        :param name: key of object that should be deleted
        :return:
        """
        raise NotImplementedError
