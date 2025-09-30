# MailHog Kubernetes Deployment Guide

This guide provides comprehensive instructions for deploying MailHog on Kubernetes for email testing and development purposes.

## Overview

MailHog is a web and API based SMTP testing tool that captures emails sent by your application during development. It provides a web interface to view captured emails without actually sending them to real recipients.

## Deployment Options

### 1. Simple Deployment

For quick testing and development:

```bash
kubectl apply -f k8s-mailhog-simple.yaml
```

This creates:
- MailHog deployment with 1 replica
- Service with NodePort access
- Basic resource limits

### 2. Production-Ready Deployment

For more comprehensive setup with security and monitoring:

```bash
kubectl apply -f k8s-mailhog.yaml
```

This creates:
- Dedicated namespace (`email-testing`)
- MailHog deployment with health checks
- Service with ClusterIP access
- Ingress for external access
- ConfigMap for configuration
- NetworkPolicy for security
- ServiceAccount for RBAC

## Accessing MailHog

### After Simple Deployment

1. **Get the NodePort**:
   ```bash
   kubectl get services mailhog
   ```

2. **Access the web interface**:
   - Web UI: `http://<node-ip>:<nodeport-8025>`
   - SMTP: `<node-ip>:<nodeport-1025>`

### After Production Deployment

1. **Access via Ingress** (if ingress controller is available):
   ```bash
   # Add to /etc/hosts
   echo "<ingress-ip> mailhog.local" >> /etc/hosts
   ```
   - Web UI: `http://mailhog.local`

2. **Port Forward for Testing**:
   ```bash
   kubectl port-forward -n email-testing service/mailhog 8025:8025
   kubectl port-forward -n email-testing service/mailhog 1025:1025
   ```
   - Web UI: `http://localhost:8025`
   - SMTP: `localhost:1025`

## Configuration

### Environment Variables

MailHog supports several environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `MH_STORAGE` | `memory` | Storage backend (`memory`, `maildir`, `mongodb`) |
| `MH_MAILDIR_PATH` | `/tmp/maildir` | Path for maildir storage |
| `MH_SMTP_BIND_ADDR` | `0.0.0.0:1025` | SMTP server bind address |
| `MH_UI_BIND_ADDR` | `0.0.0.0:8025` | Web UI bind address |
| `MH_API_BIND_ADDR` | `0.0.0.0:8025` | API bind address |
| `MH_CORS_ORIGIN` | `*` | CORS origin for API |

### Storage Options

1. **Memory Storage** (default):
   - Fast but emails are lost on restart
   - Good for development

2. **Maildir Storage**:
   - Persistent storage
   - Emails survive pod restarts
   - Configured in the production deployment

3. **MongoDB Storage**:
   - For production use
   - Requires MongoDB deployment

## Integration with Email Service

### Docker Compose Integration

The `docker-compose.yml` includes MailHog for local testing:

```bash
# Start MailHog and NATS
docker-compose up mailhog nats

# Run email service with MailHog
EMAIL_TEMPLATE=welcome \
USER_NAME="Test User" \
USER_EMAIL="test@example.com" \
COMPANY_NAME="Test Company" \
USER_ROLE="admin_user" \
SMTP_SERVER=localhost \
SMTP_PORT=1025 \
SMTP_USER="" \
SMTP_PASS="" \
NATS_SERVER=nats://localhost:4222 \
NATS_SUBJECT=email-notifications \
python3 email_notification_service.py
```

### Kubernetes Integration

Update your email service deployment to use MailHog:

```yaml
env:
  - name: SMTP_SERVER
    value: "mailhog.email-testing.svc.cluster.local"
  - name: SMTP_PORT
    value: "1025"
  - name: SMTP_USER
    value: ""  # Not required for MailHog
  - name: SMTP_PASS
    value: ""  # Not required for MailHog
```

## Monitoring and Debugging

### Health Checks

The production deployment includes health checks:

```bash
# Check pod health
kubectl get pods -n email-testing -l app=mailhog

# Check logs
kubectl logs -n email-testing -l app=mailhog
```

### Web Interface Features

1. **Email List**: View all captured emails
2. **Email Details**: Inspect headers, body, and attachments
3. **Search**: Search through captured emails
4. **Download**: Download emails as EML files
5. **API**: REST API for programmatic access

### API Endpoints

- `GET /api/v1/messages` - List all messages
- `GET /api/v1/messages/{id}` - Get specific message
- `DELETE /api/v1/messages` - Clear all messages
- `DELETE /api/v1/messages/{id}` - Delete specific message

## Security Considerations

### Network Policies

The production deployment includes a NetworkPolicy that:
- Restricts ingress to specific namespaces
- Allows access from email service pods
- Permits all egress traffic

### RBAC

ServiceAccount is created for potential RBAC requirements:
```bash
# Create role binding if needed
kubectl create rolebinding mailhog-role-binding \
  --role=mailhog-role \
  --serviceaccount=email-testing:mailhog \
  --namespace=email-testing
```

## Troubleshooting

### Common Issues

1. **Pod Not Starting**:
   ```bash
   kubectl describe pod -n email-testing -l app=mailhog
   kubectl logs -n email-testing -l app=mailhog
   ```

2. **Cannot Access Web UI**:
   - Check service type and ports
   - Verify ingress configuration
   - Try port-forwarding

3. **Emails Not Captured**:
   - Verify SMTP server configuration
   - Check network connectivity
   - Review email service logs

### Logs and Debugging

```bash
# Get detailed pod information
kubectl describe pod -n email-testing -l app=mailhog

# View logs
kubectl logs -n email-testing -l app=mailhog -f

# Check service endpoints
kubectl get endpoints -n email-testing mailhog

# Test SMTP connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside the pod:
telnet mailhog.email-testing.svc.cluster.local 1025
```

## Cleanup

### Remove Simple Deployment
```bash
kubectl delete -f k8s-mailhog-simple.yaml
```

### Remove Production Deployment
```bash
kubectl delete -f k8s-mailhog.yaml
```

### Remove Docker Compose
```bash
docker-compose down -v
```

## References

- [MailHog GitHub Repository](https://github.com/mailhog/MailHog)
- [MailHog Docker Documentation](https://github.com/mailhog/MailHog/blob/master/docs/DEPLOY.md#docker)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
