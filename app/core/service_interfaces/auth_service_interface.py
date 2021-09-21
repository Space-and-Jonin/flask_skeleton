import abc


class AuthServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            (hasattr(subclass, "get_token"))
            and callable(subclass.get_token)
            and hasattr(subclass, "refresh_token")
            and callable(subclass.refresh_token)
            and hasattr(subclass, "create_user")
            and callable(subclass.create_user)
        )

    @abc.abstractmethod
    def get_token(self, request_data):
        """

        :param request_data: authentication data needed to retrieve valid token
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def refresh_token(self, refresh_token):
        """

        :param refresh_token: refresh token needed to get the next valid token
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_user(self, data):
        """

        :param data: data to create user with
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def reset_password(self, param):
        raise NotImplementedError
