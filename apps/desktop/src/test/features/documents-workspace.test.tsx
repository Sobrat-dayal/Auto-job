import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { DocumentsWorkspace } from '@/features/documents/DocumentsWorkspace';
import { apiClient } from '@/lib/api-client';

describe('DocumentsWorkspace', () => {
  beforeEach(() => {
    vi.spyOn(apiClient, 'listArtifacts').mockResolvedValue({
      items: [
        {
          id: 'art-1',
          artifact_type: 'resume_pdf',
          storage_path: 'vault/resumes/staff_systems_v1.pdf',
          file_size: 204800,
          checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
          related_task_id: null,
          related_profile_id: null,
          related_application_id: null,
          retention_class: 'permanent',
          created_at: new Date().toISOString(),
        },
      ],
      total: 1,
      limit: 50,
      offset: 0,
    });
  });

  it('renders artifacts list and file size metadata', async () => {
    render(
      <MemoryRouter initialEntries={['/documents/workspace']}>
        <DocumentsWorkspace />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Documents & Artifacts Storage'
    );

    await waitFor(() => {
      expect(screen.getByText('staff_systems_v1.pdf')).toBeInTheDocument();
      expect(screen.getByText('vault/resumes/staff_systems_v1.pdf')).toBeInTheDocument();
      expect(screen.getByText('200.0 KB')).toBeInTheDocument();
    });
  });
});
