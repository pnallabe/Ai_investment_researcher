import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { CssBaseline, Box } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { SnackbarProvider } from 'notistack'

// Pages and components
import SimpleLayout from '@components/SimpleLayout'
import Login from '@pages/Login/Login'
import LiveDashboard from '@pages/Dashboard/LiveDashboard'
import Research from '@pages/Research/Research'
import Portfolio from '@pages/Portfolio/Portfolio'
import Companies from '@pages/Companies/Companies'
import Analytics from '@pages/Analytics/Analytics'
import Profile from '@pages/Profile/Profile'
import SimpleTest from '@pages/SimpleTest'
import DebugLogin from '@components/DebugLogin'
import AIAnalysis from '@pages/Analysis/AIAnalysis'
import TechnicalAnalysis from '@pages/Analysis/TechnicalAnalysis'
import StockComparison from '@pages/Analysis/StockComparison'

// Hooks and utilities
import { AuthProvider, useAuth } from '@hooks/useAuth'
import './App.css'

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Create MUI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
})

// Protected Route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading, user, token } = useAuth()

  console.log('ProtectedRoute state:', { isAuthenticated, loading, hasUser: !!user, hasToken: !!token })

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Loading...</Box>
  }

  if (!isAuthenticated) {
    console.log('Not authenticated, redirecting to login')
    return <Navigate to="/login" replace />
  }

  console.log('Authenticated, rendering children')
  return <>{children}</>
}

// Main App Routes component
const AppRoutes: React.FC = () => {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} 
      />
      <Route path="/test" element={<SimpleTest />} />
      <Route path="/debug" element={<DebugLogin />} />
      <Route path="/test-ai" element={<AIAnalysis />} />
      <Route path="/test-technical" element={<TechnicalAnalysis />} />
      <Route path="/test-comparison" element={<StockComparison />} />
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <SimpleLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<LiveDashboard />} />
        <Route path="research" element={<Research />} />
        <Route path="portfolio" element={<Portfolio />} />
        <Route path="companies" element={<Companies />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="analysis/ai" element={<AIAnalysis />} />
        <Route path="analysis/technical" element={<TechnicalAnalysis />} />
        <Route path="analysis/comparison" element={<StockComparison />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

// Main App component
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider 
          maxSnack={3}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <AuthProvider>
            <Router>
              <AppRoutes />
            </Router>
          </AuthProvider>
        </SnackbarProvider>
        <ReactQueryDevtools initialIsOpen={false} />
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App