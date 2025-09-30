# Email Notification Service

A Python service that sends templated emails based on environment variables and publishes events to NATS subjects. This service supports two email templates: welcome emails for new users and marketing notifications for internal teams.

## Features

- **Template-based Email Sending**: Uses Jinja2 templates for dynamic email content
- **Environment Variable Configuration**: All configuration through environment variables
- **NATS Event Publishing**: Publishes events after successful email sending
- **Two Email Templates**:
  - Welcome email for new users
  - Marketing notification for internal teams
- **Professional HTML Templates**: Responsive, modern email designs
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Database Schema Integration

This service integrates with the database schema defined in `database_schema.sql`:

- **Users Table**: Contains user information (name, email, role, company)
- **Corporate Customers Table**: Company information and subscription tiers
- **User Roles Table**: Available roles (customer_account_owner, admin_user, generic_user)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd knapscen-email-notifications
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your actual configuration
   ```

## Quick Start with MailHog (Testing)

For development and testing, you can use MailHog to capture emails without sending them to real recipients:

1. **Start MailHog and NATS**:
   ```bash
   docker-compose up mailhog nats
   ```

2. **Access MailHog Web UI**:
   - Open `http://localhost:8025` in your browser
   - This is where captured emails will appear

3. **Run the email service**:
   ```bash
   # Set environment variables for testing
   export EMAIL_TEMPLATE=welcome
   export USER_NAME="Test User"
   export USER_EMAIL="test@example.com"
   export COMPANY_NAME="Test Company"
   export USER_ROLE="admin_user"
   export SMTP_SERVER=localhost
   export SMTP_PORT=1025
   export SMTP_USER=""
   export SMTP_PASS=""
   export NATS_SERVER=nats://localhost:4222
   export NATS_SUBJECT=email-notifications
   
   python3 email_notification_service.py
   ```

4. **View the email**:
   - Check `http://localhost:8025` to see the captured email
   - You can inspect headers, body, and test the email rendering

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_TEMPLATE` | Template type: 'welcome' or 'marketing' | `welcome` |
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username | `your-email@gmail.com` |
| `SMTP_PASS` | SMTP password/app password | `your-app-password` |
| `NATS_SERVER` | NATS server address | `nats://localhost:4222` |
| `NATS_SUBJECT` | NATS subject for events | `email-notifications` |
| `NATS_USER` | NATS username | `your-nats-username` |
| `NATS_PASSWORD` | NATS password | `your-nats-password` |

### Template-Specific Variables

#### Welcome Template
| Variable | Description | Example |
|----------|-------------|---------|
| `USER_NAME` | User's full name | `John Doe` |
| `USER_EMAIL` | User's email address | `john.doe@company.com` |
| `COMPANY_NAME` | Company name | `Acme Corporation` |
| `USER_ROLE` | User's role in the application | `customer_account_owner` |

#### Marketing Template
| Variable | Description | Example |
|----------|-------------|---------|
| `COMPANY_NAME` | Company name | `Acme Corporation` |
| `MARKETING_TEAM_EMAIL` | Marketing team email | `marketing@knapscen.com` |
| `USERS_JSON` | JSON array of user objects | `[{"name":"John Doe","email":"john.doe@company.com","role":"customer_account_owner"}]` |

## Usage

### Running the Service

```bash
python email_notification_service.py
```

### Example Configurations

#### Welcome Email Example
```bash
export EMAIL_TEMPLATE=welcome
export USER_NAME="Alice Johnson"
export USER_EMAIL="alice.johnson@techcorp.com"
export COMPANY_NAME="TechCorp Solutions"
export USER_ROLE="admin_user"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASS="your-app-password"
export NATS_SERVER="nats://localhost:4222"
export NATS_SUBJECT="email-notifications"
export NATS_USER="your-nats-username"
export NATS_PASSWORD="your-nats-password"

python email_notification_service.py
```

