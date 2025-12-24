"""
Reminder Scheduling and Notification System for DEADLINEAI

This module provides functionality for scheduling reminders and sending notifications
for upcoming deadlines. It includes scheduling, notification delivery, and persistence.
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
import json
import uuid


@dataclass
class Reminder:
    """Represents a reminder for a deadline."""
    
    id: str
    deadline_id: str
    title: str
    description: str
    deadline_time: datetime
    reminder_time: datetime
    notification_type: str  # 'email', 'sms', 'push', 'in_app'
    status: str  # 'pending', 'sent', 'dismissed', 'failed'
    created_at: datetime
    updated_at: datetime
    recipient: str  # email or phone number
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.metadata is None:
            self.metadata = {}


class ReminderScheduler:
    """
    Manages reminder scheduling and executes reminders at specified times.
    """
    
    def __init__(self, notification_handler: Optional[Callable] = None):
        """
        Initialize the reminder scheduler.
        
        Args:
            notification_handler: Callable to handle notification dispatch
        """
        self.reminders: Dict[str, Reminder] = {}
        self.notification_handler = notification_handler or self._default_handler
        self.scheduler_thread = None
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
        self._lock = threading.Lock()
    
    def add_reminder(
        self,
        deadline_id: str,
        title: str,
        description: str,
        deadline_time: datetime,
        reminder_time: datetime,
        notification_type: str,
        recipient: str,
        metadata: Optional[Dict] = None
    ) -> Reminder:
        """
        Add a new reminder to the scheduler.
        
        Args:
            deadline_id: ID of the associated deadline
            title: Reminder title
            description: Reminder description
            deadline_time: When the deadline occurs
            reminder_time: When the reminder should be sent
            notification_type: Type of notification (email, sms, push, in_app)
            recipient: Recipient identifier (email/phone)
            metadata: Additional metadata for the reminder
            
        Returns:
            The created Reminder object
        """
        reminder_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        reminder = Reminder(
            id=reminder_id,
            deadline_id=deadline_id,
            title=title,
            description=description,
            deadline_time=deadline_time,
            reminder_time=reminder_time,
            notification_type=notification_type,
            status='pending',
            created_at=now,
            updated_at=now,
            recipient=recipient,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.reminders[reminder_id] = reminder
        
        return reminder
    
    def remove_reminder(self, reminder_id: str) -> bool:
        """
        Remove a reminder from the scheduler.
        
        Args:
            reminder_id: ID of the reminder to remove
            
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if reminder_id in self.reminders:
                del self.reminders[reminder_id]
                return True
        return False
    
    def update_reminder_status(self, reminder_id: str, status: str) -> bool:
        """
        Update the status of a reminder.
        
        Args:
            reminder_id: ID of the reminder
            status: New status (pending, sent, dismissed, failed)
            
        Returns:
            True if updated, False if not found
        """
        with self._lock:
            if reminder_id in self.reminders:
                self.reminders[reminder_id].status = status
                self.reminders[reminder_id].updated_at = datetime.utcnow()
                return True
        return False
    
    def get_reminder(self, reminder_id: str) -> Optional[Reminder]:
        """Get a reminder by ID."""
        with self._lock:
            return self.reminders.get(reminder_id)
    
    def get_pending_reminders(self) -> List[Reminder]:
        """Get all pending reminders."""
        with self._lock:
            return [r for r in self.reminders.values() if r.status == 'pending']
    
    def start(self):
        """Start the reminder scheduler in a background thread."""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True
            )
            self.scheduler_thread.start()
    
    def stop(self):
        """Stop the reminder scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _scheduler_loop(self):
        """Main scheduler loop that checks and dispatches reminders."""
        while self.running:
            try:
                self._check_and_dispatch_reminders()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
    
    def _check_and_dispatch_reminders(self):
        """Check for reminders that should be sent and dispatch them."""
        now = datetime.utcnow()
        pending = self.get_pending_reminders()
        
        for reminder in pending:
            # Check if reminder time has passed
            if reminder.reminder_time <= now:
                try:
                    self.notification_handler(reminder)
                    self.update_reminder_status(reminder.id, 'sent')
                except Exception as e:
                    print(f"Failed to send reminder {reminder.id}: {e}")
                    self.update_reminder_status(reminder.id, 'failed')
    
    @staticmethod
    def _default_handler(reminder: Reminder):
        """Default notification handler (prints to console)."""
        print(f"[{reminder.notification_type.upper()}] {reminder.title}: {reminder.description}")
        print(f"  Recipient: {reminder.recipient}")
        print(f"  Deadline: {reminder.deadline_time}")


class ReminderPersistence:
    """
    Handles persistence of reminders to file storage.
    """
    
    def __init__(self, filepath: str = "reminders.json"):
        """
        Initialize the persistence handler.
        
        Args:
            filepath: Path to store reminders JSON file
        """
        self.filepath = filepath
    
    def save_reminders(self, scheduler: ReminderScheduler) -> bool:
        """
        Save all reminders to file.
        
        Args:
            scheduler: ReminderScheduler instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            reminders_data = []
            for reminder in scheduler.reminders.values():
                data = asdict(reminder)
                # Convert datetime objects to ISO format strings
                data['deadline_time'] = reminder.deadline_time.isoformat()
                data['reminder_time'] = reminder.reminder_time.isoformat()
                data['created_at'] = reminder.created_at.isoformat()
                data['updated_at'] = reminder.updated_at.isoformat()
                reminders_data.append(data)
            
            with open(self.filepath, 'w') as f:
                json.dump(reminders_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving reminders: {e}")
            return False
    
    def load_reminders(self) -> List[Reminder]:
        """
        Load reminders from file.
        
        Returns:
            List of Reminder objects
        """
        try:
            with open(self.filepath, 'r') as f:
                reminders_data = json.load(f)
            
            reminders = []
            for data in reminders_data:
                # Convert ISO format strings back to datetime objects
                data['deadline_time'] = datetime.fromisoformat(data['deadline_time'])
                data['reminder_time'] = datetime.fromisoformat(data['reminder_time'])
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                
                reminder = Reminder(**data)
                reminders.append(reminder)
            
            return reminders
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading reminders: {e}")
            return []


class NotificationManager:
    """
    Manages different notification channels.
    """
    
    def __init__(self):
        """Initialize the notification manager."""
        self.handlers: Dict[str, Callable] = {
            'email': self._send_email,
            'sms': self._send_sms,
            'push': self._send_push,
            'in_app': self._send_in_app
        }
    
    def send_notification(self, reminder: Reminder) -> bool:
        """
        Send a notification via the appropriate channel.
        
        Args:
            reminder: Reminder object containing notification details
            
        Returns:
            True if successful, False otherwise
        """
        handler = self.handlers.get(reminder.notification_type)
        if handler:
            try:
                return handler(reminder)
            except Exception as e:
                print(f"Error sending {reminder.notification_type} notification: {e}")
                return False
        return False
    
    @staticmethod
    def _send_email(reminder: Reminder) -> bool:
        """Send email notification."""
        print(f"Sending email to {reminder.recipient}: {reminder.title}")
        # TODO: Integrate with email service (SMTP, SendGrid, etc.)
        return True
    
    @staticmethod
    def _send_sms(reminder: Reminder) -> bool:
        """Send SMS notification."""
        print(f"Sending SMS to {reminder.recipient}: {reminder.title}")
        # TODO: Integrate with SMS service (Twilio, etc.)
        return True
    
    @staticmethod
    def _send_push(reminder: Reminder) -> bool:
        """Send push notification."""
        print(f"Sending push notification to {reminder.recipient}: {reminder.title}")
        # TODO: Integrate with push notification service (Firebase, etc.)
        return True
    
    @staticmethod
    def _send_in_app(reminder: Reminder) -> bool:
        """Send in-app notification."""
        print(f"Sending in-app notification: {reminder.title}")
        # TODO: Store in database for in-app display
        return True


# Example usage
if __name__ == "__main__":
    # Initialize components
    notification_manager = NotificationManager()
    scheduler = ReminderScheduler(notification_handler=notification_manager.send_notification)
    persistence = ReminderPersistence()
    
    # Add a sample reminder
    now = datetime.utcnow()
    deadline = now + timedelta(days=7)
    reminder_time = deadline - timedelta(hours=1)
    
    reminder = scheduler.add_reminder(
        deadline_id="deadline_001",
        title="Project Submission",
        description="Submit the final project report",
        deadline_time=deadline,
        reminder_time=reminder_time,
        notification_type="email",
        recipient="user@example.com",
        metadata={"priority": "high", "project": "DEADLINEAI"}
    )
    
    print(f"Reminder created: {reminder.id}")
    print(f"Status: {reminder.status}")
    
    # Start the scheduler
    scheduler.start()
    
    # Save reminders
    persistence.save_reminders(scheduler)
    
    # Keep running for demonstration
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("Scheduler stopped")
