import Anthropic from '@anthropic-ai/sdk';
import { calendar_v3 } from 'googleapis';
import { authorize } from './auth.js';

// Tool definitions for Claude
const tools: Anthropic.Tool[] = [
  {
    name: 'list_events',
    description: 'List upcoming events from Google Calendar. Returns events sorted by start time.',
    input_schema: {
      type: 'object',
      properties: {
        max_results: {
          type: 'number',
          description: 'Maximum number of events to return (default: 10)',
        },
        days_ahead: {
          type: 'number',
          description: 'Number of days ahead to look for events (default: 7)',
        },
      },
      required: [],
    },
  },
  {
    name: 'create_event',
    description: 'Create a new event in Google Calendar',
    input_schema: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          description: 'Event title/summary',
        },
        description: {
          type: 'string',
          description: 'Event description (optional)',
        },
        start_time: {
          type: 'string',
          description: 'Start time in ISO 8601 format (e.g., 2025-12-25T14:00:00-08:00)',
        },
        end_time: {
          type: 'string',
          description: 'End time in ISO 8601 format (e.g., 2025-12-25T15:00:00-08:00)',
        },
        attendees: {
          type: 'array',
          items: { type: 'string' },
          description: 'List of attendee email addresses (optional)',
        },
        location: {
          type: 'string',
          description: 'Event location (optional)',
        },
      },
      required: ['title', 'start_time', 'end_time'],
    },
  },
  {
    name: 'search_events',
    description: 'Search for events by keyword in title or description',
    input_schema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query to match against event titles and descriptions',
        },
        max_results: {
          type: 'number',
          description: 'Maximum number of results to return (default: 20)',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'delete_event',
    description: 'Delete an event from Google Calendar by event ID',
    input_schema: {
      type: 'object',
      properties: {
        event_id: {
          type: 'string',
          description: 'The ID of the event to delete',
        },
      },
      required: ['event_id'],
    },
  },
];

/**
 * Handle tool calls from Claude
 */
async function handleToolCall(
  calendar: calendar_v3.Calendar,
  toolName: string,
  toolInput: Record<string, any>
): Promise<string> {
  try {
    switch (toolName) {
      case 'list_events': {
        const maxResults = toolInput.max_results || 10;
        const daysAhead = toolInput.days_ahead || 7;
        const timeMin = new Date();
        const timeMax = new Date();
        timeMax.setDate(timeMax.getDate() + daysAhead);

        const response = await calendar.events.list({
          calendarId: 'primary',
          timeMin: timeMin.toISOString(),
          timeMax: timeMax.toISOString(),
          maxResults,
          singleEvents: true,
          orderBy: 'startTime',
        });

        const events = response.data.items || [];

        if (events.length === 0) {
          return 'No upcoming events found.';
        }

        const formatted = events.map((event) => ({
          id: event.id,
          title: event.summary,
          start: event.start?.dateTime || event.start?.date,
          end: event.end?.dateTime || event.end?.date,
          location: event.location,
          attendees: event.attendees?.map((a) => a.email),
          description: event.description,
        }));

        return JSON.stringify(formatted, null, 2);
      }

      case 'create_event': {
        const event: calendar_v3.Schema$Event = {
          summary: toolInput.title,
          description: toolInput.description,
          location: toolInput.location,
          start: {
            dateTime: toolInput.start_time,
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          },
          end: {
            dateTime: toolInput.end_time,
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          },
        };

        if (toolInput.attendees && Array.isArray(toolInput.attendees)) {
          event.attendees = toolInput.attendees.map((email: string) => ({ email }));
        }

        const response = await calendar.events.insert({
          calendarId: 'primary',
          requestBody: event,
        });

        return `Event created successfully! Event ID: ${response.data.id}, Title: "${response.data.summary}", Start: ${response.data.start?.dateTime}`;
      }

      case 'search_events': {
        const maxResults = toolInput.max_results || 20;

        const response = await calendar.events.list({
          calendarId: 'primary',
          q: toolInput.query,
          maxResults,
          singleEvents: true,
          orderBy: 'startTime',
        });

        const events = response.data.items || [];

        if (events.length === 0) {
          return `No events found matching "${toolInput.query}".`;
        }

        const formatted = events.map((event) => ({
          id: event.id,
          title: event.summary,
          start: event.start?.dateTime || event.start?.date,
          end: event.end?.dateTime || event.end?.date,
          description: event.description,
        }));

        return JSON.stringify(formatted, null, 2);
      }

      case 'delete_event': {
        await calendar.events.delete({
          calendarId: 'primary',
          eventId: toolInput.event_id,
        });

        return `Event ${toolInput.event_id} deleted successfully.`;
      }

      default:
        return `Unknown tool: ${toolName}`;
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return `Error executing ${toolName}: ${errorMessage}`;
  }
}

/**
 * Run the Google Calendar agent
 */
export async function runCalendarAgent(userMessage: string): Promise<string> {
  // Initialize Google Calendar
  const calendar = await authorize();

  // Initialize Anthropic client
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY environment variable not set');
  }

  const anthropic = new Anthropic({ apiKey });

  // Initialize messages
  const messages: Anthropic.MessageParam[] = [
    {
      role: 'user',
      content: userMessage,
    },
  ];

  console.log('\n' + '='.repeat(60));
  console.log('Google Calendar Agent');
  console.log('='.repeat(60));
  console.log(`\nUser: ${userMessage}\n`);
  console.log('Agent: ', { lineBreak: false });

  let finalResponse = '';

  // Agent loop
  while (true) {
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      tools,
      messages,
    });

    // Add assistant response to messages
    messages.push({
      role: 'assistant',
      content: response.content,
    });

    // Process response content
    for (const block of response.content) {
      if (block.type === 'text') {
        process.stdout.write(block.text);
        finalResponse += block.text;
      }
    }

    // Check if we're done
    if (response.stop_reason === 'end_turn') {
      console.log('\n' + '='.repeat(60) + '\n');
      break;
    }

    // Process tool calls
    if (response.stop_reason === 'tool_use') {
      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const block of response.content) {
        if (block.type === 'tool_use') {
          console.log(`\n[Using tool: ${block.name}]`);

          const result = await handleToolCall(calendar, block.name, block.input as Record<string, any>);

          toolResults.push({
            type: 'tool_result',
            tool_use_id: block.id,
            content: result,
          });
        }
      }

      // Add tool results to messages
      messages.push({
        role: 'user',
        content: toolResults,
      });
    }
  }

  return finalResponse;
}
