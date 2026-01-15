# Google Calendar Agent

A Claude Agent SDK integration that allows you to interact with your Google Calendar using natural language.

## Features

- **List Events**: View upcoming events from your calendar
- **Create Events**: Schedule new meetings and events
- **Search Events**: Find events by keyword
- **Delete Events**: Remove events from your calendar
- **Interactive Mode**: Chat-like interface for multiple requests
- **Single Query Mode**: Run one-off commands

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Anthropic API Key** - Get from [Anthropic Console](https://console.anthropic.com/)
3. **Google Cloud Project** with Calendar API enabled

## Setup Instructions

### Step 1: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URI: `http://localhost:3000/oauth2callback`
   - Click "Create"
   - Note down the **Client ID** and **Client Secret**

### Step 2: Project Setup

1. **Navigate to the project directory**:
   ```bash
   cd google-calendar-agent
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` file** with your credentials:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:3000/oauth2callback
   ```

### Step 3: Build the Project

```bash
npm run build
```

### Step 4: Authorize Google Calendar Access

Run the authorization script to authenticate with Google:

```bash
npm run dev -- auth
```

This will:
1. Open a URL in your terminal
2. Visit the URL in your browser
3. Sign in with your Google account
4. Grant calendar access
5. Store the token locally in `token.json`

**Note**: You only need to do this once. The token will be refreshed automatically.

## Usage

### Interactive Mode

Start the agent in interactive mode for ongoing conversation:

```bash
npm run dev
```

Example session:
```
You: What are my meetings today?
Agent: You have 3 meetings today:
1. Team Standup at 9:00 AM
2. Project Review at 2:00 PM
3. Client Call at 4:00 PM

You: Create a meeting with john@example.com tomorrow at 3pm for 1 hour titled "Project Discussion"
Agent: Event created successfully! I've scheduled "Project Discussion" for tomorrow at 3:00 PM...

You: quit
```

### Single Query Mode

Run a single command and exit:

```bash
npm run dev "What are my meetings this week?"
```

```bash
npm run dev "Create a team meeting tomorrow at 10am for 30 minutes"
```

## Example Queries

### List Events
- "What are my meetings today?"
- "Show me my calendar for the next 3 days"
- "What do I have scheduled this week?"

### Create Events
- "Schedule a meeting with alice@example.com tomorrow at 2pm for 1 hour"
- "Create a team standup every weekday at 9am"
- "Add a reminder for my dentist appointment on Friday at 3pm"

### Search Events
- "Find all meetings about the project review"
- "Search for events with John"
- "Show me all client meetings"

### Delete Events
- "Delete the meeting at 3pm today"
- "Cancel my 2pm appointment"
- Note: You'll need the event ID for deletion

## Available Tools

The agent has access to four tools:

1. **list_events**: Lists upcoming events
   - Parameters: `max_results`, `days_ahead`

2. **create_event**: Creates a new calendar event
   - Parameters: `title`, `start_time`, `end_time`, `description`, `attendees`, `location`

3. **search_events**: Searches events by keyword
   - Parameters: `query`, `max_results`

4. **delete_event**: Deletes an event
   - Parameters: `event_id`

## Project Structure

```
google-calendar-agent/
├── src/
│   ├── auth.ts       # Google OAuth authentication
│   ├── agent.ts      # Main agent logic with tools
│   └── index.ts      # Entry point (interactive/single query mode)
├── dist/             # Compiled TypeScript output
├── .env              # Environment variables (you create this)
├── .env.example      # Example environment file
├── token.json        # Google OAuth token (auto-generated)
├── package.json      # Dependencies and scripts
├── tsconfig.json     # TypeScript configuration
└── README.md         # This file
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Make sure you've created a `.env` file with your API key
- Check that the `.env` file is in the `google-calendar-agent` directory

### "Missing Google OAuth credentials"
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are in `.env`
- Make sure they match your Google Cloud Console credentials

### "Token expired" or Authentication errors
- Delete `token.json` and re-run authorization: `npm run dev -- auth`
- Check that your redirect URI in Google Cloud Console matches the one in `.env`

### "Calendar API not enabled"
- Go to Google Cloud Console and enable the Google Calendar API
- Wait a few minutes for the API to activate

### Port 3000 already in use
- The OAuth callback uses port 3000
- Stop any other services using this port or update `GOOGLE_REDIRECT_URI` in `.env`

## Security Notes

- **Never commit** `.env` or `token.json` to version control
- The `.gitignore` file is configured to exclude these files
- Keep your API keys and OAuth tokens secure
- The token has full access to your Google Calendar

## Development

Build the project:
```bash
npm run build
```

Run in development mode (with auto-reload):
```bash
npm run dev
```

Run the compiled version:
```bash
npm start
```

## License

MIT

## Support

For issues with:
- **Claude Agent SDK**: Check [Claude API Documentation](https://docs.anthropic.com/claude/docs)
- **Google Calendar API**: See [Google Calendar API Docs](https://developers.google.com/calendar/api)
- **This Project**: Open an issue on GitHub
