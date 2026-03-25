/**
 * GlassBox Runner — Action handlers.
 * 7 actions: goto, click, type, press, wait_for, extract_text, screenshot.
 */
import { Page } from 'playwright';
import { ActionRequest, ActionResult } from '../types.js';

type ActionHandler = (page: Page, req: ActionRequest) => Promise<ActionResult>;

// ── goto ────────────────────────────────────────────────────────
const handleGoto: ActionHandler = async (page, req) => {
  if (!req.value) return { success: false, step_id: req.step_id, error: 'goto requires value (URL)' };
  const resp = await page.goto(req.value, { timeout: req.timeout_ms, waitUntil: 'domcontentloaded' });
  return {
    success: true,
    step_id: req.step_id,
    data: { url: page.url(), status: resp?.status() ?? null },
  };
};

// ── click ───────────────────────────────────────────────────────
const handleClick: ActionHandler = async (page, req) => {
  if (!req.selector) return { success: false, step_id: req.step_id, error: 'click requires selector' };
  await page.click(req.selector, { timeout: req.timeout_ms });
  return { success: true, step_id: req.step_id, data: { selector: req.selector } };
};

// ── type ────────────────────────────────────────────────────────
const handleType: ActionHandler = async (page, req) => {
  if (!req.selector) return { success: false, step_id: req.step_id, error: 'type requires selector' };
  if (req.value === null) return { success: false, step_id: req.step_id, error: 'type requires value' };
  await page.fill(req.selector, req.value, { timeout: req.timeout_ms });
  return { success: true, step_id: req.step_id, data: { selector: req.selector, typed: req.value } };
};

// ── press ───────────────────────────────────────────────────────
const handlePress: ActionHandler = async (page, req) => {
  if (!req.value) return { success: false, step_id: req.step_id, error: 'press requires value (key)' };
  if (req.selector) {
    await page.press(req.selector, req.value, { timeout: req.timeout_ms });
  } else {
    await page.keyboard.press(req.value);
  }
  return { success: true, step_id: req.step_id, data: { key: req.value } };
};

// ── wait_for ────────────────────────────────────────────────────
const handleWaitFor: ActionHandler = async (page, req) => {
  if (!req.selector) return { success: false, step_id: req.step_id, error: 'wait_for requires selector' };
  await page.waitForSelector(req.selector, { timeout: req.timeout_ms, state: 'visible' });
  return { success: true, step_id: req.step_id, data: { selector: req.selector, found: true } };
};

// ── extract_text ────────────────────────────────────────────────
const handleExtractText: ActionHandler = async (page, req) => {
  if (!req.selector) return { success: false, step_id: req.step_id, error: 'extract_text requires selector' };
  const el = await page.waitForSelector(req.selector, { timeout: req.timeout_ms });
  const text = el ? await el.textContent() : null;
  return { success: true, step_id: req.step_id, data: { selector: req.selector, text: text ?? '' } };
};

// ── screenshot ──────────────────────────────────────────────────
const handleScreenshot: ActionHandler = async (page, req) => {
  const buffer = await page.screenshot({ type: 'png', fullPage: false });
  const base64 = buffer.toString('base64');
  return {
    success: true,
    step_id: req.step_id,
    data: { format: 'png', base64, size: buffer.length },
  };
};

// ── Registry ────────────────────────────────────────────────────
const ACTION_MAP: Record<string, ActionHandler> = {
  goto: handleGoto,
  click: handleClick,
  type: handleType,
  press: handlePress,
  wait_for: handleWaitFor,
  extract_text: handleExtractText,
  screenshot: handleScreenshot,
};

export async function executeAction(page: Page, req: ActionRequest): Promise<ActionResult> {
  const handler = ACTION_MAP[req.action];
  if (!handler) {
    return { success: false, step_id: req.step_id, error: `Unknown action: ${req.action}` };
  }
  try {
    return await handler(page, req);
  } catch (err: any) {
    return { success: false, step_id: req.step_id, error: err.message || String(err) };
  }
}
