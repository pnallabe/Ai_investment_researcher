import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Avatar,
  LinearProgress,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material'
import {
  TrendingUp,
  AttachMoney,
  Business,
  Analytics,
  Refresh,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material'
import LiveDataService, { Portfolio, MarketOverview } from '@services/liveDataService'

interface StatCard {
  title: string
  value: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  icon: React.ReactElement
  color: string
}

const LiveDashboard: React.FC = () => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [marketData, setMarketData] = useState<MarketOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<string>('')
  const [systemStatus, setSystemStatus] = useState<any>(null)

  // Fetch all data
  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch portfolio data
      const portfolios = await LiveDataService.getPortfolios()
      if (portfolios.length > 0) {
        setPortfolio(portfolios[0])
      }

      // Fetch market data
      const market = await LiveDataService.getMarketOverview()
      setMarketData(market)

      // Fetch system status
      const status = await LiveDataService.getSystemStatus()
      setSystemStatus(status)

      setLastUpdated(new Date().toLocaleTimeString())
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err)
      setError(err.message || 'Failed to fetch dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  // Create stat cards from portfolio data
  const getStatCards = (): StatCard[] => {
    if (!portfolio) return []

    return [
      {
        title: 'Portfolio Value',
        value: LiveDataService.formatCurrency(portfolio.total_value),
        change: LiveDataService.formatPercentage(portfolio.total_gain_loss_percent),
        changeType: portfolio.total_gain_loss_percent > 0 ? 'positive' : 
                   portfolio.total_gain_loss_percent < 0 ? 'negative' : 'neutral',
        icon: <AttachMoney sx={{ fontSize: 30 }} />,
        color: '#4caf50',
      },
      {
        title: 'Total Positions',
        value: portfolio.holdings_count.toString(),
        change: `${Object.keys(portfolio.sectors).length} sectors`,
        changeType: 'neutral',
        icon: <Business sx={{ fontSize: 30 }} />,
        color: '#2196f3',
      },
      {
        title: 'Best Performer',
        value: portfolio.top_performers[0]?.ticker || 'N/A',
        change: portfolio.top_performers[0] ? 
                LiveDataService.formatPercentage(portfolio.top_performers[0].change_percent) : '',
        changeType: 'positive',
        icon: <TrendingUp sx={{ fontSize: 30 }} />,
        color: '#ff9800',
      },
      {
        title: 'Data Source',
        value: portfolio.real_data ? 'Live' : 'Mock',
        change: `Updated ${new Date(portfolio.last_updated).toLocaleTimeString()}`,
        changeType: portfolio.real_data ? 'positive' : 'neutral',
        icon: <Analytics sx={{ fontSize: 30 }} />,
        color: '#9c27b0',
      },
    ]
  }

  const getChangeColor = (changeType: string) => {
    switch (changeType) {
      case 'positive': return '#4caf50'
      case 'negative': return '#f44336'
      default: return '#757575'
    }
  }

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <Box textAlign="center">
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6">Loading live financial data...</Typography>
            <Typography variant="body2" color="text.secondary">
              Fetching real-time market data and portfolio information
            </Typography>
          </Box>
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Alert 
          severity="error" 
          action={
            <IconButton onClick={fetchDashboardData} color="inherit">
              <Refresh />
            </IconButton>
          }
        >
          <Typography variant="h6">Error Loading Dashboard Data</Typography>
          <Typography variant="body2">{error}</Typography>
        </Alert>
      </Container>
    )
  }

  const statCards = getStatCards()

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header with System Status */}
      <Box mb={4} display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Live Investment Dashboard 📈
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time data from SEC EDGAR and Yahoo Finance
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={2}>
          {systemStatus && (
            <Chip
              icon={systemStatus.dependencies?.data_processor === 'available' ? 
                    <CheckCircle /> : <ErrorIcon />}
              label={systemStatus.dependencies?.data_processor === 'available' ? 
                    'Live Data' : 'Mock Data'}
              color={systemStatus.dependencies?.data_processor === 'available' ? 
                    'success' : 'warning'}
              variant="outlined"
            />
          )}
          <Tooltip title="Refresh Dashboard">
            <IconButton onClick={fetchDashboardData} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Typography variant="caption" color="text.secondary">
            Last updated: {lastUpdated}
          </Typography>
        </Box>
      </Box>

      {/* Portfolio Stats Cards */}
      {portfolio && (
        <Grid container spacing={3} mb={4}>
          {statCards.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                    <Avatar sx={{ bgcolor: stat.color, width: 56, height: 56 }}>
                      {stat.icon}
                    </Avatar>
                    <Chip
                      label={stat.change}
                      size="small"
                      sx={{
                        bgcolor: getChangeColor(stat.changeType),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </Box>
                  <Typography variant="h4" component="div" gutterBottom>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Grid container spacing={3}>
        {/* Portfolio Positions */}
        {portfolio && (
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Portfolio Positions
                </Typography>
                <TableContainer component={Paper} elevation={0}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Company</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell align="right">Price</TableCell>
                        <TableCell align="right">Value</TableCell>
                        <TableCell align="right">Change</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(portfolio.positions).map(([ticker, position]) => (
                        <TableRow key={ticker}>
                          <TableCell>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {ticker}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2">
                                {position.company_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {position.sector}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">{position.quantity}</TableCell>
                          <TableCell align="right">
                            ${position.current_price.toFixed(2)}
                          </TableCell>
                          <TableCell align="right">
                            {LiveDataService.formatCurrency(position.position_value)}
                          </TableCell>
                          <TableCell align="right">
                            <Chip
                              label={LiveDataService.formatPercentage(position.change_percent)}
                              size="small"
                              sx={{
                                bgcolor: LiveDataService.getChangeColor(position.change_percent),
                                color: 'white',
                                fontWeight: 'bold',
                              }}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Market Overview and Top Performers */}
        <Grid item xs={12} md={4}>
          {/* Market Indices */}
          {marketData && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Indices
                </Typography>
                {Object.entries(marketData.indices).slice(0, 4).map(([name, data]) => (
                  <Box
                    key={name}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    py={1}
                    borderBottom={1}
                    borderColor="divider"
                  >
                    <Typography variant="body2" fontWeight="medium">
                      {name}
                    </Typography>
                    <Box textAlign="right">
                      <Typography variant="body2">
                        ${data.price?.toFixed(2) || 'N/A'}
                      </Typography>
                      <Chip
                        label={LiveDataService.formatPercentage(data.change_percent || 0)}
                        size="small"
                        sx={{
                          bgcolor: LiveDataService.getChangeColor(data.change_percent || 0),
                          color: 'white',
                          fontSize: '0.7rem'
                        }}
                      />
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Top Performers */}
          {portfolio && portfolio.top_performers.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Performers
                </Typography>
                {portfolio.top_performers.slice(0, 3).map((performer, index) => (
                  <Box
                    key={performer.ticker}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    py={1.5}
                    borderBottom={index < 2 ? 1 : 0}
                    borderColor="divider"
                  >
                    <Box>
                      <Typography variant="subtitle2" fontWeight="bold">
                        {performer.ticker}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {LiveDataService.formatCurrency(performer.position_value)}
                      </Typography>
                    </Box>
                    <Chip
                      label={LiveDataService.formatPercentage(performer.change_percent)}
                      size="small"
                      sx={{
                        bgcolor: '#4caf50',
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Portfolio Performance Chart Placeholder */}
      {portfolio && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Portfolio Performance
            </Typography>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="body2" color="text.secondary">
                Overall Performance: {LiveDataService.formatPercentage(portfolio.total_gain_loss_percent)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Real-time data from Yahoo Finance & SEC EDGAR
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(Math.abs(portfolio.total_gain_loss_percent) * 10, 100)}
              sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  bgcolor: portfolio.total_gain_loss_percent > 0 ? '#4caf50' : '#f44336',
                  borderRadius: 4,
                },
              }}
            />
            <Box display="flex" justifyContent="space-between" mt={1}>
              <Typography variant="caption" color="text.secondary">
                Total Value: {LiveDataService.formatCurrency(portfolio.total_value)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {portfolio.holdings_count} positions across {Object.keys(portfolio.sectors).length} sectors
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Container>
  )
}

export default LiveDashboard