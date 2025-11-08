# Vercel Setup Guide

This guide walks you through creating and configuring a Vercel project for the Brazilian CDS Data Feeder application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Create Vercel Account](#step-1-create-vercel-account)
- [Step 2: Import GitHub Repository](#step-2-import-github-repository)
- [Step 3: Configure Project Settings](#step-3-configure-project-settings)
- [Step 4: Set Environment Variables](#step-4-set-environment-variables)
- [Step 5: Deploy](#step-5-deploy)
- [Step 6: Verify Deployment](#step-6-verify-deployment)
- [Vercel CLI Setup](#vercel-cli-setup)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:

- GitHub account with the repository pushed
- Neon PostgreSQL database created (see [NEON_POSTGRES_SETUP.md](./NEON_POSTGRES_SETUP.md))
- Database connection string ready
- (Optional) BetterStack account for logging

## Step 1: Create Vercel Account

1. **Go to Vercel**: Visit [vercel.com](https://vercel.com)

2. **Sign Up**: Click "Sign Up" or "Start Deploying"
   - Recommended: Sign up with GitHub for seamless integration
   - This automatically connects your GitHub account

3. **Complete Registration**: Follow the prompts to complete your account setup

## Step 2: Import GitHub Repository

1. **Access Dashboard**: After logging in, you'll see your Vercel dashboard

2. **Add New Project**: Click "Add New" → "Project"

3. **Import Git Repository**:
   - You'll see "Import Git Repository" section
   - Select "GitHub" as the source
   - If not connected, click "Connect GitHub Account"

4. **Authorize Vercel**: 
   - Grant Vercel access to your GitHub repositories
   - You can choose "All repositories" or "Only select repositories"
   - For security, recommended: select only the repositories you want to deploy

5. **Select Repository**:
   - Search for: `brazilian_cds_datafeeder` (or your repository name)
   - Click "Import" on your repository

## Step 3: Configure Project Settings

You'll see the "Configure Project" screen with several options:

### Project Name

- **Default**: `brazilian-cds-datafeeder`
- **Custom**: You can change to any name you prefer
- This becomes part of your URL: `https://your-project-name.vercel.app`

### Vercel Team

- **Personal Account**: Use "Flavio Lopes' projects" (your personal account)
- **Team Account**: Or select a team if you're part of one
- The dropdown shows "Hobby" plan for personal projects (free tier)

### Framework Preset

- **Select**: `Other`
- This project uses Python/FastAPI which requires custom configuration
- Vercel will detect the `vercel.json` configuration file

### Root Directory

- **Default**: `./` (root of repository)
- **Leave as**: `./`
- The project structure is already configured correctly
- Click "Edit" only if your project is in a subdirectory

### Build and Output Settings

Click to expand this section:

#### Build Command

**Leave empty or set to**: `echo "No build step required"`

- Python serverless functions don't need a build step
- Dependencies are installed automatically by Vercel

#### Output Directory

**Leave empty**

- Not needed for serverless functions
- Vercel uses the `api/` directory automatically

#### Install Command

**Leave empty** (default: auto-detected)

- Vercel automatically runs: `pip install -r requirements.txt`
- Our `requirements.txt` is at the root, so this works automatically

#### Development Command

**Leave empty**

- Local development uses: `python scripts/start_api.py`
- Not used by Vercel deployment

### Environment Variables

Click to expand "Environment Variables" section. You'll need to add these:

**Critical Variables:**

1. **NEON_DATABASE_URL**
   - **Key**: `NEON_DATABASE_URL`
   - **Value**: Your Neon PostgreSQL connection string
   - Format: `postgresql://user:password@host/database?sslmode=require`
   - **Environment**: Production (default)

2. **ENVIRONMENT**
   - **Key**: `ENVIRONMENT`
   - **Value**: `production`
   - **Environment**: Production

**Optional Variables:**

3. **BETTERSTACK_SOURCE_TOKEN**
   - **Key**: `BETTERSTACK_SOURCE_TOKEN`
   - **Value**: Your BetterStack source token
   - **Environment**: Production
   - Skip if not using BetterStack logging

4. **LOG_LEVEL**
   - **Key**: `LOG_LEVEL`
   - **Value**: `INFO`
   - **Environment**: Production

To add each variable:
- Click "Add" or the first empty field
- Enter the key name
- Enter the value
- Select environment (Production recommended)
- Click checkmark or press Enter

**⚠️ Important**: Add `NEON_DATABASE_URL` before deploying!

## Step 4: Set Environment Variables

### Method 1: During Initial Setup (Recommended)

1. In the "Environment Variables" section, click to expand
2. Add each variable as described above
3. Ensure `NEON_DATABASE_URL` is set correctly
4. Click outside the section or continue to deploy

### Method 2: After Project Creation

1. Go to your project dashboard
2. Click "Settings" tab
3. Select "Environment Variables" from the left sidebar
4. Click "Add New" for each variable
5. Enter key, value, and select environment
6. Click "Save"

### Environment Variable Checklist

✅ Required:
- [ ] `NEON_DATABASE_URL` - PostgreSQL connection string
- [ ] `ENVIRONMENT` - Set to `production`

✅ Optional:
- [ ] `BETTERSTACK_SOURCE_TOKEN` - For centralized logging
- [ ] `LOG_LEVEL` - Set to `INFO` or `DEBUG`

## Step 5: Deploy

1. **Review Configuration**: Double-check all settings

2. **Click "Deploy"**: The gray button at the bottom becomes active after configuration

3. **Wait for Deployment**:
   - Vercel will start building and deploying
   - You'll see real-time logs
   - Takes 30-60 seconds typically

4. **Deployment Process**:
   ```
   Building...
   → Installing dependencies
   → Analyzing project structure
   → Creating serverless functions
   → Deploying...
   ✓ Deployment successful
   ```

5. **Success**: You'll see a success screen with:
   - Preview image of your deployment
   - Deployment URL
   - "Visit" button

## Step 6: Verify Deployment

### Test Your API

1. **Visit Deployment**: Click "Visit" or open: `https://your-project-name.vercel.app`

2. **Test Health Endpoint**:
   ```bash
   curl https://your-project-name.vercel.app/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "environment": "production"
   }
   ```

3. **Test API Documentation**:
   - Visit: `https://your-project-name.vercel.app/docs`
   - You should see the interactive API documentation

4. **Test CDS Data Endpoint**:
   ```bash
   curl https://your-project-name.vercel.app/cds/latest
   ```
   
   Expected response: Array of latest CDS records (JSON)

### Check Logs

1. Go to your project dashboard
2. Click "Deployments" tab
3. Click on the latest deployment
4. View "Functions" logs to see API requests

### Verify Database Connection

The API should automatically connect to your Neon database. Check:

1. **Function Logs**: Look for successful database queries
2. **Test Stats Endpoint**:
   ```bash
   curl https://your-project-name.vercel.app/cds/stats
   ```

## Vercel CLI Setup

For advanced users, you can use Vercel CLI for deployment and management.

### Install Vercel CLI

```bash
# Using npm
npm i -g vercel

# Using yarn
yarn global add vercel

# Using pnpm
pnpm add -g vercel
```

### Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate.

### Link Project

From your project directory:

```bash
cd /path/to/brazilian_cds
vercel link
```

Select:
- Your Vercel team/account
- Link to existing project
- Select `brazilian-cds-datafeeder`

### Deploy via CLI

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Force redeploy
vercel --prod --force
```

### Manage Environment Variables

```bash
# Add variable
vercel env add NEON_DATABASE_URL

# List variables
vercel env ls

# Pull environment variables
vercel env pull .env.production
```

### View Logs

```bash
# View real-time logs
vercel logs

# View logs for specific deployment
vercel logs [deployment-url]
```

## Project Configuration Files

The project includes these Vercel configuration files:

### vercel.json

Located at project root, defines:
- Build configuration
- Route redirects to API
- Serverless function settings

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### .vercelignore

Excludes files from deployment:
- `__pycache__/`
- `*.pyc`
- `.env`
- Development files
- Documentation

## Troubleshooting

### Deployment Fails

**Problem**: Build or deployment errors

**Solutions**:

1. **Check requirements.txt**: Ensure all dependencies are listed
   ```bash
   pip freeze > requirements.txt
   ```

2. **Verify vercel.json**: Check syntax and configuration

3. **Check logs**: Click on failed deployment → View function logs

4. **Python version**: Vercel uses Python 3.9 by default
   - Add `runtime.txt` with: `python-3.11` if needed

### API Returns 500 Errors

**Problem**: Function errors or crashes

**Solutions**:

1. **Check environment variables**:
   ```bash
   vercel env ls
   ```
   Ensure `NEON_DATABASE_URL` is set

2. **View function logs**:
   - Dashboard → Deployments → Latest → Functions
   - Look for error messages

3. **Test locally first**:
   ```bash
   ENVIRONMENT=production python scripts/start_api.py
   ```

4. **Database connection**: Verify Neon database is accessible

### Environment Variables Not Working

**Problem**: Variables not available in functions

**Solutions**:

1. **Check environment scope**: Variables must be set for "Production"

2. **Redeploy after adding variables**:
   ```bash
   vercel --prod --force
   ```

3. **Variable naming**: Use exact names from `config/settings.py`

### Cold Start Timeouts

**Problem**: First request takes too long (10+ seconds)

**Solutions**:

1. **Expected behavior**: Serverless functions have cold starts
   - First request after idle: 5-10 seconds
   - Subsequent requests: < 1 second

2. **Keep warm**: Use a monitoring service to ping health endpoint

3. **Connection pooling**: Already configured in `src/database/connection.py`

4. **Upgrade plan**: Pro plan has faster cold starts

### Database Connection Fails

**Problem**: Cannot connect to Neon database

**Solutions**:

1. **Check connection string**: Must include `?sslmode=require`

2. **Verify format**:
   ```
   postgresql://user:password@host/database?sslmode=require
   ```

3. **Test connection**: Use Neon dashboard SQL editor

4. **Check Neon status**: Database may be suspended (free tier)
   - First query wakes it up (takes longer)

5. **IP restrictions**: Vercel uses dynamic IPs
   - Ensure Neon allows all IPs (default)

### Custom Domain Issues

**Problem**: Domain not working after setup

**Solutions**:

1. **DNS propagation**: Wait 24-48 hours

2. **Check DNS records**: Verify CNAME or A records

3. **Force HTTPS**: Enable in Vercel project settings

4. **Check domain status**: Project → Settings → Domains

## Advanced Configuration

### Custom Domain Setup

1. Go to Project → Settings → Domains
2. Click "Add"
3. Enter your domain: `api.yourdomain.com`
4. Follow DNS configuration instructions
5. Wait for verification

### Automatic Deployments

By default, Vercel automatically deploys:
- **Production**: Pushes to `main` branch
- **Preview**: Pushes to other branches or pull requests

To disable:
1. Project → Settings → Git
2. Toggle "Production Branch" or "Preview Deployments"

### Deploy Hooks

Create webhook URLs for triggering deployments:

1. Project → Settings → Git → Deploy Hooks
2. Click "Create Hook"
3. Choose branch and name
4. Use the webhook URL to trigger deploys

Example with GitHub Actions:
```yaml
- name: Trigger Vercel Deploy
  run: |
    curl -X POST ${{ secrets.VERCEL_DEPLOY_HOOK }}
```

### Function Configuration

Adjust serverless function settings:

**Memory**: 1024 MB (default, up to 3008 MB on Pro)
**Max Duration**: 10s (Hobby), 60s (Pro)
**Region**: Automatic (or specify in vercel.json)

## Next Steps

After successful deployment:

1. **Set up GitHub Actions**: Configure daily data updates
   - See [DEPLOYMENT.md](./DEPLOYMENT.md)

2. **Configure monitoring**: Set up uptime monitoring
   - Use Vercel Analytics
   - Add external monitoring (UptimeRobot, etc.)

3. **Add custom domain**: Professional look
   - Project → Settings → Domains

4. **Review logs**: Monitor API usage
   - Enable BetterStack for centralized logging

5. **Test thoroughly**: Verify all endpoints work

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Serverless Functions](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Custom Domains](https://vercel.com/docs/concepts/projects/domains)

## Support

- **Vercel Support**: [vercel.com/support](https://vercel.com/support)
- **Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Project Issues**: Check your project's GitHub issues

---

**Last Updated**: November 7, 2025

**Related Guides**:
- [SETUP_FROM_SCRATCH.md](./SETUP_FROM_SCRATCH.md) - Complete setup overview
- [NEON_POSTGRES_SETUP.md](./NEON_POSTGRES_SETUP.md) - Database setup
- [DEPLOYMENT.md](./DEPLOYMENT.md) - GitHub Actions configuration
- [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md) - Production deployment guide
