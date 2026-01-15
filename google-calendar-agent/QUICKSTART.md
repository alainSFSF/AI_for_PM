# Quick Start Guide

Get your Google Calendar Agent running in 5 minutes!

## Prerequisites Checklist

- [ ] Node.js v18+ installed
- [ ] Anthropic API key from https://console.anthropic.com/
- [ ] Google account

## Step-by-Step Setup

### 1. Google Cloud Setup (5 minutes)

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable Google Calendar API:
   - Click "Enable APIs and Services"
   - Search "Google Calendar API"
   - Click "Enable"
4. Create credentials:
   - Go to "Credentials" tab
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Name it (e.g., "Calendar Agent")
   - Add redirect URI: `http://localhost:3000/oauth2callback`
   - Click "Create"
   - **Copy the Client ID and Client Secret**

### 2. Install & Configure (2 minutes)

```bash
# Navigate to the project
cd google-calendar-agent

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your keys
# Use nano, vim, or your favorite editor
nano .env
```

Add these to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_CLIENT_ID=123456789-....apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
GOOGLE_REDIRECT_URI=http://localhost:3000/oauth2callback
```

### 3. Build & Authorize (2 minutes)

```bash
# Build the project
npm run build

# Authorize Google Calendar access
npm run dev
```

The auth script will:
1. Show you a URL
2. Open it in your browser
3. Sign in with Google
4. Grant calendar permissions
5. Redirect back (you'll see "Authentication successful!")

### 4. Try It Out!

```bash
# Start interactive mode
npm run dev
```

Try these commands:
```
You: What are my meetings today?
You: Create a test event tomorrow at 2pm for 1 hour
You: Search for meetings with "standup"
You: quit
```

## Common Issues

**"Module not found"**
→ Run `npm install` again

**"ANTHROPIC_API_KEY not set"**
→ Check your `.env` file exists and has the correct key

**"Missing Google OAuth credentials"**
→ Verify Client ID and Secret are in `.env`

**"Port 3000 in use"**
→ Stop other services on port 3000, or change the redirect URI

## Next Steps

- Read [README.md](./README.md) for detailed documentation
- Try different queries in interactive mode
- Build your own calendar workflows!

## Getting Help

- Check the [Troubleshooting section](./README.md#troubleshooting) in README
- Review [Google Calendar API docs](https://developers.google.com/calendar/api)
- Check [Claude API documentation](https://docs.anthropic.com/)

Enjoy your new calendar agent! 🎉
