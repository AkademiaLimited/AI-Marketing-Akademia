import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import AutomationPage from '@/app/admin/automation/page';

jest.mock('@/lib/api', () => ({
  apiFetchWithAuth: jest.fn(),
  apiFetch: jest.fn(),
}));

jest.mock('@/app/admin/_components/auth-context', () => ({
  useAuth: () => ({
    token: 'mock-token',
    user: { id: '1', email: 'admin@akademia.local', name: 'Admin' },
    loading: false,
  }),
}));

const { apiFetchWithAuth } = require('@/lib/api') as { apiFetchWithAuth: jest.Mock };

describe('AdminAutomation', () => {
  beforeEach(() => {
    (apiFetchWithAuth as jest.Mock).mockClear();
  });

  it('renders automation table with data', async () => {
    (apiFetchWithAuth as jest.Mock).mockImplementation((path: string) => {
      if (path === '/workflows/activities') return Promise.resolve([]);
      return Promise.resolve([
        {
          id: 'A1',
          name: 'Lead Discovery',
          status: 'running',
          last_run: '12 min ago',
          result: 'Found 6 new leads',
        },
      ]);
    });

    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText('Lead Discovery')).toBeInTheDocument();
    });
    expect(screen.getByText('running')).toBeInTheDocument();
    expect(screen.getByText('Found 6 new leads')).toBeInTheDocument();
    expect(apiFetchWithAuth).toHaveBeenCalledWith('/workflows/activities', 'mock-token');
  });

  it('shows empty state when no automations', async () => {
    (apiFetchWithAuth as jest.Mock).mockResolvedValue([]);

    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText(/No automations found/i)).toBeInTheDocument();
    });
  });
});
