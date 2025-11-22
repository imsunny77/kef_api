# Deployment Guide

This guide explains how to deploy the KEF API Django application to a production server using Nginx and Gunicorn on Ubuntu.

## Prerequisites

- Ubuntu 20.04 or later
- Python 3.8 or later
- PostgreSQL (or MySQL) database
- Nginx web server
- Root or sudo access

## Step 1: Server Setup

### Install System Packages

```bash
sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx
```

### Create Project User (Optional but Recommended)

```bash
sudo adduser --disabled-password --gecos "" kefuser
```

## Step 2: Database Setup

### Create PostgreSQL Database and User

```bash
sudo -u postgres psql
```

In PostgreSQL prompt:

```sql
CREATE DATABASE kef_api_db;
CREATE USER kefuser WITH PASSWORD 'your_secure_password';
ALTER ROLE kefuser SET client_encoding TO 'utf8';
ALTER ROLE kefuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE kefuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE kef_api_db TO kefuser;
GRANT ALL ON SCHEMA public TO kefuser;
\q
```

## Step 3: Clone and Setup Project

### Clone Repository

```bash
cd /var/www  # or your preferred directory
sudo git clone https://github.com/imsunny77/kef_api.git
sudo chown -R kefuser:kefuser /var/www/kef_api
cd /var/www/kef_api
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Environment Variables

### Create .env File

```bash
cp example-env .env
nano .env
```

Update the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your_domain.com,www.your_domain.com,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=kef_api_db
DB_USER=kefuser
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

**Important**: Generate a secure SECRET_KEY:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Step 5: Database Migrations

```bash
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

## Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This will create a `staticfiles/` directory with all static files.

## Step 7: Test Gunicorn

Test that Gunicorn can serve your application:

```bash
cd /var/www/kef_api
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 kef_api.wsgi:application
```

Visit `http://your_server_ip:8000` in your browser. If you see your application, press Ctrl+C to stop Gunicorn.

## Step 8: Configure Gunicorn Systemd Service

### Update Service File

Edit `systemd/gunicorn.service` and replace all `/path/to/kef_api` with your actual project path (e.g., `/var/www/kef_api`):

```bash
sudo nano systemd/gunicorn.service
```

Update:
- `WorkingDirectory=/var/www/kef_api`
- `ExecStart=/var/www/kef_api/venv/bin/gunicorn`
- `Environment="PATH=/var/www/kef_api/venv/bin"`
- `EnvironmentFile=/var/www/kef_api/.env`

### Install Service Files

```bash
sudo cp systemd/gunicorn.service /etc/systemd/system/
sudo cp systemd/gunicorn.socket /etc/systemd/system/
```

### Start and Enable Services

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### Check Status

```bash
sudo systemctl status gunicorn
sudo systemctl status gunicorn.socket
```

### Verify Socket

```bash
sudo systemctl status gunicorn.socket
file /run/gunicorn.sock
```

## Step 9: Configure Nginx

### Update Nginx Configuration

Edit `nginx/nginx.conf` and replace:
- `your_domain.com` with your actual domain
- `/path/to/kef_api/staticfiles/` with `/var/www/kef_api/staticfiles/`
- `/path/to/kef_api/media/` with `/var/www/kef_api/media/` (if using media files)

### Install Nginx Configuration

```bash
sudo cp nginx/nginx.conf /etc/nginx/sites-available/kef_api
sudo ln -s /etc/nginx/sites-available/kef_api /etc/nginx/sites-enabled/
```

### Test Nginx Configuration

```bash
sudo nginx -t
```

### Restart Nginx

```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

## Step 10: Set Proper Permissions

### Static Files Permissions

```bash
sudo chown -R www-data:www-data /var/www/kef_api/staticfiles/
sudo chmod -R 755 /var/www/kef_api/staticfiles/
sudo chmod 755 /var/www/kef_api/
```

### Project Directory Permissions

```bash
sudo chown -R kefuser:www-data /var/www/kef_api
sudo chmod -R 755 /var/www/kef_api
```

## Step 11: Firewall Configuration

If using UFW firewall:

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

## Step 12: Testing

### Test Application

1. Visit `http://your_domain.com/api/v1/products/` in your browser
2. Check API endpoints are accessible
3. Test authentication endpoints
4. Verify static files are being served

### Check Logs

```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx logs
sudo tail -f /var/log/nginx/kef_api_access.log
sudo tail -f /var/log/nginx/kef_api_error.log

# Django logs (if configured)
tail -f /var/www/kef_api/logs/django.log
```

## Troubleshooting

### Gunicorn Service Issues

**Service won't start:**
```bash
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50
```

**Socket not found:**
```bash
sudo systemctl restart gunicorn.socket
sudo systemctl status gunicorn.socket
```

**Permission denied:**
- Check file permissions on project directory
- Verify user in gunicorn.service matches project owner
- Ensure socket directory has correct permissions

### Nginx Issues

**502 Bad Gateway:**
- Check Gunicorn is running: `sudo systemctl status gunicorn`
- Verify socket exists: `file /run/gunicorn.sock`
- Check Nginx error log: `sudo tail -f /var/log/nginx/kef_api_error.log`

**Static files not loading:**
- Verify STATIC_ROOT is set correctly
- Run `python manage.py collectstatic` again
- Check file permissions on staticfiles directory
- Verify nginx.conf has correct path to staticfiles

**403 Forbidden:**
- Check directory permissions
- Verify nginx user (www-data) has read access
- Check SELinux/AppArmor if enabled

### Database Connection Issues

```bash
# Test PostgreSQL connection
sudo -u postgres psql -d kef_api_db -U kefuser

# Check Django database connection
python manage.py dbshell
```

### Environment Variables Not Loading

- Verify .env file exists and has correct path in gunicorn.service
- Check file permissions on .env file
- Ensure EnvironmentFile path is correct in service file

## Maintenance

### Update Application

```bash
cd /var/www/kef_api
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Backup Database

```bash
sudo -u postgres pg_dump kef_api_db > backup_$(date +%Y%m%d).sql
```

### Monitor Services

```bash
# Check all services
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

## Security Considerations

1. **Keep DEBUG=False** in production
2. **Use strong SECRET_KEY**
3. **Set proper ALLOWED_HOSTS**
4. **Use HTTPS** (configure SSL certificates with Let's Encrypt)
5. **Regular security updates**: `sudo apt update && sudo apt upgrade`
6. **Firewall configuration**: Only allow necessary ports
7. **Database security**: Use strong passwords, limit access

## SSL/HTTPS Setup (Recommended)

Install Certbot for Let's Encrypt SSL:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

Certbot will automatically configure Nginx for HTTPS.

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [DigitalOcean Django Deployment Tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu)

