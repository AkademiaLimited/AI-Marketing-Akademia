import React from 'react';
import { render, screen } from '@testing-library/react';
import HomePage from '@/app/(marketing)/page';

jest.mock('@/lib/api', () => ({
  apiFetch: jest.fn(),
}));

const { apiFetch } = require('@/lib/api') as { apiFetch: jest.Mock };

describe('HomePage', () => {
  it('renders hero heading', async () => {
    apiFetch.mockResolvedValue([]);
    render(await HomePage());
    expect(screen.getByText(/Six practical AI products/i)).toBeInTheDocument();
  });

  it('renders product dock with all six products', async () => {
    apiFetch.mockResolvedValue([]);
    render(await HomePage());
    expect(screen.getByText('AI AVATAR AKADEMIA')).toBeInTheDocument();
    expect(screen.getByText('AIPOD')).toBeInTheDocument();
    expect(screen.getByText('VIRTUAL WORLD')).toBeInTheDocument();
    expect(screen.getByText('UgaJapa Translation')).toBeInTheDocument();
    expect(screen.getByText('AI DOJO')).toBeInTheDocument();
    expect(screen.getByText('AI RECRUITER')).toBeInTheDocument();
  });

  it('renders product cards when products are published', async () => {
    apiFetch.mockResolvedValue([
      {
        id: '1',
        slug: 'pod',
        name: 'AIPOD',
        published: true,
        problem: 'Scaling outreach',
        target: 'Growth teams',
        description: 'AIPOD helps teams manage tasks and reporting in one place.',
        features: ['A'],
        benefits: ['B'],
      },
    ]);
    render(await HomePage());
    const podElements = screen.getAllByText('AIPOD');
    expect(podElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('AIPOD helps teams manage tasks and reporting in one place.')).toBeInTheDocument();
  });

  it('shows empty state when no published products', async () => {
    apiFetch.mockResolvedValue([]);
    render(await HomePage());
    expect(screen.getByText(/No products published yet/i)).toBeInTheDocument();
  });
});
