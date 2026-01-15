import { google } from 'googleapis';
import * as fs from 'fs';
import * as http from 'http';
import { URL } from 'url';
import * as dotenv from 'dotenv';

dotenv.config();

const SCOPES = ['https://www.googleapis.com/auth/calendar'];
const TOKEN_PATH = './token.json';

interface TokenData {
  access_token: string;
  refresh_token: string;
  scope: string;
  token_type: string;
  expiry_date: number;
}

/**
 * Create an OAuth2 client with the given credentials
 */
export function createOAuth2Client() {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const redirectUri = process.env.GOOGLE_REDIRECT_URI || 'http://localhost:3000/oauth2callback';

  if (!clientId || !clientSecret) {
    throw new Error('Missing Google OAuth credentials. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file');
  }

  return new google.auth.OAuth2(clientId, clientSecret, redirectUri);
}

/**
 * Get and store new token after prompting for user authorization
 */
async function getNewToken(oAuth2Client: any): Promise<void> {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });

  console.log('\n==========================================================');
  console.log('Google Calendar Authorization');
  console.log('==========================================================\n');
  console.log('To authorize this app, visit this URL in your browser:\n');
  console.log(authUrl);
  console.log('\n==========================================================\n');

  return new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      try {
        if (req.url && req.url.indexOf('/oauth2callback') > -1) {
          const qs = new URL(req.url, 'http://localhost:3000').searchParams;
          const code = qs.get('code');

          if (!code) {
            res.end('No code received. Authorization failed.');
            server.close();
            reject(new Error('No authorization code received'));
            return;
          }

          res.end('Authentication successful! You can close this window.');
          server.close();

          const { tokens } = await oAuth2Client.getToken(code);
          oAuth2Client.setCredentials(tokens);

          // Store the token to disk for later program executions
          fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens));
          console.log('\n✓ Token stored to', TOKEN_PATH);
          resolve();
        }
      } catch (e) {
        reject(e);
      }
    }).listen(3000, () => {
      console.log('Waiting for authorization on http://localhost:3000...\n');
    });
  });
}

/**
 * Load or request authorization to call Google Calendar API
 */
export async function authorize() {
  const oAuth2Client = createOAuth2Client();

  // Check if we have previously stored a token
  if (fs.existsSync(TOKEN_PATH)) {
    const token = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf-8')) as TokenData;
    oAuth2Client.setCredentials(token);

    // Check if token is expired
    if (token.expiry_date && token.expiry_date < Date.now()) {
      console.log('Token expired, refreshing...');
      try {
        const { credentials } = await oAuth2Client.refreshAccessToken();
        oAuth2Client.setCredentials(credentials);
        fs.writeFileSync(TOKEN_PATH, JSON.stringify(credentials));
        console.log('✓ Token refreshed');
      } catch (error) {
        console.log('Failed to refresh token, requesting new authorization...');
        await getNewToken(oAuth2Client);
      }
    } else {
      console.log('✓ Using existing token');
    }
  } else {
    await getNewToken(oAuth2Client);
  }

  return google.calendar({ version: 'v3', auth: oAuth2Client });
}

/**
 * Run this file directly to perform initial authorization
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  authorize()
    .then(() => {
      console.log('\n==========================================================');
      console.log('Authorization complete! You can now run the agent.');
      console.log('==========================================================\n');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Error during authorization:', error);
      process.exit(1);
    });
}
