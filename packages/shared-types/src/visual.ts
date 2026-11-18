/**
 * Shared TypeScript definitions for Visual Computer Automation (Stage 18).
 */

export type CaptureProviderType = 'mss' | 'gdi' | 'wgc';
export type CaptureTargetType = 'display' | 'window';
export type CaptureSessionState = 'idle' | 'capturing' | 'paused' | 'closed';

export type VisualActionType =
  | 'click'
  | 'double_click'
  | 'right_click'
  | 'move'
  | 'enter_text'
  | 'press_key'
  | 'scroll'
  | 'drag_and_drop'
  | 'wait';

export type VisualTaskStatus =
  | 'pending'
  | 'observing'
  | 'grounding'
  | 'acting'
  | 'verifying'
  | 'recovering'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'paused';

export type VisualVerificationStatus = 'verified' | 'failed' | 'uncertain' | 'skipped';

export type ElementCategory =
  | 'button'
  | 'input'
  | 'text'
  | 'link'
  | 'icon'
  | 'image'
  | 'checkbox'
  | 'radio'
  | 'dropdown'
  | 'menu'
  | 'window'
  | 'unknown';

export interface Point2D {
  x: number;
  y: number;
}

export interface BoundingBox {
  left: number;
  top: number;
  width: number;
  height: number;
}

export interface NormalizedBox {
  ymin: number;
  xmin: number;
  ymax: number;
  xmax: number;
}

export interface DisplayInfo {
  display_index: number;
  name: string;
  width: number;
  height: number;
  left: number;
  top: number;
  right: number;
  bottom: number;
  is_primary: boolean;
  scale_factor: number;
  dpi: number;
}

export interface FrameMetadata {
  frame_id: string;
  session_id: string;
  timestamp: string;
  target_type: string;
  target_hwnd?: number;
  display_index?: number;
  width: number;
  height: number;
  dpi_scale: number;
  content_hash: string;
}

export interface OCRWord {
  text: string;
  bounding_box: BoundingBox;
  confidence: number;
}

export interface OCRLine {
  text: string;
  words: OCRWord[];
  bounding_box: BoundingBox;
}

export interface OCRResult {
  text: string;
  lines: OCRLine[];
  duration_ms: number;
}

export interface VisualElementDetection {
  frame_id: string;
  category: ElementCategory;
  label?: string;
  bounding_box: BoundingBox;
  normalized_box: NormalizedBox;
  confidence: number;
  source: string;
}

export interface VisualGroundingResult {
  success: boolean;
  query: string;
  target_point?: Point2D;
  bounding_box?: BoundingBox;
  category?: ElementCategory;
  confidence: number;
  explanation: string;
  disambiguation_count?: number;
}

export interface VisualActionRequest {
  action_type: VisualActionType;
  target_point?: Point2D;
  target_element?: string;
  text?: string;
  key?: string;
  button?: string;
  click_count?: number;
  drag_target?: Point2D;
  scroll_amount?: number;
  wait_seconds?: number;
  expected_change?: string;
  wait_for_render?: boolean;
}

export interface VisualActionResult {
  success: boolean;
  action_type: VisualActionType;
  execution_time_ms: number;
  verification_status: VisualVerificationStatus;
  visual_difference: number;
  verification_notes?: string;
  post_action_frame_id?: string;
  error_message?: string;
}

export interface VisualDiagnosticsInfo {
  active_provider: CaptureProviderType;
  available_providers: CaptureProviderType[];
  active_sessions_count: number;
  monitors_count: number;
  primary_display_resolution: string;
  dpi_scaling_factor: number;
  offline_windows_ocr_available: boolean;
  vlm_grounding_available: boolean;
  gpu_acceleration: boolean;
  last_capture_latency_ms: number;
  last_ocr_latency_ms: number;
  active_emergency_stop: boolean;
}

export interface CaptureSessionCreateRequest {
  target_type?: CaptureTargetType;
  target_hwnd?: number;
  display_index?: number;
  provider?: CaptureProviderType;
  frame_rate_limit?: number;
}

export interface CaptureSessionResponse {
  session_id: string;
  target_type: CaptureTargetType;
  target_hwnd?: number;
  display_index?: number;
  provider: CaptureProviderType;
  state: CaptureSessionState;
  frame_rate_limit: number;
  frames_captured: number;
  created_at: string;
  updated_at: string;
}

export interface VisualTaskRequest {
  instruction: string;
  session_id?: string;
  target_type?: CaptureTargetType;
  target_hwnd?: number;
  display_index?: number;
  provider?: CaptureProviderType;
  timeout_seconds?: number;
}

export interface VisualTaskResponse {
  task_id: string;
  status: VisualTaskStatus;
  instruction: string;
  created_at: string;
  updated_at: string;
  steps_completed: number;
  total_steps: number;
  result_summary?: string;
  error_message?: string;
}
