import * as dotenv from 'dotenv';
import * as readline from 'readline';
import { runCalendarAgent } from './agent.js';

dotenv.config();

/**
 * Interactive mode - run the agent in a REPL loop
 */
async function interactiveMode() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log('\n' + '='.repeat(60));
  console.log('Google Calendar Agent - Interactive Mode');
  console.log('='.repeat(60));
  console.log('\nType your requests or "quit" to exit.\n');
  console.log('Examples:');
  console.log('  - "What are my meetings today?"');
  console.log('  - "Create a meeting tomorrow at 2pm for 1 hour"');
  console.log('  - "Search for events about project review"');
  console.log('='.repeat(60) + '\n');

  const askQuestion = () => {
    rl.question('You: ', async (input) => {
      const trimmed = input.trim();

      if (trimmed.toLowerCase() === 'quit' || trimmed.toLowerCase() === 'exit') {
        console.log('\nGoodbye!\n');
        rl.close();
        return;
      }

      if (!trimmed) {
        askQuestion();
        return;
      }

      try {
        await runCalendarAgent(trimmed);
      } catch (error) {
        console.error('\nError:', error instanceof Error ? error.message : String(error));
      }

      askQuestion();
    });
  };

  askQuestion();
}

/**
 * Single query mode - run one query and exit
 */
async function singleQueryMode(query: string) {
  try {
    await runCalendarAgent(query);
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

/**
 * Main entry point
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length > 0) {
    // Single query mode
    const query = args.join(' ');
    await singleQueryMode(query);
  } else {
    // Interactive mode
    await interactiveMode();
  }
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
