from blinker import Namespace

from app.core.notification_handler import NotificationHandler


class Notifier:
    notification_signals = Namespace()
    signal = notification_signals.signal("notify")

    def notify(self, notification_listener: NotificationHandler):
        self.signal.send(self, notification=notification_listener)

    @signal.connect
    def send_notification(self, **kwargs):
        notification = kwargs["notification"]
        notification.send()
