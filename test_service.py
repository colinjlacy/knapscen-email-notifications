#!/usr/bin/env python3
"""
Test script for the Email Notification Service

This script provides example configurations and test scenarios
for the email notification service.
"""

import os
import json
import subprocess
import sys
from typing import Dict, Any


def set_env_vars(env_vars: Dict[str, str]) -> None:
    """Set environment variables for testing."""
    for key, value in env_vars.items():
        os.environ[key] = value


def test_welcome_email():
    """Test the welcome email template."""
    print("🧪 Testing Welcome Email Template...")
    
    env_vars = {
        'EMAIL_TEMPLATE': 'welcome',
        'USER_NAME': 'Alice Johnson',
        'USER_EMAIL': 'alice.johnson@techcorp.com',
        'COMPANY_NAME': 'TechCorp Solutions',
        'USER_ROLE': 'admin_user',
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASS': 'test-password',
        'NATS_SERVER': 'nats://localhost:4222',
        'NATS_SUBJECT': 'email-notifications',
        'NATS_USER': 'test-user',
        'NATS_PASSWORD': 'test-password'
    }
    
    set_env_vars(env_vars)
    
    try:
        # Import and test the service
        from email_notification_service import EmailNotificationService
        
        service = EmailNotificationService()
        context = service._get_template_context('welcome')
        template_filename = service._get_template_filename('welcome')
        subject = service._get_email_subject('welcome')
        recipient = service._get_recipient_email('welcome')
        nats_subject = service._get_nats_event_subject('welcome')
        
        print(f"✅ Template context: {context}")
        print(f"✅ Template filename: {template_filename}")
        print(f"✅ Email subject: {subject}")
        print(f"✅ Recipient: {recipient}")
        print(f"✅ NATS subject: {nats_subject}")
        
        # Test template rendering (without sending email)
        template = service.jinja_env.get_template(template_filename)
        html_content = template.render(**context)
        
        print(f"✅ Template rendered successfully ({len(html_content)} characters)")
        
    except Exception as e:
        print(f"❌ Welcome email test failed: {e}")
        return False
    
    return True


def test_marketing_notification():
    """Test the marketing notification template."""
    print("\n🧪 Testing Marketing Notification Template...")
    
    users_data = [
        {"name": "Alice Brown", "email": "alice.brown@startupxyz.com", "role": "customer_account_owner"},
        {"name": "Bob Wilson", "email": "bob.wilson@startupxyz.com", "role": "admin_user"},
        {"name": "Carol Davis", "email": "carol.davis@startupxyz.com", "role": "generic_user"}
    ]
    
    env_vars = {
        'EMAIL_TEMPLATE': 'marketing',
        'COMPANY_NAME': 'StartupXYZ Inc.',
        'MARKETING_TEAM_EMAIL': 'marketing@knapscen.com',
        'USERS_JSON': json.dumps(users_data),
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASS': 'test-password',
        'NATS_SERVER': 'nats://localhost:4222',
        'NATS_SUBJECT': 'email-notifications',
        'NATS_USER': 'test-user',
        'NATS_PASSWORD': 'test-password'
    }
    
    set_env_vars(env_vars)
    
    try:
        from email_notification_service import EmailNotificationService
        
        service = EmailNotificationService()
        context = service._get_template_context('marketing')
        template_filename = service._get_template_filename('marketing')
        subject = service._get_email_subject('marketing')
        recipient = service._get_recipient_email('marketing')
        nats_subject = service._get_nats_event_subject('marketing')
        
        print(f"✅ Template context: {context}")
        print(f"✅ Template filename: {template_filename}")
        print(f"✅ Email subject: {subject}")
        print(f"✅ Recipient: {recipient}")
        print(f"✅ NATS subject: {nats_subject}")
        
        # Test template rendering (without sending email)
        template = service.jinja_env.get_template(template_filename)
        html_content = template.render(**context)
        
        print(f"✅ Template rendered successfully ({len(html_content)} characters)")
        
    except Exception as e:
        print(f"❌ Marketing notification test failed: {e}")
        return False
    
    return True


def test_environment_validation():
    """Test environment variable validation."""
    print("\n🧪 Testing Environment Variable Validation...")
    
    # Test missing required variables
    required_vars = ['EMAIL_TEMPLATE', 'SMTP_SERVER', 'SMTP_USER', 'SMTP_PASS', 'NATS_SERVER', 'NATS_SUBJECT', 'NATS_USER', 'NATS_PASSWORD']
    
    for var in required_vars:
        # Clear the variable
        if var in os.environ:
            del os.environ[var]
        
        try:
            from email_notification_service import EmailNotificationService
            service = EmailNotificationService()
            print(f"❌ Should have failed with missing {var}")
            return False
        except ValueError as e:
            if var in str(e):
                print(f"✅ Correctly caught missing {var}")
            else:
                print(f"❌ Wrong error message for missing {var}: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error for missing {var}: {e}")
            return False
    
    return True


def test_invalid_template():
    """Test invalid template type."""
    print("\n🧪 Testing Invalid Template Type...")
    
    env_vars = {
        'EMAIL_TEMPLATE': 'invalid_template',
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASS': 'test-password',
        'NATS_SERVER': 'nats://localhost:4222',
        'NATS_SUBJECT': 'email-notifications',
        'NATS_USER': 'test-user',
        'NATS_PASSWORD': 'test-password'
    }
    
    set_env_vars(env_vars)
    
    try:
        from email_notification_service import EmailNotificationService
        
        service = EmailNotificationService()
        context = service._get_template_context('invalid_template')
        print(f"❌ Should have failed with invalid template type")
        return False
    except ValueError as e:
        if 'Unknown template type' in str(e):
            print(f"✅ Correctly caught invalid template type")
            return True
        else:
            print(f"❌ Wrong error message for invalid template: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error for invalid template: {e}")
        return False


def run_all_tests():
    """Run all test scenarios."""
    print("🚀 Starting Email Notification Service Tests\n")
    
    tests = [
        test_environment_validation,
        test_welcome_email,
        test_marketing_notification,
        test_invalid_template
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
