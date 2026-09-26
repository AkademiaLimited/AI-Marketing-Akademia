import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from '@/app/admin/dashboard/page';

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

const DEFAULT_SUMMARY = {
  new: 10,
  contacted: 5,
  responded: 3,
  needs_followup: 2,
  meetings: 1,
  customers: 0,
  lost: 1,
};

const DEFAULT_PROGRESS = {
  marketing_pipeline: { pending: 0, queued: 0, running: 2, completed: 1, failed: 0 },
  lead_funnel: {},
  email_pipeline: {},
  campaign_status: {},
  workflow_runs: {},
  active_brand: null,
  recent_activity: [],
};

describe('AdminDashboard', () => {
  beforeEach(() => {
    (apiFetchWithAuth as jest.Mock).mockClear();
  });

  it('renders dashboard heading', async () => {
    (apiFetchWithAuth as jest.Mock)
      .mockResolvedValueOnce(DEFAULT_SUMMARY)
      .mockResolvedValueOnce(DEFAULT_PROGRESS)
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([]);

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
    expect(screen.getAllByText('New').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Customers').length).toBeGreaterThanOrEqual(1);
  });

  it('renders pipeline stages from summary', async () => {
    (apiFetchWithAuth as jest.Mock)
      .mockResolvedValueOnce(DEFAULT_SUMMARY)
      .mockResolvedValueOnce(DEFAULT_PROGRESS)
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([]);

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getAllByText('New').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText('Contacted').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Meetings').length).toBeGreaterThanOrEqual(1);
  });

  it('shows needs attention when leads exist', async () => {
    (apiFetchWithAuth as jest.Mock)
      .mockResolvedValueOnce(DEFAULT_SUMMARY)
      .mockResolvedValueOnce(DEFAULT_PROGRESS)
      .mockResolvedValueOnce([
        {
          id: '1',
          company: 'Acme Corp',
          status: 'new',
          last_contact: '',
        },
        {
          id: '2',
          company: 'Beta Ltd',
          status: 'needs-followup',
          last_contact: '2 days ago',
        },
      ])
      .mockResolvedValueOnce([]);

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('Acme Corp')).toBeInTheDocument();
    });
    expect(screen.getByText('Beta Ltd')).toBeInTheDocument();
  });

  it('renders marketing pipeline bars from progress data', async () => {
    (apiFetchWithAuth as jest.Mock)
      .mockResolvedValueOnce(DEFAULT_SUMMARY)
      .mockResolvedValueOnce(DEFAULT_PROGRESS)
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([]);

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('Marketing Pipeline')).toBeInTheDocument();
    });
    expect(screen.getByText('Lead Funnel')).toBeInTheDocument();
    expect(screen.getByText('Email Pipeline')).toBeInTheDocument();
    expect(screen.getByText('Campaign Status')).toBeInTheDocument();
  });

  it('shows active brand when set', async () => {
    (apiFetchWithAuth as jest.Mock)
      .mockResolvedValueOnce(DEFAULT_SUMMARY)
      .mockResolvedValueOnce({ ...DEFAULT_PROGRESS, active_brand: 'Akademia Default' })
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([]);

    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('Active brand:')).toBeInTheDocument();
    });
    expect(screen.getByText('Akademia Default')).toBeInTheDocument();
  });
});
