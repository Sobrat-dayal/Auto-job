import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComputerWorkspace } from '@/features/computer/ComputerWorkspace';
import { apiClient } from '@/lib/api-client';
import type {
  RecordingSession,
  ReusableProcedure,
  ProcedureExecution,
  ExecutionCheckpoint,
  RecoveryPlan,
  ReliabilityDiagnosticsInfo,
  PreflightReport,
} from '@autonom/shared-types';

describe('Workflow Reliability & Computer Action Recording (Stage 20)', () => {
  let queryClient: QueryClient;

  const mockDiagnostics: ReliabilityDiagnosticsInfo = {
    service_status: 'operational',
    active_recording_sessions: 1,
    total_registered_procedures: 8,
    active_executions: 0,
    total_checkpoints_preserved: 42,
    tracked_side_effects_count: 14,
    emergency_stop_triggered: false,
    interrupted_executions_found: 1,
  };

  const mockRecordingSession: RecordingSession = {
    session_id: 'recsess_test_100',
    name: 'LinkedIn Job Application Flow',
    status: 'active',
    mode: 'supervised',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    allowed_app_scopes: ['notepad.exe', 'msedge.exe'],
    allowed_web_origins: ['https://jobs.example.com'],
    actions: [
      {
        action_id: 'act_1',
        session_id: 'recsess_test_100',
        sequence_number: 1,
        timestamp: new Date().toISOString(),
        source_adapter: 'desktop',
        action_type: 'type_text',
        raw_parameters: { text: 'Senior Engineer' },
        normalized_parameters: { text: 'Senior Engineer' },
        application_name: 'notepad.exe',
        is_sensitive: false,
      },
    ],
    captured_actions_count: 1,
  };

  const mockProcedure: ReusableProcedure = {
    procedure_id: 'proc_apply_flow',
    version: 1,
    name: 'One-Click Apply Flow',
    description: 'Fills applicant profile and clicks apply',
    category: 'recruitment',
    is_draft: false,
    is_deprecated: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    parameters: [
      {
        name: 'applicant_name',
        type: 'string',
        default_value: 'Sobrat',
        required: true,
        is_secret: false,
      },
    ],
    steps: [
      {
        step_id: 'step_enter_name',
        order_index: 1,
        name: 'Enter Applicant Name',
        action_type: 'fill',
        target_surface: 'browser',
        locator_schema: { selector: 'input#name' },
        input_bindings: { text: '{{applicant_name}}' },
        side_effect_class: 'read_only',
        checkpoint_policy: 'per_step',
        preconditions: [],
        postconditions: [],
        timeout_ms: 5000,
        max_retries: 2,
        allow_failure: false,
      },
      {
        step_id: 'step_click_submit',
        order_index: 2,
        name: 'Submit Application',
        action_type: 'click',
        target_surface: 'browser',
        locator_schema: { selector: 'button#submit' },
        input_bindings: {},
        side_effect_class: 'non_idempotent',
        checkpoint_policy: 'per_side_effect',
        preconditions: [],
        postconditions: [],
        timeout_ms: 10000,
        max_retries: 1,
        allow_failure: false,
      },
    ],
    allowed_applications: ['msedge.exe'],
    allowed_origins: ['https://jobs.example.com'],
    required_permissions: ['browser:interact', 'recruitment_submit_application'],
    validation_status: 'valid',
    validation_issues: [],
    static_risk_score: 25,
  };

  const mockPreflight: PreflightReport = {
    can_execute: true,
    procedure_id: 'proc_apply_flow',
    version: 1,
    issues: [],
    missing_parameters: [],
    missing_permissions: [],
    required_adapters: ['browser'],
    adapters_ready: true,
    emergency_stop_active: false,
    session_locked: false,
    risk_assessment: { level: 'LOW' },
  };

  const mockExecution: ProcedureExecution = {
    execution_id: 'procexec_test_500',
    procedure_id: 'proc_apply_flow',
    version: 1,
    status: 'completed',
    mode: 'automatic_authorized',
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    current_step_index: 2,
    total_steps: 2,
    resolved_arguments: { applicant_name: 'Sobrat' },
    completed_steps: ['step_enter_name', 'step_click_submit'],
    failed_steps: [],
    execution_time_ms: 120,
    checkpoints: [
      {
        checkpoint_id: 'chk_test_1',
        execution_id: 'procexec_test_500',
        step_id: 'step_enter_name',
        step_index: 1,
        checkpoint_type: 'post_action',
        timestamp: new Date().toISOString(),
        state_fingerprint: {
          fingerprint_id: 'fp_1',
          timestamp: new Date().toISOString(),
          active_window_title: 'Job Portal - Edge',
          active_process_name: 'msedge.exe',
          browser_url: 'https://jobs.example.com/apply',
          extra_attributes: {},
        },
        scope_variables: { applicant_name: 'Sobrat' },
        completed_steps: ['step_enter_name'],
        integrity_hash: 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890',
        can_resume: true,
      },
    ],
    side_effects: [
      {
        effect_id: 'eff_test_1',
        execution_id: 'procexec_test_500',
        step_id: 'step_click_submit',
        side_effect_class: 'non_idempotent',
        outcome: 'confirmed',
        intent_hash: 'hash_intent_1234567890abcdef',
        target_system: 'https://jobs.example.com',
        operation: 'submit_application',
        parameters: { job_id: '999' },
        timestamp: new Date().toISOString(),
        response_evidence: { status_code: 200 },
      },
    ],
  };

  const mockInterruptedExecution: ProcedureExecution = {
    ...mockExecution,
    execution_id: 'procexec_interrupted_999',
    status: 'failed',
    completed_steps: ['step_enter_name'],
    error_message: 'Target button obscured by modal overlay',
  };

  const mockRecoveryPlan: RecoveryPlan = {
    plan_id: 'recplan_test_001',
    execution_id: 'procexec_interrupted_999',
    checkpoint_id: 'chk_test_1',
    classification: 'safe_to_retry',
    can_resume: true,
    resume_step_index: 2,
    actions_to_skip: ['step_enter_name'],
    actions_to_reexecute: ['step_click_submit'],
    rationale: 'Step 1 completed and verified. Safe to resume from step 2.',
    created_at: new Date().toISOString(),
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.spyOn(apiClient, 'getReliabilityDiagnostics').mockResolvedValue(mockDiagnostics);
    vi.spyOn(apiClient, 'listRecordings').mockResolvedValue([mockRecordingSession]);
    vi.spyOn(apiClient, 'getRecording').mockResolvedValue(mockRecordingSession);
    vi.spyOn(apiClient, 'startRecording').mockResolvedValue(mockRecordingSession);
    vi.spyOn(apiClient, 'pauseRecording').mockResolvedValue({ ...mockRecordingSession, status: 'paused' });
    vi.spyOn(apiClient, 'resumeRecording').mockResolvedValue(mockRecordingSession);
    vi.spyOn(apiClient, 'stopRecording').mockResolvedValue({ ...mockRecordingSession, status: 'stopped', integrity_hash: 'abcdef1234567890' });
    vi.spyOn(apiClient, 'listProcedures').mockResolvedValue([mockProcedure]);
    vi.spyOn(apiClient, 'getProcedure').mockResolvedValue(mockProcedure);
    vi.spyOn(apiClient, 'preflightProcedure').mockResolvedValue(mockPreflight);
    vi.spyOn(apiClient, 'executeProcedure').mockResolvedValue(mockExecution);
    vi.spyOn(apiClient, 'listExecutions').mockResolvedValue([mockInterruptedExecution, mockExecution]);
    vi.spyOn(apiClient, 'listExecutionCheckpoints').mockResolvedValue(mockExecution.checkpoints);
    vi.spyOn(apiClient, 'getRecoveryPlan').mockResolvedValue(mockRecoveryPlan);
    vi.spyOn(apiClient, 'resumeExecution').mockResolvedValue(mockExecution);
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/computer/reliability']}>
          <ComputerWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders Stage 20 badges and Workflow Reliability workspace', async () => {
    renderComponent();

    // Verify stage and operational badges
    expect(screen.getByText('Stage 20 Production Active')).toBeInTheDocument();
    expect(screen.getByText('Reliability: Operational')).toBeInTheDocument();
    expect(screen.getByText('Stage 19 Production Active')).toBeInTheDocument();
    expect(screen.getByText('Stage 18 Production Active')).toBeInTheDocument();
    expect(screen.getByText('Stage 17 Production Active')).toBeInTheDocument();

    // Verify reliability workspace container
    await waitFor(() => {
      expect(screen.getByTestId('workflow-reliability-workspace')).toBeInTheDocument();
    });
  });

  it('renders Action Recording Studio and allows pausing/resuming recording', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByTestId('recording-studio-tab')).toBeInTheDocument();
      expect(screen.getByText('Action Recording Studio')).toBeInTheDocument();
      expect(screen.getByText('LIVE RECORDING')).toBeInTheDocument();
    });

    // Pause recording
    const pauseBtn = screen.getByTestId('pause-recording-btn');
    fireEvent.click(pauseBtn);

    await waitFor(() => {
      expect(apiClient.pauseRecording).toHaveBeenCalledWith('recsess_test_100');
    });
  });

  it('navigates to Procedure Library and displays procedures and preflight checks', async () => {
    renderComponent();

    const libTabBtn = await screen.findByTestId('reliability-subtab-library');
    fireEvent.click(libTabBtn);

    await waitFor(() => {
      expect(screen.getByTestId('procedure-library-tab')).toBeInTheDocument();
      expect(screen.getByText('One-Click Apply Flow')).toBeInTheDocument();
    });

    // Preflight button click
    const preflightBtn = screen.getByTestId('preflight-procedure-proc_apply_flow');
    fireEvent.click(preflightBtn);

    await waitFor(() => {
      expect(apiClient.preflightProcedure).toHaveBeenCalledWith('proc_apply_flow', {}, 1);
    });
  });

  it('navigates to Procedure Editor and inspects parameters, steps, and risk audit', async () => {
    renderComponent();

    // Open Library then click inspect
    const libTabBtn = await screen.findByTestId('reliability-subtab-library');
    fireEvent.click(libTabBtn);

    const inspectBtn = await screen.findByTestId('inspect-procedure-proc_apply_flow');
    fireEvent.click(inspectBtn);

    await waitFor(() => {
      expect(screen.getByTestId('procedure-editor-tab')).toBeInTheDocument();
      expect(screen.getByText('{{applicant_name}}')).toBeInTheDocument();
      expect(screen.getByText('Enter Applicant Name')).toBeInTheDocument();
      expect(screen.getByText('Submit Application')).toBeInTheDocument();
      expect(screen.getByText(/25 \/ 100/)).toBeInTheDocument();
    });
  });

  it('navigates to State-Aware Replay tab and executes procedure in dry-run mode', async () => {
    renderComponent();

    const replayTabBtn = await screen.findByTestId('reliability-subtab-replay');
    fireEvent.click(replayTabBtn);

    await waitFor(() => {
      expect(screen.getByTestId('replay-inspector-tab')).toBeInTheDocument();
    });

    const procInput = screen.getByTestId('replay-procedure-id-input');
    fireEvent.change(procInput, { target: { value: 'proc_apply_flow' } });

    const modeSelect = screen.getByTestId('replay-mode-select');
    fireEvent.change(modeSelect, { target: { value: 'dry_run' } });

    const executeBtn = screen.getByTestId('start-replay-btn');
    fireEvent.click(executeBtn);

    await waitFor(() => {
      expect(apiClient.executeProcedure).toHaveBeenCalledWith(
        'proc_apply_flow',
        {},
        1,
        'dry_run'
      );
      expect(screen.getByTestId('execution-status-badge')).toHaveTextContent('completed');
    });
  });

  it('navigates to Checkpoints Timeline and displays state fingerprints and SHA-256 hashes', async () => {
    renderComponent();

    const cpTabBtn = await screen.findByTestId('reliability-subtab-checkpoints');
    fireEvent.click(cpTabBtn);

    await waitFor(() => {
      expect(screen.getByTestId('checkpoint-timeline-tab')).toBeInTheDocument();
      expect(screen.getByTestId('checkpoint-card-1')).toBeInTheDocument();
      expect(screen.getByText(/Job Portal - Edge/)).toBeInTheDocument();
      expect(screen.getByText(/msedge\.exe/)).toBeInTheDocument();
      expect(screen.getByText(/Resume Eligible/)).toBeInTheDocument();
    });
  });

  it('navigates to Recovery Center and displays automated recovery plan with safe resume', async () => {
    renderComponent();

    const recTabBtn = await screen.findByTestId('reliability-subtab-recovery');
    fireEvent.click(recTabBtn);

    await waitFor(() => {
      expect(screen.getByTestId('recovery-center-tab')).toBeInTheDocument();
      expect(screen.getByTestId('interrupted-item-procexec_interrupted_999')).toBeInTheDocument();
      expect(screen.getByText(/safe_to_retry/)).toBeInTheDocument();
      expect(screen.getByText('step_enter_name')).toBeInTheDocument();
      expect(screen.getByText('step_click_submit')).toBeInTheDocument();
    });

    // Click resume button
    const resumeBtn = screen.getByTestId('resume-execution-btn');
    fireEvent.click(resumeBtn);

    await waitFor(() => {
      expect(apiClient.resumeExecution).toHaveBeenCalledWith('procexec_interrupted_999');
    });
  });
});
