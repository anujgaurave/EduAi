# Deployment Guide - Production Setup

This guide covers deploying EduAI to production environments.

---

## 🔧 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] No console errors in development
- [ ] .env files configured with production values
- [ ] MongoDB Atlas cluster created
- [ ] Ollama model selected and tested
- [ ] SSL certificate ready (for HTTPS)
- [ ] Domain name purchased
- [ ] API documentation reviewed
- [ ] Security audit completed
- [ ] Backup strategy defined

---

## Option 1: Deploy Backend to Render

Render is a modern cloud platform that supports Python Flask applications with free tier.

### 1.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Link your GitHub account

### 1.2 Prepare GitHub Repository
```bash
# In your backend directory
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 1.3 Create Web Service on Render
1. Dashboard → New → Web Service
2. Connect GitHub repository
3. Choose your repository

### 1.4 Configure Service Settings

**Service Details:**
- Name: `eduai-backend`
- Environment: `Python 3.10`
- Region: `Oregon` (or closest to users)

**Build & Deploy:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `python run.py`

**Environment Variables:**
```
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=<generate-secure-random-string>
JWT_SECRET_KEY=<generate-secure-random-string>
MONGODB_URI=<mongodb-atlas-connection-string>
MONGODB_DB_NAME=educational_platform
OLLAMA_BASE_URL=<ollama-server-url>
OLLAMA_MODEL=mistral
CORS_ORIGINS=https://your-frontend-domain.com
LOG_LEVEL=INFO
```

### 1.5 Deploy
1. Click "Create Web Service"
2. Render builds and deploys automatically
3. Once deployed, you get a URL like: `https://eduai-backend.onrender.com`

### 1.6 Test Backend Deployment
```bash
curl https://eduai-backend.onrender.com/health

# Should return:
# {"status":"healthy","database":"connected"}
```

**Note:** Render hobby tier may have cold starts. Upgrade to paid tier for production.

---

## Option 2: Deploy Backend to AWS EC2

AWS provides more control and scalability for production applications.

