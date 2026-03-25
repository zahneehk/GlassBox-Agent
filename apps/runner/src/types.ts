/**
 * GlassBox Runner — Action Protocol Types
 * Fixed protocol as specified.
 */

export interface ActionRequest {
  task_id: string;
  step_id: string;
  action: 'goto' | 'click' | 'type' | 'press' | 'wait_for' | 'extract_text' | 'screenshot';
  selector: string | null;
  value: string | null;
  risk: 'low' | 'medium' | 'high';
  timeout_ms: number;
}

export interface ActionResult {
  success: boolean;
  step_id: string;
  data?: Record<string, unknown>;
  error?: string;
}
