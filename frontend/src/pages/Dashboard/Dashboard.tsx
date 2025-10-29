import React from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  LinearProgress,
} from '@mui/material'
import {
  TrendingUp,
  AttachMoney,
  ShowChart,
  Business,
  Analytics,
} from '@mui/icons-material'
import { useAuth } from '@hooks/useAuth'
import AuthDebug from '@components/AuthDebug'

interface StatCard {
  title: string
  value: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  icon: React.ReactElement
  color: string
}

const Dashboard: React.FC = () => {
  const { user } = useAuth()

  const stats: StatCard[] = [
    {
      title: 'Portfolio Value',
      value: '$124,567',
      change: '+12.3%',
      changeType: 'positive',
      icon: <AttachMoney sx={{ fontSize: 30 }} />,
      color: '#4caf50',
    },
    {
      title: 'Total Gain/Loss',
      value: '$15,234',
      change: '+8.7%',
      changeType: 'positive',
      icon: <TrendingUp sx={{ fontSize: 30 }} />,
      color: '#2196f3',
    },
    {
      title: 'Active Positions',
      value: '23',
      change: '+2',
      changeType: 'positive',
      icon: <ShowChart sx={{ fontSize: 30 }} />,
      color: '#ff9800',
    },
    {
      title: 'Research Reports',
      value: '147',
      change: '+12',
      changeType: 'positive',
      icon: <Analytics sx={{ fontSize: 30 }} />,
      color: '#9c27b0',
    },
  ]

  const recentActivity = [
    {
      type: 'Buy',
      symbol: 'AAPL',
      company: 'Apple Inc.',
      shares: 50,
      price: '$175.23',
      time: '2 hours ago',
    },
    {
      type: 'Sell',
      symbol: 'TSLA',
      company: 'Tesla Inc.',
      shares: 25,
      price: '$248.92',
      time: '5 hours ago',
    },
    {
      type: 'Research',
      symbol: 'MSFT',
      company: 'Microsoft Corporation',
      shares: null,
      price: null,
      time: '1 day ago',
    },
  ]

  const topPerformers = [
    { symbol: 'AAPL', change: '+5.67%', value: '$175.23' },
    { symbol: 'MSFT', change: '+3.21%', value: '$412.34' },
    { symbol: 'GOOGL', change: '+2.89%', value: '$138.45' },
    { symbol: 'AMZN', change: '+1.45%', value: '$154.67' },
  ]

  const getChangeColor = (changeType: string) => {
    switch (changeType) {
      case 'positive': return '#4caf50'
      case 'negative': return '#f44336'
      default: return '#757575'
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Debug Component */}
      <AuthDebug />
      
      {/* Welcome Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome back, {user?.first_name || user?.username || 'Investor'}! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your investments today.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        {stats.map((stat, index) => (
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

      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Box>
                {recentActivity.map((activity, index) => (
                  <Box
                    key={index}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    py={2}
                    borderBottom={index < recentActivity.length - 1 ? 1 : 0}
                    borderColor="divider"
                  >
                    <Box display="flex" alignItems="center">
                      <Avatar
                        sx={{
                          bgcolor: activity.type === 'Buy' ? '#4caf50' : 
                                   activity.type === 'Sell' ? '#f44336' : '#2196f3',
                          mr: 2,
                          width: 40,
                          height: 40,
                        }}
                      >
                        {activity.type === 'Research' ? (
                          <Analytics sx={{ fontSize: 20 }} />
                        ) : (
                          <Business sx={{ fontSize: 20 }} />
                        )}
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle1">
                          {activity.type} {activity.symbol}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {activity.company}
                        </Typography>
                      </Box>
                    </Box>
                    <Box textAlign="right">
                      {activity.shares && (
                        <Typography variant="body2">
                          {activity.shares} shares @ {activity.price}
                        </Typography>
                      )}
                      <Typography variant="caption" color="text.secondary">
                        {activity.time}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
            <CardActions>
              <Button size="small">View All Activity</Button>
            </CardActions>
          </Card>
        </Grid>

        {/* Top Performers */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: 'fit-content' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Performers Today
              </Typography>
              <Box>
                {topPerformers.map((stock, index) => (
                  <Box
                    key={index}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    py={1.5}
                    borderBottom={index < topPerformers.length - 1 ? 1 : 0}
                    borderColor="divider"
                  >
                    <Box>
                      <Typography variant="subtitle2">
                        {stock.symbol}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {stock.value}
                      </Typography>
                    </Box>
                    <Chip
                      label={stock.change}
                      size="small"
                      sx={{
                        bgcolor: '#4caf50',
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
            <CardActions>
              <Button size="small">View All Stocks</Button>
            </CardActions>
          </Card>

          {/* Quick Actions */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Analytics />}
                    sx={{ py: 1.5 }}
                  >
                    Research
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<TrendingUp />}
                    sx={{ py: 1.5 }}
                  >
                    Portfolio
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<ShowChart />}
                    sx={{ py: 1.5, mt: 1 }}
                  >
                    Start AI Analysis
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Portfolio Performance */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Portfolio Performance (Last 30 Days)
          </Typography>
          <Box mt={2}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Overall Performance: +12.3%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={75}
              sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  bgcolor: '#4caf50',
                  borderRadius: 4,
                },
              }}
            />
            <Box display="flex" justifyContent="space-between" mt={1}>
              <Typography variant="caption" color="text.secondary">
                Start: $110,234
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Current: $124,567
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Container>
  )
}

export default Dashboard