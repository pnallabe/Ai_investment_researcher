import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter, MemoryRouter, Routes, Route } from 'react-router-dom'
import '@testing-library/jest-dom'
import Dashboard from './Dashboard'
import AIAnalysis from '../Analysis/AIAnalysis'
import TechnicalAnalysis from '../Analysis/TechnicalAnalysis'

// Mock the useAuth hook
jest.mock('@hooks/useAuth', () => ({
  useAuth: () => ({
    user: {
      id: 'test-user-001',
      email: 'test@example.com',
      username: 'testuser',
      first_name: 'Test',
      last_name: 'User',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    isAuthenticated: true,
    loading: false,
    token: 'test-token',
    login: jest.fn(),
    logout: jest.fn(),
  }),
}))

// Mock the AuthDebug component
jest.mock('@components/AuthDebug', () => {
  return function MockAuthDebug() {
    return <div data-testid="auth-debug">Auth Debug</div>
  }
})

describe('Dashboard Navigation Tests', () => {
  describe('Dashboard Component Rendering', () => {
    it('should render the dashboard with all sections', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      expect(screen.getByText(/Welcome back/i)).toBeInTheDocument()
      expect(screen.getByText(/Portfolio Value/i)).toBeInTheDocument()
      expect(screen.getByText(/Quick Actions/i)).toBeInTheDocument()
    })

    it('should display quick action buttons', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      const aiAnalysisBtn = screen.getByRole('button', { name: /AI Analysis/i })
      const technicalAnalysisBtn = screen.getByRole('button', { name: /Technical Analysis/i })
      const portfolioBtn = screen.getByRole('button', { name: /Portfolio/i })

      expect(aiAnalysisBtn).toBeInTheDocument()
      expect(technicalAnalysisBtn).toBeInTheDocument()
      expect(portfolioBtn).toBeInTheDocument()
    })
  })

  describe('Dashboard Button Navigation', () => {
    it('should navigate to AI Analysis page when AI Analysis button is clicked', async () => {
      const { container } = render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analysis/ai" element={<div data-testid="ai-analysis-page">AI Analysis Page</div>} />
          </Routes>
        </MemoryRouter>
      )

      const aiAnalysisBtn = screen.getByRole('button', { name: /AI Analysis/i })
      fireEvent.click(aiAnalysisBtn)

      await waitFor(() => {
        expect(screen.getByTestId('ai-analysis-page')).toBeInTheDocument()
      })
    })

    it('should navigate to Technical Analysis page when Technical Analysis button is clicked', async () => {
      const { container } = render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analysis/technical" element={<div data-testid="technical-analysis-page">Technical Analysis Page</div>} />
          </Routes>
        </MemoryRouter>
      )

      const technicalAnalysisBtn = screen.getByRole('button', { name: /Technical Analysis/i })
      fireEvent.click(technicalAnalysisBtn)

      await waitFor(() => {
        expect(screen.getByTestId('technical-analysis-page')).toBeInTheDocument()
      })
    })

    it('should navigate to Portfolio page when Portfolio button is clicked', async () => {
      const { container } = render(
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/portfolio" element={<div data-testid="portfolio-page">Portfolio Page</div>} />
          </Routes>
        </MemoryRouter>
      )

      const portfolioBtn = screen.getByRole('button', { name: /Portfolio/i })
      fireEvent.click(portfolioBtn)

      await waitFor(() => {
        expect(screen.getByTestId('portfolio-page')).toBeInTheDocument()
      })
    })
  })

  describe('Button Click Behavior', () => {
    it('AI Analysis button should be clickable', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      const aiAnalysisBtn = screen.getByRole('button', { name: /AI Analysis/i })
      expect(aiAnalysisBtn).not.toBeDisabled()
      
      fireEvent.click(aiAnalysisBtn)
      // Event should fire without errors
      expect(aiAnalysisBtn).toBeInTheDocument()
    })

    it('Technical Analysis button should be clickable', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      const technicalAnalysisBtn = screen.getByRole('button', { name: /Technical Analysis/i })
      expect(technicalAnalysisBtn).not.toBeDisabled()
      
      fireEvent.click(technicalAnalysisBtn)
      // Event should fire without errors
      expect(technicalAnalysisBtn).toBeInTheDocument()
    })

    it('Portfolio button should be clickable', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      const portfolioBtn = screen.getByRole('button', { name: /Portfolio/i })
      expect(portfolioBtn).not.toBeDisabled()
      
      fireEvent.click(portfolioBtn)
      // Event should fire without errors
      expect(portfolioBtn).toBeInTheDocument()
    })
  })

  describe('Dashboard Stats and Layout', () => {
    it('should display stat cards with correct information', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      expect(screen.getByText(/Portfolio Value/i)).toBeInTheDocument()
      expect(screen.getByText(/Total Gain\/Loss/i)).toBeInTheDocument()
      expect(screen.getByText(/Active Positions/i)).toBeInTheDocument()
      expect(screen.getByText(/Research Reports/i)).toBeInTheDocument()
    })

    it('should display recent activity section', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      expect(screen.getByText(/Recent Activity/i)).toBeInTheDocument()
      expect(screen.getByText(/AAPL/)).toBeInTheDocument()
      expect(screen.getByText(/TSLA/)).toBeInTheDocument()
      expect(screen.getByText(/MSFT/)).toBeInTheDocument()
    })

    it('should display top performers section', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      expect(screen.getByText(/Top Performers Today/i)).toBeInTheDocument()
    })

    it('should display portfolio performance chart', () => {
      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      )

      expect(screen.getByText(/Portfolio Performance/i)).toBeInTheDocument()
      expect(screen.getByText(/Last 30 Days/i)).toBeInTheDocument()
    })
  })
})
