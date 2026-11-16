import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/data-display/DataTable';

interface TestItem {
  id: string;
  name: string;
  role: string;
}

const TEST_COLUMNS: ColumnDef<TestItem>[] = [
  { accessorKey: 'id', header: 'ID' },
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'role', header: 'Role' },
];

const TEST_DATA: TestItem[] = [
  { id: '1', name: 'Alpha Agent', role: 'Scout' },
  { id: '2', name: 'Beta Agent', role: 'Tailor' },
  { id: '3', name: 'Gamma Agent', role: 'Submitter' },
  { id: '4', name: 'Delta Agent', role: 'Supervisor' },
];

describe('DataTable Component', () => {
  it('renders data table with column headers and rows', () => {
    render(<DataTable columns={TEST_COLUMNS} data={TEST_DATA} pageSize={10} />);

    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Role')).toBeInTheDocument();

    expect(screen.getByText('Alpha Agent')).toBeInTheDocument();
    expect(screen.getByText('Beta Agent')).toBeInTheDocument();
    expect(screen.getByText('Gamma Agent')).toBeInTheDocument();
    expect(screen.getByText('Delta Agent')).toBeInTheDocument();
  });

  it('filters data rows using global search input', () => {
    render(
      <DataTable columns={TEST_COLUMNS} data={TEST_DATA} searchPlaceholder="Search agents..." />
    );

    const searchInput = screen.getByPlaceholderText('Search agents...');
    expect(searchInput).toBeInTheDocument();

    // Type filter
    fireEvent.change(searchInput, { target: { value: 'Beta' } });

    expect(screen.getByText('Beta Agent')).toBeInTheDocument();
    expect(screen.queryByText('Alpha Agent')).not.toBeInTheDocument();
    expect(screen.queryByText('Gamma Agent')).not.toBeInTheDocument();
  });

  it('handles empty data state', () => {
    render(<DataTable columns={TEST_COLUMNS} data={[]} emptyMessage="No agents found." />);
    expect(screen.getByText('No agents found.')).toBeInTheDocument();
  });

  it('paginates data when pageSize is less than item count', () => {
    render(<DataTable columns={TEST_COLUMNS} data={TEST_DATA} pageSize={2} />);

    // Page 1: Alpha & Beta
    expect(screen.getByText('Alpha Agent')).toBeInTheDocument();
    expect(screen.getByText('Beta Agent')).toBeInTheDocument();
    expect(screen.queryByText('Gamma Agent')).not.toBeInTheDocument();

    // Next page button with aria-label
    const nextBtn = screen.getByRole('button', { name: 'Next page' });
    fireEvent.click(nextBtn);

    // Page 2: Gamma & Delta
    expect(screen.getByText('Gamma Agent')).toBeInTheDocument();
    expect(screen.getByText('Delta Agent')).toBeInTheDocument();
    expect(screen.queryByText('Alpha Agent')).not.toBeInTheDocument();
  });
});
