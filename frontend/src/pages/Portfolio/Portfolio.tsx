import React from 'react'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
} from '@mui/icons-material'

const Portfolio: React.FC = () => {
  const holdings = [
    { symbol: 'AAPL', name: 'Apple Inc.', shares: 50, currentPrice: '$175.23', totalValue: '$8,761.50', gain: '+12.3%', gainType: 'positive' },
    { symbol: 'MSFT', name: 'Microsoft Corporation', shares: 30, currentPrice: '$412.34', totalValue: '$12,370.20', gain: '+8.7%', gainType: 'positive' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', shares: 15, currentPrice: '$138.45', totalValue: '$2,076.75', gain: '-2.1%', gainType: 'negative' },
    { symbol: 'TSLA', name: 'Tesla Inc.', shares: 25, currentPrice: '$248.92', totalValue: '$6,223.00', gain: '+15.8%', gainType: 'positive' },
  ]

  const totalValue = holdings.reduce((sum, holding) => sum + parseFloat(holding.totalValue.replace('$', '').replace(',', '')), 0)

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Portfolio Overview
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Track your investments and portfolio performance.
      </Typography>

      {/* Portfolio Summary */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AttachMoney color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Value</Typography>
              </Box>
              <Typography variant="h4" gutterBottom>
                ${totalValue.toLocaleString()}
              </Typography>
              <Chip
                label="+12.3%"
                size="small"
                sx={{ bgcolor: '#4caf50', color: 'white' }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Gain</Typography>
              </Box>
              <Typography variant="h4" gutterBottom color="success.main">
                +$3,456
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Since inception
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingDown color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Day Change</Typography>
              </Box>
              <Typography variant="h4" gutterBottom color="success.main">
                +$234
              </Typography>
              <Typography variant="body2" color="text.secondary">
                +1.2% today
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Holdings */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Your Holdings
          </Typography>
          {holdings.map((holding, index) => (
            <Box
              key={index}
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              py={2}
              borderBottom={index < holdings.length - 1 ? 1 : 0}
              borderColor="divider"
            >
              <Box flex={1}>
                <Typography variant="subtitle1" fontWeight="bold">
                  {holding.symbol}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {holding.name}
                </Typography>
              </Box>
              <Box flex={1} textAlign="center">
                <Typography variant="body2">
                  {holding.shares} shares @ {holding.currentPrice}
                </Typography>
              </Box>
              <Box flex={1} textAlign="center">
                <Typography variant="subtitle1" fontWeight="bold">
                  {holding.totalValue}
                </Typography>
              </Box>
              <Box flex={1} textAlign="right">
                <Chip
                  label={holding.gain}
                  size="small"
                  sx={{
                    bgcolor: holding.gainType === 'positive' ? '#4caf50' : '#f44336',
                    color: 'white',
                  }}
                />
              </Box>
            </Box>
          ))}
        </CardContent>
      </Card>

      {/* Allocation */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Asset Allocation
          </Typography>
          <Box mt={2}>
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2">Technology</Typography>
              <Typography variant="body2">65%</Typography>
            </Box>
            <LinearProgress variant="determinate" value={65} sx={{ mb: 2 }} />
            
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2">Automotive</Typography>
              <Typography variant="body2">20%</Typography>
            </Box>
            <LinearProgress variant="determinate" value={20} sx={{ mb: 2 }} />
            
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2">Other</Typography>
              <Typography variant="body2">15%</Typography>
            </Box>
            <LinearProgress variant="determinate" value={15} />
          </Box>
        </CardContent>
      </Card>
    </Container>
  )
}

export default Portfolio