#!/bin/bash

# Email Notification Service Runner
# This script helps run the email notification service with proper environment setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "email_notification_service.py" ]; then
    print_error "email_notification_service.py not found"
    exit 1
fi

if [ ! -d "templates" ]; then
    print_error "templates directory not found"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Using environment variables from shell."
    print_status "You can create a .env file by copying env.example:"
    print_status "cp env.example .env"
    print_status "Then edit .env with your configuration."
    echo
fi

# Load .env file if it exists
if [ -f ".env" ]; then
    print_status "Loading environment variables from .env file"
    # Use a more robust method to load .env file
    set -a  # automatically export all variables
    source .env
    set +a  # turn off automatic export
fi

# Check required environment variables
required_vars=("EMAIL_TEMPLATE" "SMTP_SERVER" "SMTP_USER" "SMTP_PASS" "NATS_SERVER" "NATS_SUBJECT")

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        print_error "  - $var"
    done
    print_status "Please set these variables or create a .env file"
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "Installing/updating dependencies..."
    pip3 install -r requirements.txt --quiet
fi

# Run the service
print_status "Starting Email Notification Service..."
print_status "Template: $EMAIL_TEMPLATE"
print_status "SMTP Server: $SMTP_SERVER"
print_status "NATS Server: $NATS_SERVER"
echo

python3 email_notification_service.py

if [ $? -eq 0 ]; then
    print_success "Email notification service completed successfully"
else
    print_error "Email notification service failed"
    exit 1
fi
