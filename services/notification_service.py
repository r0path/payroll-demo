import logging

class NotificationService:
    def __init__(self):
        self.logger = logging.getLogger('notifications')
    
    def send_email(self, to, subject, body):
        """Send email notification (safe implementation)"""
        self.logger.info(f"Sending email to {to}: {subject}")
        return {'status': 'sent', 'to': to}
    
    def send_slack(self, channel, message):
        """Send slack notification (safe implementation)"""
        self.logger.info(f"Sending slack to {channel}")
        return {'status': 'sent', 'channel': channel}
