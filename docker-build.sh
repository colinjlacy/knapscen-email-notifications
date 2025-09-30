#!/bin/bash

# Docker Build Script for Email Notification Service
# This script builds the Docker image locally for testing

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

# Default values
IMAGE_NAME="knapscen-email-notifications"
TAG="latest"
PLATFORM="linux/amd64"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -t, --tag TAG        Docker image tag (default: latest)"
            echo "  -p, --platform PLATFORM  Target platform (default: linux/amd64)"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Build with default settings"
            echo "  $0 -t v1.0.0                # Build with specific tag"
            echo "  $0 -p linux/arm64            # Build for ARM64"
            echo "  $0 -t dev -p linux/amd64,linux/arm64  # Multi-platform build"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

print_status "Building Docker image: $IMAGE_NAME:$TAG"
print_status "Platform: $PLATFORM"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if buildx is available
if ! docker buildx version >/dev/null 2>&1; then
    print_warning "Docker Buildx not available. Using regular docker build."
    print_status "Building image..."
    docker build -t "$IMAGE_NAME:$TAG" .
else
    print_status "Using Docker Buildx for multi-platform support..."
    
    # Create and use buildx builder if it doesn't exist
    if ! docker buildx inspect email-builder >/dev/null 2>&1; then
        print_status "Creating buildx builder..."
        docker buildx create --name email-builder --use
    else
        print_status "Using existing buildx builder..."
        docker buildx use email-builder
    fi
    
    # Build the image
    print_status "Building image..."
    docker buildx build \
        --platform "$PLATFORM" \
        --tag "$IMAGE_NAME:$TAG" \
        --load \
        .
fi

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully: $IMAGE_NAME:$TAG"
    
    # Show image information
    print_status "Image details:"
    docker images "$IMAGE_NAME:$TAG"
    
    print_status "To run the container:"
    echo "docker run --rm -it $IMAGE_NAME:$TAG"
    
    print_status "To test with environment variables:"
    echo "docker run --rm -it \\"
    echo "  -e EMAIL_TEMPLATE=welcome \\"
    echo "  -e USER_NAME='Test User' \\"
    echo "  -e USER_EMAIL='test@example.com' \\"
    echo "  -e COMPANY_NAME='Test Company' \\"
    echo "  -e USER_ROLE='admin_user' \\"
    echo "  -e SMTP_SERVER=mailhog \\"
    echo "  -e SMTP_PORT=1025 \\"
    echo "  -e SMTP_USER='' \\"
    echo "  -e SMTP_PASS='' \\"
    echo "  -e NATS_SERVER=nats://nats:4222 \\"
    echo "  -e NATS_SUBJECT=email-notifications \\"
    echo "  -e NATS_USER=test \\"
    echo "  -e NATS_PASSWORD=test \\"
    echo "  $IMAGE_NAME:$TAG"
else
    print_error "Docker build failed"
    exit 1
fi
