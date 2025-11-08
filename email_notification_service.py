#!/usr/bin/env python3
"""
Email Notification Service

This service sends emails based on templates and environment variables,
then publishes events to NATS subjects.

Templates:
- welcome: Sends welcome email to new users
- marketing: Notifies internal marketing team of new company onboarding

Environment Variables Required:
- EMAIL_TEMPLATE: 'welcome' or 'marketing'
- SMTP_SERVER: SMTP server address
- SMTP_PORT: SMTP server port (default: 587)
- SMTP_USER: SMTP username
- SMTP_PASS: SMTP password
- NATS_SERVER: NATS server address
- NATS_SUBJECT: NATS subject for events

For welcome template:
- USER_NAME: User's name
- USER_EMAIL: User's email address
- COMPANY_NAME: Company name
- USER_ROLE: User's role in the application

For marketing template:
- COMPANY_NAME: Company name
- MARKETING_TEAM_EMAIL: Marketing team email address
- USERS_JSON: JSON string containing user data
"""

import os
import json
import smtplib
import asyncio
import logging
import hashlib
import uuid
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
import nats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service for sending templated emails and publishing NATS events."""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.nats_server = os.getenv('NATS_SERVER')
        self.nats_subject = os.getenv('NATS_SUBJECT')
        self.nats_user = os.getenv('NATS_USER')
        self.nats_password = os.getenv('NATS_PASSWORD')
        
        # Validate required environment variables
        self._validate_env_vars()
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader('templates'))
    
    def _validate_env_vars(self):
        """Validate that all required environment variables are set."""
        required_vars = [
            'EMAIL_TEMPLATE', 'SMTP_SERVER', 'SMTP_USER', 'SMTP_PASS',
            'NATS_SERVER', 'NATS_SUBJECT', 'NATS_USER', 'NATS_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def _get_template_context(self, template_type: str) -> Dict[str, Any]:
        """Get template context based on template type."""
        if template_type == 'welcome':
            return {
                'user_name': os.getenv('USER_NAME'),
                'user_email': os.getenv('USER_EMAIL'),
                'company_name': os.getenv('COMPANY_NAME'),
                'user_role': os.getenv('USER_ROLE')
            }
        elif template_type == 'marketing':        
            return {
                'company_name': os.getenv('COMPANY_NAME'),
                'marketing_team_email': os.getenv('MARKETING_TEAM_EMAIL'),
                'subscription_tier': os.getenv('SUBSCRIPTION_TIER'),
                'next_actions': os.getenv('NEXT_ACTIONS')
            }
        else:
            raise ValueError(f"Unknown template type: {template_type}")
    
    def _get_template_filename(self, template_type: str) -> str:
        """Get template filename based on template type."""
        template_map = {
            'welcome': 'welcome_email.html',
            'marketing': 'marketing_notification.html'
        }
        return template_map.get(template_type, f'{template_type}_email.html')
    
    def _get_email_subject(self, template_type: str) -> str:
        """Get email subject based on template type."""
        subject_map = {
            'welcome': 'Welcome to Knapscen!',
            'marketing': 'New Company Onboarded - Marketing Notification'
        }
        return subject_map.get(template_type, 'Notification')
    
    def _get_recipient_email(self, template_type: str) -> str:
        """Get recipient email based on template type."""
        if template_type == 'welcome':
            return os.getenv('USER_EMAIL')
        elif template_type == 'marketing':
            return os.getenv('MARKETING_TEAM_EMAIL')
        else:
            raise ValueError(f"Unknown template type: {template_type}")
      
    def send_email(self, template_type: str) -> bool:
        """Send email based on template type."""
        try:
            # Get template context and configuration
            context = self._get_template_context(template_type)
            template_filename = self._get_template_filename(template_type)
            subject = self._get_email_subject(template_type)
            recipient = self._get_recipient_email(template_type)
            
            # Load and render template
            template = self.jinja_env.get_template(template_filename)
            html_content = template.render(**context)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient} using {template_type} template")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _generate_cloud_event(self, template_type: str) -> Dict[str, Any]:
        """Generate a CloudEvents-compliant event payload."""
        # Get template-specific data
        context = self._get_template_context(template_type)
        
        # Generate event type based on template
        event_type_map = {
            'welcome': 'disco.knapscen.email.welcome.sent',
            'marketing': 'disco.knapscen.email.marketing.notified'
        }
        event_type = event_type_map.get(template_type, f'disco.knapscen.email.{template_type}.sent')
        
        ceSubject = ""

        if template_type == 'welcome':
            user_email = context.get('user_email') or context.get('marketing_team_email', 'unknown@example.com')
            email_hash = hashlib.sha256(user_email.encode()).hexdigest()
            ceSubject = f"welcome-email-sent-{email_hash[:8]}"
        elif template_type == 'marketing':
            customer_name = context.get('company_name')
            customer_hash = hashlib.sha256(customer_name.encode()).hexdigest()
            ceSubject = f"marketing-email-sent-{customer_hash[:8]}"
        # Generate ID and subject from user email hash
        
        # Generate unique event ID
        event_id = f"evt-email-{ceSubject[:8]}"
        
        # Current timestamp in ISO format
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Prepare data payload based on template type
        if template_type == 'welcome':
            data = {
                'customer_name': context.get('company_name'),
                'user_name': context.get('user_name'),
                'user_email': context.get('user_email'),
                'user_role': context.get('user_role')
            }
        elif template_type == 'marketing':
            data = {
                'customer_name': context.get('company_name'),
                'marketing_team_email': context.get('marketing_team_email')
            }
        else:
            data = {
                'template_type': template_type,
                'customer_name': context.get('company_name'),
                'user_email': context.get('user_email'),
                'user_name': context.get('user_name')
            }
        
        # Create CloudEvents payload
        cloud_event = {
            'specversion': '1.0',
            'type': event_type,
            'source': 'knapscen.disco',
            'subject': ceSubject,
            'id': event_id,
            'time': current_time,
            'datacontenttype': 'application/json',
            'data': data
        }
        
        return cloud_event

    async def publish_nats_event(self, template_type: str) -> bool:
        """Publish CloudEvents-compliant event to NATS subject."""
        try:
            # Generate CloudEvents payload
            event_data = self._generate_cloud_event(template_type)
            
            # Connect to NATS and publish event
            nc = await nats.connect(servers=[self.nats_server], user=self.nats_user, password=self.nats_password)
            event_subject = os.getenv('NATS_SUBJECT')
            
            await nc.publish(event_subject, json.dumps(event_data).encode())
            await nc.close()
            
            logger.info(f"NATS event published to subject: {event_subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish NATS event: {e}")
            return False
    
    async def process_notification(self) -> bool:
        """Process email notification based on environment variables."""
        template_type = os.getenv('EMAIL_TEMPLATE')
        
        if not template_type:
            logger.error("EMAIL_TEMPLATE environment variable not set")
            return False
        
        logger.info(f"Processing {template_type} email notification")
        
        # Send email
        email_success = self.send_email(template_type)
        if not email_success:
            return False
        
        # Publish NATS event
        event_success = await self.publish_nats_event(template_type)
        if not event_success:
            logger.warning("Email sent but failed to publish NATS event")
        
        return email_success and event_success


async def main():
    """Main function to run the email notification service."""
    try:
        service = EmailNotificationService()
        success = await service.process_notification()
        
        if success:
            logger.info("Email notification service completed successfully")
            exit(0)
        else:
            logger.error("Email notification service failed")
            exit(1)
            
    except Exception as e:
        logger.error(f"Service failed with error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
