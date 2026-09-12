import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProductsPage from '@/app/admin/products/page';

jest.mock('@/lib/api', () => ({
  apiFetchWithAuth: jest.fn(),
  apiFetch: jest.fn(),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => ({ refresh: jest.fn() }),
}));

jest.mock('@/app/admin/_components/auth-context', () => ({
  useAuth: () => ({
    token: 'mock-token',
    user: { id: '1', email: 'admin@akademia.local', name: 'Admin' },
    loading: false,
  }),
}));

const { apiFetchWithAuth } = require('@/lib/api') as { apiFetchWithAuth: jest.Mock };

describe('AdminProducts', () => {
  beforeEach(() => {
    (apiFetchWithAuth as jest.Mock).mockClear();
    global.fetch = jest.fn();
  });

  it('renders products table with data', async () => {
    (apiFetchWithAuth as jest.Mock).mockResolvedValue([
      {
        id: 'prod-1',
        name: 'AI Pod',
        slug: 'pod',
        published: true,
        problem: 'Work scattered',
        target: 'Teams',
        description: 'Task management and reporting system',
        features: [],
        benefits: [],
        capabilities: [],
        category: 'business',
        price: '$299/mo',
        image_url: '',
        marketing_status: 'completed',
        marketing_result: '',
      },
    ]);

    render(<ProductsPage />);
    await waitFor(() => {
      expect(screen.getByText('AI Pod')).toBeInTheDocument();
    });
    expect(screen.getByText('Marketing complete')).toBeInTheDocument();
  });

  it('shows pending status and publish button for unpublished products', async () => {
    (apiFetchWithAuth as jest.Mock).mockResolvedValue([
      {
        id: 'prod-2',
        name: 'AI World',
        slug: 'world',
        published: true,
        problem: 'Virtual experiences',
        target: 'Travellers',
        description: 'A virtual world built around Japan.',
        features: [],
        benefits: [],
        capabilities: [],
        category: 'general',
        price: '$99/mo',
        image_url: '',
        marketing_status: 'pending',
        marketing_result: '',
      },
    ]);

    render(<ProductsPage />);
    await waitFor(() => {
      expect(screen.getByText('pending')).toBeInTheDocument();
    });
    expect(screen.getByText('Publish to Marketing')).toBeInTheDocument();
  });

  it('shows running status for queued products', async () => {
    (apiFetchWithAuth as jest.Mock).mockResolvedValue([
      {
        id: 'prod-3',
        name: 'AI Dojo',
        slug: 'dojo',
        published: true,
        problem: 'Impersonal AI',
        target: 'Everyone',
        description: 'Interactive AI avatars.',
        features: [],
        benefits: [],
        capabilities: [],
        category: 'general',
        price: '$199/mo',
        image_url: '',
        marketing_status: 'queued',
        marketing_result: '',
      },
    ]);

    render(<ProductsPage />);
    await waitFor(() => {
      expect(screen.getByText('Running...')).toBeInTheDocument();
    });
  });

  it('shows empty state when no products', async () => {
    (apiFetchWithAuth as jest.Mock).mockResolvedValue([]);

    render(<ProductsPage />);
    await waitFor(() => {
      expect(screen.getByText(/No products found/i)).toBeInTheDocument();
    });
  });

  it('triggers publish when Publish button is clicked', async () => {
    (apiFetchWithAuth as jest.Mock).mockResolvedValueOnce([
      {
        id: 'prod-4',
        name: 'AI Recruiter',
        slug: 'recruiter',
        published: true,
        problem: 'Manual screening',
        target: 'HR teams',
        description: 'AI recruiting platform.',
        features: [],
        benefits: [],
        capabilities: [],
        category: 'business',
        price: '$249/mo',
        image_url: '',
        marketing_status: 'pending',
        marketing_result: '',
      },
    ]);

    (apiFetchWithAuth as jest.Mock).mockResolvedValue({});

    render(<ProductsPage />);

    const publishButton = await screen.findByText('Publish to Marketing');
    fireEvent.click(publishButton);

    await waitFor(() => {
      expect(apiFetchWithAuth).toHaveBeenCalledWith(
        '/products/recruiter/publish',
        'mock-token',
        expect.objectContaining({ method: 'POST' })
      );
    });
  });
});
