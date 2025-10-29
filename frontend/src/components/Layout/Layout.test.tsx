import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import '@testing-library/jest-dom'
import Layout from './Layout'

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

describe('Layout Navigation Tests', () => {
  const renderLayoutWithRoutes = () => {
    return render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<div data-testid="dashboard-page">Dashboard</div>} />
            <Route path="/research" element={<div data-testid="research-page">Research</div>} />
            <Route path="/portfolio" element={<div data-testid="portfolio-page">Portfolio</div>} />
            <Route path="/companies" element={<div data-testid="companies-page">Companies</div>} />
            <Route path="/analytics" element={<div data-testid="analytics-page">Analytics</div>} />
            <Route path="/analysis/ai" element={<div data-testid="ai-analysis-page">AI Analysis</div>} />
            <Route path="/analysis/technical" element={<div data-testid="technical-analysis-page">Technical Analysis</div>} />
            <Route path="/profile" element={<div data-testid="profile-page">Profile</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    )
  }

  describe('Layout Component Rendering', () => {
    it('should render layout with navigation drawer', () => {
      renderLayoutWithRoutes()
      expect(screen.getByText('AI Research')).toBeInTheDocument()
    })

    it('should display all main navigation items', () => {
      renderLayoutWithRoutes()
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Research')).toBeInTheDocument()
      expect(screen.getByText('Portfolio')).toBeInTheDocument()
      expect(screen.getByText('Companies')).toBeInTheDocument()
      expect(screen.getByText('Analytics')).toBeInTheDocument()
    })

    it('should display analysis navigation items', () => {
      renderLayoutWithRoutes()
      expect(screen.getByText('AI Analysis')).toBeInTheDocument()
      expect(screen.getByText('Technical Analysis')).toBeInTheDocument()
    })
  })

  describe('Navigation Menu Links', () => {
    it('should navigate to AI Analysis page from menu', async () => {
      renderLayoutWithRoutes()
      
      const aiAnalysisBtn = screen.getByRole('button', { name: /AI Analysis/i })
      fireEvent.click(aiAnalysisBtn)

      await waitFor(() => {
        expect(screen.getByTestId('ai-analysis-page')).toBeInTheDocument()
      })
    })

    it('should navigate to Technical Analysis page from menu', async () => {
      renderLayoutWithRoutes()
      
      const technicalAnalysisBtn = screen.getByRole('button', { name: /Technical Analysis/i })
      fireEvent.click(technicalAnalysisBtn)

      await waitFor(() => {
        expect(screen.getByTestId('technical-analysis-page')).toBeInTheDocument()
      })
    })

    it('should highlight active navigation item', () => {
      renderLayoutWithRoutes()
      
      const dashboardBtn = screen.getAllByRole('button', { name: /Dashboard/i })[0]
      expect(dashboardBtn).toHaveStyle({ backgroundColor: expect.anything() })
    })

    it('should navigate to Dashboard from menu', async () => {
      renderLayoutWithRoutes()
      
      const dashboardBtn = screen.getAllByRole('button', { name: /Dashboard/i })[0]
      fireEvent.click(dashboardBtn)

      await waitFor(() => {
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument()
      })
    })

    it('should navigate to Research from menu', async () => {
      renderLayoutWithRoutes()
      
      const researchBtn = screen.getByRole('button', { name: /Research/i })
      fireEvent.click(researchBtn)

      await waitFor(() => {
        expect(screen.getByTestId('research-page')).toBeInTheDocument()
      })
    })

    it('should navigate to Portfolio from menu', async () => {
      renderLayoutWithRoutes()
      
      const portfolioBtn = screen.getByRole('button', { name: /Portfolio/i })
      fireEvent.click(portfolioBtn)

      await waitFor(() => {
        expect(screen.getByTestId('portfolio-page')).toBeInTheDocument()
      })
    })

    it('should navigate to Companies from menu', async () => {
      renderLayoutWithRoutes()
      
      const companiesBtn = screen.getByRole('button', { name: /Companies/i })
      fireEvent.click(companiesBtn)

      await waitFor(() => {
        expect(screen.getByTestId('companies-page')).toBeInTheDocument()
      })
    })

    it('should navigate to Analytics from menu', async () => {
      renderLayoutWithRoutes()
      
      const analyticsBtn = screen.getByRole('button', { name: /Analytics/i })
      fireEvent.click(analyticsBtn)

      await waitFor(() => {
        expect(screen.getByTestId('analytics-page')).toBeInTheDocument()
      })
    })
  })

  describe('User Menu Navigation', () => {
    it('should display user avatar with initials', () => {
      renderLayoutWithRoutes()
      expect(screen.getByText('TU')).toBeInTheDocument()
    })

    it('should navigate to Profile from user menu', async () => {
      renderLayoutWithRoutes()
      
      const profileMenuBtn = screen.getByRole('button', { name: /Profile/i })
      fireEvent.click(profileMenuBtn)

      await waitFor(() => {
        expect(screen.getByTestId('profile-page')).toBeInTheDocument()
      })
    })
  })

  describe('Analysis Pages Accessibility', () => {
    it('AI Analysis should be accessible from sidebar navigation', () => {
      renderLayoutWithRoutes()
      
      const navItems = screen.getAllByRole('button', { name: /AI Analysis/i })
      expect(navItems.length).toBeGreaterThan(0)
      expect(navItems[0]).toBeInTheDocument()
    })

    it('Technical Analysis should be accessible from sidebar navigation', () => {
      renderLayoutWithRoutes()
      
      const navItems = screen.getAllByRole('button', { name: /Technical Analysis/i })
      expect(navItems.length).toBeGreaterThan(0)
      expect(navItems[0]).toBeInTheDocument()
    })
  })
})
