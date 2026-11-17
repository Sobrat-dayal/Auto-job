import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryWorkspace } from '@/features/memory/MemoryWorkspace';
import { apiClient } from '@/lib/api-client';

describe('MemoryWorkspace (Stage 15)', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.spyOn(apiClient, 'getMemoryStatus').mockResolvedValue({
      total_records: 42,
      by_type: { semantic: 25, episodic: 10, procedural: 5, working: 2 },
      by_verification_status: { verified: 30, user_confirmed: 8, unverified: 4 },
      by_scope: { applicant_profile: 20, user: 15, project: 7 },
      indexed_records: 40,
      pending_embeddings: 2,
      conflicts_unresolved: 1,
      active_procedures: 5,
      vector_dimension: 384,
      fts_enabled: true,
    });

    vi.spyOn(apiClient, 'listMemories').mockResolvedValue([
      {
        id: 'mem_skill_rust',
        memory_type: 'semantic',
        title: 'Verified Skill: Rust Systems',
        content: 'Candidate has 5 years of production Rust experience with async Tokio.',
        summary: 'Rust expertise',
        owner_scope: 'applicant_profile',
        scope_id: 'app_101',
        source_type: 'verified_profile',
        source_ref: 'resume_pdf',
        provenance: {},
        verification_status: 'verified',
        confidence_category: 'high',
        sensitivity_category: 'internal',
        visibility_policy: 'scoped',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_accessed_at: new Date().toISOString(),
        version: 1,
        embedding_model_id: 'local-minilm-l6',
        embedding_version: 1,
        embedding_status: 'completed',
        content_checksum: 'abc123sha',
        retention_policy: 'permanent',
        is_deleted: false,
        metadata: {},
      },
    ]);

    vi.spyOn(apiClient, 'listMemoryConflicts').mockResolvedValue([
      {
        id: 'cnf_101',
        memory_id_a: 'mem_salary_old',
        memory_id_b: 'mem_salary_new',
        conflict_type: 'contradiction',
        description: 'Contradicting salary expectations stated',
        status: 'unresolved',
        created_at: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'listProceduralMemories').mockResolvedValue([
      {
        id: 'proc_doc_ocr',
        procedure_id: 'proc_ocr_extract',
        name: 'Document Text & OCR Extraction',
        description: 'Multi-stage fallback for text extraction from PDF files.',
        capability_id: 'structured_extract',
        required_inputs: {},
        steps: [
          { name: 'Extract Text Layer', action: 'pdf_extract' },
          { name: 'OCR Fallback', action: 'ocr_scan' },
        ],
        preconditions: {},
        expected_outputs: {},
        verification_requirements: {},
        required_permissions: ['capability:structured_extract'],
        provenance: {},
        version: 1,
        validation_status: 'validated',
        success_count: 12,
        failure_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]);

    vi.spyOn(apiClient, 'searchMemory').mockResolvedValue({
      results: [
        {
          memory_id: 'mem_skill_rust',
          title: 'Verified Skill: Rust Systems',
          content_snippet: 'Candidate has 5 years of production Rust experience with async Tokio.',
          memory_type: 'semantic',
          owner_scope: 'applicant_profile',
          scope_id: 'app_101',
          verification_status: 'verified',
          sensitivity_category: 'internal',
          similarity_score: 0.88,
          keyword_score: 0.75,
          combined_score: 0.92,
          provenance: {},
          created_at: new Date().toISOString(),
        },
      ],
      query: 'Rust developer',
      search_mode: 'hybrid',
      total_matched: 1,
      latency_ms: 12.4,
    });
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <MemoryWorkspace />
        </MemoryRouter>
      </QueryClientProvider>
    );

  it('renders overview dashboard with real storage and index telemetry', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Agent Memory & Knowledge Engine')).toBeInTheDocument();
      expect(screen.getByText('Total Stored Memories')).toBeInTheDocument();
      expect(screen.getAllByText('42').length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('40')).toBeInTheDocument(); // active vector index
    });
  });

  it('navigates to Memory Explorer tab and displays memory records', async () => {
    renderComponent();

    const explorerTab = screen.getByRole('tab', { name: /Memory Explorer/i });
    fireEvent.click(explorerTab);

    await waitFor(() => {
      expect(screen.getByText('Verified Skill: Rust Systems')).toBeInTheDocument();
      expect(screen.getByText('applicant_profile:app_101')).toBeInTheDocument();
    });
  });

  it('executes hybrid search and displays ranked results with score badges', async () => {
    renderComponent();

    const searchTab = screen.getByRole('tab', { name: /Semantic & Hybrid Search/i });
    fireEvent.click(searchTab);

    const input = screen.getByPlaceholderText(/Search memories via semantic intent/i);
    fireEvent.change(input, { target: { value: 'Rust developer' } });

    const searchBtn = screen.getByRole('button', { name: /^Search$/i });
    fireEvent.click(searchBtn);

    await waitFor(() => {
      expect(apiClient.searchMemory).toHaveBeenCalledWith(
        expect.objectContaining({
          query: 'Rust developer',
          search_mode: 'hybrid',
        })
      );
      expect(screen.getByText('Score: 92%')).toBeInTheDocument();
      expect(screen.getByText('Vec: 88%')).toBeInTheDocument();
    });
  });

  it('displays procedural memories and workflow steps', async () => {
    renderComponent();

    const procTab = screen.getByRole('tab', { name: /Procedural Knowledge/i });
    fireEvent.click(procTab);

    await waitFor(() => {
      expect(screen.getByText('Document Text & OCR Extraction')).toBeInTheDocument();
      expect(screen.getByText('Capability:')).toBeInTheDocument();
      expect(screen.getByText('structured_extract')).toBeInTheDocument();
      expect(screen.getByText('Extract Text Layer')).toBeInTheDocument();
    });
  });

  it('displays memory conflict review panel with action triggers', async () => {
    renderComponent();

    const conflictTab = screen.getByRole('tab', { name: /Conflict Review/i });
    fireEvent.click(conflictTab);

    await waitFor(() => {
      expect(screen.getByText(/CONTRADICTION: Contradicting salary expectations stated/i)).toBeInTheDocument();
      expect(screen.getByText('Supersede Older Record')).toBeInTheDocument();
      expect(screen.getByText('Dismiss Conflict')).toBeInTheDocument();
    });
  });
});
