# Deployment Guide - Braai Bites & Beverages

## Quick Start: Deploy to Render.com (Recommended for Beginners)

### Step 1: Prepare Your Code
1. Update `.env` with secure credentials:
   ```bash
   # Generate a secure SECRET_KEY
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Change admin credentials in `.env`:
   ```
   ADMIN_USERNAME=your_username
   ADMIN_PASSWORD=your_strong_password
   ```

3. Set production mode in `.env`:
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/braai-bites-beverages.git
git push -u origin main
```

### Step 3: Deploy to Render
1. Go to https://render.com and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select the repository
4. Configure the service:
   - **Name**: braai-bites-beverages
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Instance Type**: Free (or Starter for $7/month)

5. Add Environment Variables:
   - Click "Advanced" → "Add Environment Variable"
   - Add all variables from your `.env` file:
     - `SECRET_KEY`
     - `FLASK_ENV=production`
     - `FLASK_DEBUG=False`
     - `ADMIN_USERNAME`
     - `ADMIN_PASSWORD`
     - `ALIEXPRESS_APP_KEY`
     - `ALIEXPRESS_APP_SECRET`
     - `DATABASE_URL` (will be auto-created if you add PostgreSQL)

6. Click "Create Web Service"

7. Wait 5-10 minutes for deployment

8. Your site will be live at: `https://braai-bites-beverages.onrender.com`

### Step 4: Add a Database (Optional but Recommended)
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name it `braai-bites-db`
3. Select Free tier
4. Click "Create Database"
5. Copy the "Internal Database URL"
6. Go to your Web Service → Environment
7. Update `DATABASE_URL` with the PostgreSQL URL

### Step 5: Add a Custom Domain (Optional)
1. Buy a domain from Namecheap, GoDaddy, or Google Domains
2. In Render, go to your service → Settings → Custom Domains
3. Click "Add Custom Domain"
4. Enter your domain (e.g., `braaibites.co.za`)
5. Add the DNS records shown to your domain provider
6. Wait for DNS propagation (up to 48 hours)
7. Render will automatically provision SSL certificate

---

## Alternative Deployment Options

### Railway.app (Easy + Fast)
1. Push code to GitHub
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub"
4. Select repository
5. Add environment variables
6. Railway auto-deploys!
7. Optional: Add PostgreSQL database with one click

**Cost:** $5/month after free trial

---

### DigitalOcean App Platform (Professional)
1. Sign up at https://digitalocean.com
2. Apps → Create App → GitHub
3. Select repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn run:app`
5. Add environment variables
6. Deploy

**Cost:** $5/month (Basic plan)

---

### Vercel (Serverless)
1. Install Vercel CLI: `npm i -g vercel`
2. Create `vercel.json`:
   ```json
   {
     "builds": [
       {
         "src": "run.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "run.py"
       }
     ]
   }
   ```
3. Run: `vercel`
4. Follow prompts

**Cost:** Free tier available

---

## Post-Deployment Checklist

### 1. Test Everything
- [ ] Home page loads
- [ ] All category pages work
- [ ] Search functionality works
- [ ] Admin login works at `/admin/login`
- [ ] Can add/edit/delete products
- [ ] Images load properly
- [ ] Mobile responsiveness

### 2. Security
- [ ] Changed default admin credentials
- [ ] Strong SECRET_KEY set
- [ ] DEBUG mode is False
- [ ] `.env` file not in repository
- [ ] HTTPS is enabled (automatic with Render/Railway)

### 3. Performance
- [ ] Database is PostgreSQL (not SQLite)
- [ ] Static files are cached
- [ ] Images are optimized
- [ ] Consider adding CDN for images (Cloudinary, ImageKit)

### 4. Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Monitor uptime (UptimeRobot, Pingdom)
- [ ] Check logs regularly

### 5. SEO & Analytics
- [ ] Add Google Analytics
- [ ] Submit sitemap to Google Search Console
- [ ] Add meta descriptions
- [ ] Verify social media sharing works

---

## Production Environment Variables

**Required:**
```
SECRET_KEY=your-very-long-random-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
```

**AliExpress API:**
```
ALIEXPRESS_APP_KEY=your_app_key
ALIEXPRESS_APP_SECRET=your_app_secret
ALIEXPRESS_API_URL=https://gw.api.alibaba.com/openapi/
```

**Database (if using PostgreSQL):**
```
DATABASE_URL=postgresql://username:password@hostname:5432/dbname
```

---

## Troubleshooting

### Application Won't Start
- Check logs in platform dashboard
- Verify all environment variables are set
- Ensure `gunicorn` is in requirements.txt
- Check Python version matches runtime.txt

### Database Errors
- If using SQLite, migrate to PostgreSQL for production
- Verify DATABASE_URL format
- Check database credentials
- Run migrations: `flask db upgrade`

### Admin Login Not Working
- Verify ADMIN_USERNAME and ADMIN_PASSWORD are set
- Check browser cookies are enabled
- Try incognito/private browsing mode

### Images Not Loading
- Check image URLs are valid
- Consider using CDN (Cloudinary)
- Verify CORS settings if images are external

---

## Scaling Considerations

### When to Upgrade
- Free tier sleeping is annoying users
- Response times > 2 seconds
- More than 1000 visitors/day
- Need 99.9% uptime

### Upgrade Path
1. **Starter Plan** ($7-10/month) - Better performance, no sleeping
2. **Database Optimization** - Indexes, connection pooling
3. **CDN** - Cloudflare for static assets
4. **Caching** - Redis for session/query caching
5. **Load Balancer** - Multiple app instances

---

## Cost Breakdown

### Free Options
- **Render Free Tier**: $0/month (sleeps after 15min inactivity)
- **Railway Trial**: $5 credit (lasts 2-3 months light usage)

### Budget ($5-10/month)
- **Render Starter**: $7/month
- **DigitalOcean App**: $5/month
- **Railway Pro**: $5/month

### Professional ($20-50/month)
- **DigitalOcean App + Database**: $20/month
- **AWS Elastic Beanstalk**: $25-50/month
- **Custom Domain**: $10-15/year
- **CDN (Cloudinary)**: $0-25/month

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **DigitalOcean Tutorials**: https://www.digitalocean.com/community/tutorials

---

## Quick Deploy Checklist

- [ ] Update `.env` with production credentials
- [ ] Push code to GitHub
- [ ] Create account on hosting platform
- [ ] Connect GitHub repository
- [ ] Add environment variables
- [ ] Deploy
- [ ] Test admin login
- [ ] Test product management
- [ ] Add custom domain (optional)
- [ ] Monitor for 24 hours

**Recommended for Your Project:** Start with Render.com free tier, then upgrade to Starter ($7/month) once you're ready for production traffic.
