from core import NotificationHandler
from app.producer import publish_to_kafka


class SMSNotificationHandler(NotificationHandler):
    """
    SMS Notification handler

    this class handles sms notification. It publishes a NOTIFICATION message to
    the kafka broker which is consumed by the notification service.

    :param recipient: {string} the recipient phone number
    :param message: {string} the message you want to send
    :param sms_type: {string} the type of message you want to send. based on
    the sms type specified, the message may be modified by the notification service.
    Check out https://github.com/theQuantumGroup/nova-be-notification for more info
    """

    def __init__(self, recipient, details, meta):
        self.recipient = recipient
        self.details = details
        self.meta = meta

    def send(self):
        data = {
            "meta": self.meta,
            "details": self.details,
            "recipient": self.recipient,
        }

        publish_to_kafka("SMS_NOTIFICATION", data)
