/**
 * GlassBox Runner — HTTP server.
 * Receives action commands from Orchestrator, executes via Playwright.
 */
import express from 'express';
import { getPage } from '../browser/index.js';
import { executeAction } from '../actions/index.js';
import { ActionRequest } from '../types.js';

const RUNNER_PORT = parseInt(process.env.RUNNER_PORT || '3001', 10);

export async function createServer() {
  const app = express();
  app.use(express.json());

  // Health / status
  app.get('/status', (_req, res) => {
    const page = getPage();
    res.json({
      status: 'ready',
      run_id: process.env.RUN_ID || null,
      current_url: page ? page.url() : null,
    });
  });

  // Execute action
  app.post('/actions/execute', async (req, res) => {
    const page = getPage();
    if (!page) {
      return res.status(503).json({ success: false, error: 'Browser not ready' });
    }

    const actionReq: ActionRequest = req.body;
    console.log(`[runner] executing: ${actionReq.action} | selector=${actionReq.selector} | step=${actionReq.step_id}`);

    const result = await executeAction(page, actionReq);
    console.log(`[runner] result: ${result.success ? 'OK' : 'FAIL'} | ${result.error || ''}`);

    res.json(result);
  });

  // Screenshot (convenience endpoint)
  app.get('/screenshot', async (_req, res) => {
    const page = getPage();
    if (!page) {
      return res.status(503).json({ error: 'Browser not ready' });
    }
    const buffer = await page.screenshot({ type: 'png' });
    res.setHeader('Content-Type', 'image/png');
    res.send(buffer);
  });

  app.listen(RUNNER_PORT, '0.0.0.0', () => {
    console.log(`[runner] HTTP server on port ${RUNNER_PORT}`);
  });

  return app;
}
