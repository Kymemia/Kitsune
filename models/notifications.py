#!/usr/bin/env python3

"""
this is the notifications model for our platform
"""
# consider sending SMS or strictly stick to in-app notifications and emails
import pytz
import smtplib
import logging
import os
from enum import Enum
from storage import session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

EAT = pytz.timezone('Africa/Nairobi')
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class NotificationModel:
    class NotificationStatus(Enum):
        sent = 'sent'
        DELIVERED = 'delivered'
        READ = 'read'

    class PriorityLevel(Enum):
        HIGH = 'high'
        MEDIUM = 'medium'
        LOW = 'low'

    class DeliveryChannel(Enum):
        EMAIL = 'email'
        IN_APP = 'in_app'

    def __init__(self, user_id, notification_type, content, priority=PriorityLevel.MEDIUM, delivery_channel=DeliveryChannel.IN_APP):
        self.id = None
        self.user_id = user_id
        self.notification_type = notification_type
        self.content = content
        self.timestamp = datetime.now(EAT)
        self.status = self.NotificationStatus.SENT
        self.priority = priority
        self.deliver_channel = delivery_channel

def create_notification(user_id, notification_type, content, priority=NotificationModel.PriorityLevel.MEDIUM, delivery_channel=NotificationModel.DeliveryChannel.IN_APP):
    """
    method definition to create a notification
    """
    notification = NotificationModel(user_id, notification_type, content, priority, deliver_channel)
    session.add(notification)
    session.commit()
    return notification

def send_notification(notification_id):
    """
    method definition to send a notification
    """
    notification = session.query(NotificationModel).get(notification_id)
    if notification:
        if notification.deliver_channel == NotificationModel.DeliveryChannel.IN_APP:

            update_notifications_bell(notification.user_id)
        elif notification.delivery_channel == NotificationModel.DeliveryChannel.EMAIL:
            if notification.priority == NotificationModel.PriorityLevel.HIGH:
                send_email(notification)
                notification.status = NotificationModel.NotificationStatus.DELIVERED
                session.commit()
            else:
                print(f"Notification with ID {notification.id} is not high-priority. Skipping email dleivery.")
        else:
            print(f"Unsupported delivery channel for notification ID {notification.id}")

        notification.status = NotificationModel.NotificationStatus.DELIVERED
        session.commit()

def get_user_details(user_id):
    """
    method definition to retrieve the user's email address
    based on their user ID
    """
    if user_id in email_cache:
        return email_cache[user_id]

    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            email_cache[user_id] = (user.email, user.name)
            return user.email, user.name
        return None, None
    except Exception as e:
        logging.error(f"Error retrieving email for user ID {user_id}: {e}")
        return None, None

def generate_subject(notification):
    """
    helper function to generate a custome subject
    for the email based on the notification type
        *Notifications will be added as the platform grows
    """
    if notification.notification_type == 'task_update':
        return f"Task Update: {notification.content}"
    elif notification.notification_type == 'payment_confirmation':
        return f"Payment Confirmation: {notification.content}"
    elif notification.notification_type == 'task_completed':
        return f"Task Completed: {notification.content}"
    elif notification.notification_type == 'dispute_status':
        return f"Dispute Status: {notification.content}"
    else:
        return "Important Notification"

def send_email(notification):
    """
    method definition to send
    an email notification to the user
    """
    if notification.priority == NotificationModel.PriorityLevel.HIGH:
        email_address = get_user_email(notification.user_id)
        if email_address:
            subject = generate_subject(notification)
            message = f"Dear {user_name}, \n\n{notification.content}\n\nBest regards, \nSupport Team"
            try:
                with smtplib.SMTP('stmp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
                    server.sendmail(os.getenv('MAIL_USERNAME'), email_address, f"Subject: {subject}\n\n{message}")

                print(f"Sending email: {notification.content} to user ID {notification.user_id}")
            except Exception as e:
                logging.error(f"Error sending email to {email_address}: {e}")

        else:
            logging.warning(f"Invalid email address or user name for user ID {notification.user_id}")
    else:
        logging.info(f"Notification priority is not high. No email sent for notification ID {notification.notification_id}")

def update_notifications_bell(user_id):
    """
    method definition that updates a user's notification bell
    """
    notifications = fetch_notifications(user_id)
    for notification in notifications:
        if notification.status == NotificationModel.NotificationStatus.SENT:
            pass

def mark_as_read(notification_id):
    """
    method definition that allows
    a user to mark a notification as read
    """
    notification = session.query(NotificationModel).get(notification_id)
    if notification:
        notification.status = NotificationModel.NotificationStatus.READ
        session.commit()

def fetch_notifications(user_id):
    """
    method definition that gets all notifications for a user
    """
    return session.query(NotificationModel).filter_by(user_id=user_id).all()

def notify_user(user_id, event_trigger, priority=NotificationModel.PriorityLevel.HIGH):
    """
    method definition that notifies a user upon an event trigger occurring
    """
    content = f"Your task has been {event_trigger}"
    notification = create_notification(user_id, 'task_update', content, priority)
    return send_notification(notification.id)

def notification_history(user_id):
    """
    method definition that grants a user
    the option to view their notification history
    """
    return session.query(NotificationModel).filter_by(user_id=user_id).order_by(NotificationModel.timestamp.desc()).all()

def get_notifications_bell(user_id):
    """
    method definition that shows notifications
    under the bell icon
    """
    notifications = fetch_notifications(user_id)
    unread_count = len([x for x in notifications if x.status == NotificationModel.NotificationStatus.SENT])
    return {
            'unread_count': unread_count,
            'notifications': [{
                'notification_id': x.id,
                'content': x.content,
                'status': x.status.value,
                'timestamp': x.timestamp
                } for x in notifications]
            }

def get_messages_icon(user_id):
    """
    method definition that shows messages
    under the messages icon
    """
    messages = fetch_messages(user_id)
    return [{
        'message_id': m.id,
        'content': m.content,
        'status': m.status.value,
        'timestamp': m.timestamp
        } for m in messages]
