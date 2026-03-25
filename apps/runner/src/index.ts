/**
 * GlassBox Runner — Entry point.
 * Launches browser, starts HTTP server.
 */
import { launchBrowser } from './browser/index.js';
import { createServer } from './server/http.js';

async function main() {
  console.log('[GlassBox Runner] starting...');
  console.log(`[GlassBox Runner] RUN_ID=${process.env.RUN_ID || 'none'}`);
  console.log(`[GlassBox Runner] DISPLAY=${process.env.DISPLAY || 'not set'}`);

  // 1. Launch browser (headless=false, visible on Xvfb)
  await launchBrowser();

  // 2. Start HTTP server for action commands
  await createServer();

  console.log('[GlassBox Runner] ready — waiting for actions');
}

main().catch((err) => {
  console.error('[GlassBox Runner] fatal:', err);
  process.exit(1);
});