### 2.1 Create EC2 Instance
1. Go to [AWS Console](https://console.aws.amazon.com)
2. EC2 → Instances → Launch Instance
3. Select Ubuntu Server 22.04 LTS
4. Choose instance type: `t3.small` (free tier: t2.micro)
5. Create security group with ports:
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
   - Port 22 (SSH)
   - Port 5000 (Flask)

### 2.2 Connect to Instance
```bash
# Download your .pem key file
# On Windows (PowerShell):
ssh -i "your-key.pem" ec2-user@your-instance-ip

# Or use PuTTY on Windows with .ppk format
```

### 2.3 Install Dependencies
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install Ollama (on separate server or same server)
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull mistral
```

### 2.4 Clone and Configure Application
```bash
# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit .env with production values
nano .env
```

### 2.5 Setup Gunicorn (Production Server)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 run:app &

# Or for eventlet (supports long-polling):
pip install eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 run:app &
```

### 2.6 Setup Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/eduai-backend.service
```

**Add this content:**
```ini
[Unit]
Description=EduAI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo/backend
Environment="PATH=/home/ubuntu/your-repo/backend/venv/bin"
ExecStart=/home/ubuntu/your-repo/backend/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 run:app

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable eduai-backend
sudo systemctl start eduai-backend
sudo systemctl status eduai-backend

# View logs
sudo journalctl -u eduai-backend -f
```

### 2.7 Setup Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/default
```

**Config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### 2.8 Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Option 3: Deploy Backend to Heroku (Legacy)

**Note:** Heroku free tier ended in November 2022. Use Render or AWS instead.

---

## Frontend Deployment

### Option A: Deploy to Vercel

Vercel is optimized for Next.js and React, with automatic deployments from Git.

#### A1. Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Link your repository

#### A2. Import Project
1. Dashboard → Add New → Project
2. Select your GitHub repository
3. Select `frontend` directory as root

#### A3. Configure Environment
Set environment variables:
```
REACT_APP_API_URL=https://your-backend-domain.com/api
REACT_APP_ENVIRONMENT=production
```

#### A4. Deploy
1. Click "Deploy"
2. Vercel builds and deploys automatically
3. Get URL like: `https://your-app.vercel.app`

#### A5. Connect Custom Domain
1. Settings → Domains
2. Add your custom domain
3. Update DNS records at registrar
4. Vercel provides CNAME instructions

### Option B: Deploy to Netlify

Netlify is another popular React deployment platform.

#### B1. Create Account
1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub

#### B2. Deploy
1. New Site → Connect to Git
2. Select repository and frontend directory
3. Deploy settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
4. Click "Deploy Site"

### Option C: Deploy to AWS S3 + CloudFront

For advanced S3 deployment with CDN.

#### C1. Create S3 Bucket
```bash
aws s3 mb s3://your-app-name
```

#### C2. Build Frontend
```bash
cd frontend
npm run build
```

#### C3. Upload to S3
```bash
aws s3 sync dist/ s3://your-app-name --delete
```

#### C4. Create CloudFront Distribution
1. AWS Console → CloudFront
2. Create Distribution
3. Origin Domain: S3 bucket
4. Enable HTTPS
5. Add custom domain

---

## Database Setup - MongoDB Atlas

### Prerequisites
- MongoDB Atlas account (free tier available)
- Credit card for account verification

### Setup Steps

#### 1. Create Account
1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Sign up with email
3. Create account

#### 2. Create Cluster
1. Dashboard → Create a Project
2. Choose cluster name: `eduai-prod`
3. Select Tier: `M0 Sandbox` (free)
4. Provider: `AWS`
5. Region: Choose closest to your users
6. Click "Create"

#### 3. Configure Security
1. Database Access → Add New Database User
   - Username: `eduai_user`
   - Password: Generate secure password
   - Role: `Read and write to any database`

2. Network Access → Add IP Address
   - For testing: `0.0.0.0/0` (allow all)
   - For production: Add specific IPs

#### 4. Get Connection String
1. Clusters → Connect
2. Choose "Connect your application"
3. Copy connection string:
   ```
   mongodb+srv://eduai_user:password@cluster.mongodb.net/educational_platform
   ```

4. Update in backend `.env`:
   ```env
   MONGODB_URI=mongodb+srv://eduai_user:YOUR_PASSWORD@cluster.mongodb.net/educational_platform
   ```

#### 5. Create Collections
Collections auto-create when backend starts. To manually create:

1. Go to Collections
2. Create collection: `users`
3. Repeat for: `chats`, `notes`, `assessments`, `questions`, `progress`

#### 6. Setup Backup
1. Backup & Restore → Select cluster
2. Enable continuous backups
3. Set retention policy

---

## Ollama Deployment Options

### Option 1: Local Server (Same as Backend)
```bash
# Install and start on backend server
ollama serve
```

### Option 2: Separate Ollama Server
For GPU-accelerated inference:

```bash
# On dedicated GPU server
ollama serve --host 0.0.0.0:11434

# Update backend .env:
OLLAMA_BASE_URL=http://ollama-server-ip:11434
```

### Option 3: Cloud LLM Provider
As fallback, use API-based providers:

```env
# If using OpenAI instead of Ollama
OPENAI_API_KEY=sk-xxx...
```

See code for OpenAI integration.

---

## Email Configuration (Optional)

For password reset and notifications:

```env
# Using Gmail
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=app-specific-password
MAIL_USE_TLS=true

# Using SendGrid
SENDGRID_API_KEY=SG.xxx...
```

---

## Security Hardening

### 1. Generate Secure Keys
```python
import secrets
print(secrets.token_hex(32))  # For SECRET_KEY
print(secrets.token_hex(32))  # For JWT_SECRET_KEY
```

### 2. Set Environment Variables
Never commit `.env` files to Git.

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### 3. Enable HTTPS
- Use Let's Encrypt (free)
- Or AWS Certificate Manager
- Or Cloudflare for DNS + SSL

### 4. Configure CORS
Set `CORS_ORIGINS` to your frontend domain only:

```env
CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com
```

### 5. Setup Firewall Rules
- Only expose necessary ports
- Restrict MongoDB access to application
- Whitelist IP addresses if possible

### 6. Enable Logging and Monitoring
```env
LOG_LEVEL=INFO
SENTRY_DSN=https://xxx...@sentry.io/xxx  # For error tracking
```

---

## Performance Optimization

### 1. Database Optimization
```javascript
// Add indexes in MongoDB
db.users.createIndex({ email: 1 })
db.chats.createIndex({ user_id: 1 })
db.notes.createIndex({ subject: 1 })
db.progress.createIndex({ student_id: 1 })
```

### 2. Caching
```python
# Enable Redis caching in production
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://redis-server:6379/0
```

### 3. CDN for Static Assets
- Vercel CDN (automatic)
- CloudFront for S3
- Cloudflare for any origin

### 4. Database Connection Pooling
```python
# Already configured in db.py
```

---

## Monitoring and Maintenance

### 1. Error Tracking
Setup Sentry for production errors:
```env
SENTRY_DSN=https://your-key@sentry.io/project-id
```

### 2. Application Monitoring
- Uptime monitoring: UptimeRobot
- Performance: New Relic or DataDog
- Logs: AWS CloudWatch or LogRocket

### 3. Database Backups
MongoDB Atlas automatically backs up:
- Daily snapshots
- 7-day retention (free tier)
- 30-day retention (paid)

### 4. Regular Updates
```bash
# Keep dependencies updated
pip list --outdated
npm outdated

# Update specific packages
pip install --upgrade flask
npm update
```

---

## Troubleshooting Production Issues

### High Server Load
- Check slow queries in MongoDB
- Monitor Ollama resource usage
- Increase Gunicorn workers
- Enable caching

### 502 Bad Gateway
- Check if backend is running
- Check logs: `journalctl -u eduai-backend`
- Verify MongoDB connection
- Check firewall rules

### Slow API Responses
- Check database indexes
- Monitor Ollama response time
- Check network latency
- Optimize vector search queries

### Database Connection Issues
- Verify MongoDB Atlas IP whitelist
- Check username and password
- Test connection string locally
- Check firewall on server

---

## Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] Backend deployed (Render/EC2/Heroku)
- [ ] Frontend deployed (Vercel/Netlify)
- [ ] MongoDB Atlas cluster created
- [ ] Collection indexes created
- [ ] Ollama server running
- [ ] Environment variables configured
- [ ] HTTPS/SSL enabled
- [ ] Domain DNS updated
- [ ] Email configuration (if needed)
- [ ] Error tracking (Sentry) setup
- [ ] Monitoring enabled
- [ ] Backup strategy implemented
- [ ] Tested end-to-end flow
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated

---

## Estimated Costs (Monthly)

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Render Backend | - | $7+ |
| Vercel Frontend | Yes | $20+ |
| MongoDB Atlas | 512MB | $57+ |
| Ollama Server | Self-hosted | Self-hosted |
| **Total** | Variable | **$100+** |

---

## Getting Help

**Render:** Support portal at render.com
**AWS:** AWS Support community
**MongoDB:** Community forums at mongodb.com
**Vercel:** Documentation at vercel.com/docs

---

**Deployment Time:** 1-2 hours (first time)
**Ongoing Maintenance:** 4-8 hours/month

Good luck with your production deployment! 🚀