#### Marketing Notification Example
```bash
export EMAIL_TEMPLATE=marketing
export COMPANY_NAME="StartupXYZ Inc."
export MARKETING_TEAM_EMAIL="marketing@knapscen.com"
export USERS_JSON='[{"name":"Alice Brown","email":"alice.brown@startupxyz.com","role":"customer_account_owner"},{"name":"Bob Wilson","email":"bob.wilson@startupxyz.com","role":"generic_user"}]'
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASS="your-app-password"
export NATS_SERVER="nats://localhost:4222"
export NATS_SUBJECT="email-notifications"
export NATS_USER="your-nats-username"
export NATS_PASSWORD="your-nats-password"

python email_notification_service.py
```

## Email Templates

### Welcome Email Template
- Professional, responsive design
- Displays user information in a clean format
- Includes company branding
- Call-to-action button for getting started

### Marketing Notification Template
- Internal team notification format
- Lists all users with their roles and contact information
- Provides statistics about the new company
- Includes action buttons for follow-up activities

## NATS Events

The service publishes events to NATS subjects after successful email sending:

- **Welcome Email**: `welcome-email-sent`
- **Marketing Notification**: `marketing-notified`

Event payload includes all environment variables used during execution.

## Kubernetes Deployment

### MailHog for Testing

Deploy MailHog on Kubernetes for email testing:

```bash
# Simple deployment
kubectl apply -f k8s-mailhog-simple.yaml

# Production deployment with full features
kubectl apply -f k8s-mailhog.yaml
```

Access MailHog:
- **Web UI**: `http://<node-ip>:<nodeport>` (simple) or `http://mailhog.local` (production)
- **SMTP**: `<node-ip>:<nodeport>` (simple) or `mailhog.email-testing.svc.cluster.local:1025` (production)

For detailed MailHog deployment instructions, see [MAILHOG_DEPLOYMENT.md](MAILHOG_DEPLOYMENT.md).

### Email Service on Kubernetes

Deploy the email service to use MailHog:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: email-service
spec:
  template:
    spec:
      containers:
      - name: email-service
        image: your-registry/email-service:latest
        env:
        - name: SMTP_SERVER
          value: "mailhog.email-testing.svc.cluster.local"
        - name: SMTP_PORT
          value: "1025"
        - name: SMTP_USER
          value: ""
        - name: SMTP_PASS
          value: ""
        # ... other environment variables
```

## File Structure

```
knapscen-email-notifications/
├── email_notification_service.py    # Main service script
├── templates/                       # Jinja2 email templates
│   ├── welcome_email.html          # Welcome email template
│   └── marketing_notification.html # Marketing notification template
├── requirements.txt                # Python dependencies
├── env.example                     # Environment configuration example
├── database_schema.sql            # Database schema reference
├── k8s-mailhog.yaml              # Production MailHog Kubernetes manifest
├── k8s-mailhog-simple.yaml       # Simple MailHog Kubernetes manifest
├── MAILHOG_DEPLOYMENT.md         # MailHog deployment guide
├── docker-compose.yml            # Docker Compose with MailHog
├── Dockerfile                    # Container image
├── test_service.py              # Test suite
├── run_service.sh               # Service runner script
└── README.md                    # This file
```

## Dependencies

- **Jinja2**: Template engine for dynamic email content
- **nats-py**: NATS client for event publishing
- **smtplib**: Built-in Python library for SMTP email sending
- **email**: Built-in Python library for email message handling

## Error Handling

The service includes comprehensive error handling:

- Environment variable validation
- SMTP connection and authentication errors
- NATS connection and publishing errors
- Template rendering errors
- JSON parsing errors for user data

## Logging

The service provides detailed logging at INFO level:

- Service startup and configuration
- Email sending status
- NATS event publishing status
- Error messages with context

## Security Considerations

- Use app passwords for Gmail instead of regular passwords
- Store sensitive environment variables securely
- Validate all input data before processing
- Use TLS for SMTP connections

## Troubleshooting

### Common Issues

1. **SMTP Authentication Failed**
   - Verify SMTP credentials
   - Use app passwords for Gmail
   - Check SMTP server settings

2. **NATS Connection Failed**
   - Verify NATS server is running
   - Check NATS server address and port
   - Ensure network connectivity

3. **Template Rendering Error**
   - Verify all required environment variables are set
   - Check JSON format for USERS_JSON
   - Validate template syntax

4. **Email Not Received**
   - Check spam/junk folders
   - Verify recipient email address
   - Check SMTP server logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.