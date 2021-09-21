import abc


class NotificationHandler(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "send")) and callable(subclass.send)

    @abc.abstractmethod
    def send(self):
        raise NotImplementedError
