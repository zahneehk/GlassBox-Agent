// GlassBox Runner — Node.js + Playwright execution engine
import { createServer } from './server/http';

async function main() {
  console.log('[GlassBox Runner] starting...');
  const server = await createServer();
  console.log('[GlassBox Runner] ready');
}

main().catch(console.error);
