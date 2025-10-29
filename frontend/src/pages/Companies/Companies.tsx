import React from 'react'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
} from '@mui/material'
import {
  Business,
  TrendingUp,
  TrendingDown,
  Star,
  StarBorder,
} from '@mui/icons-material'

const Companies: React.FC = () => {
  const companies = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      sector: 'Technology',
      price: '$175.23',
      change: '+2.3%',
      changeType: 'positive',
      marketCap: '$2.8T',
      rating: 'Buy',
      starred: true,
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      sector: 'Technology',
      price: '$412.34',
      change: '+1.8%',
      changeType: 'positive',
      marketCap: '$3.1T',
      rating: 'Buy',
      starred: false,
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      sector: 'Technology',
      price: '$138.45',
      change: '-0.5%',
      changeType: 'negative',
      marketCap: '$1.7T',
      rating: 'Hold',
      starred: true,
    },
    {
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      sector: 'Automotive',
      price: '$248.92',
      change: '+4.2%',
      changeType: 'positive',
      marketCap: '$792B',
      rating: 'Buy',
      starred: false,
    },
    {
      symbol: 'AMZN',
      name: 'Amazon.com Inc.',
      sector: 'Consumer Discretionary',
      price: '$154.67',
      change: '+1.2%',
      changeType: 'positive',
      marketCap: '$1.6T',
      rating: 'Buy',
      starred: false,
    },
    {
      symbol: 'NVDA',
      name: 'NVIDIA Corporation',
      sector: 'Technology',
      price: '$875.30',
      change: '+6.7%',
      changeType: 'positive',
      marketCap: '$2.2T',
      rating: 'Strong Buy',
      starred: true,
    },
  ]

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'Strong Buy': return '#1b5e20'
      case 'Buy': return '#4caf50'
      case 'Hold': return '#ff9800'
      case 'Sell': return '#f44336'
      default: return '#757575'
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Company Analysis
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Research and analyze companies in your watchlist and beyond.
      </Typography>

      {/* Companies Grid */}
      <Grid container spacing={3}>
        {companies.map((company, index) => (
          <Grid item xs={12} md={6} lg={4} key={index}>
            <Card sx={{ height: '100%', position: 'relative' }}>
              <CardContent>
                {/* Header */}
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Box display="flex" alignItems="center">
                    <Business color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">{company.symbol}</Typography>
                  </Box>
                  <Box>
                    {company.starred ? (
                      <Star sx={{ color: '#ffc107' }} />
                    ) : (
                      <StarBorder sx={{ color: '#757575' }} />
                    )}
                  </Box>
                </Box>

                {/* Company Info */}
                <Typography variant="body1" gutterBottom>
                  {company.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {company.sector}
                </Typography>

                {/* Price and Change */}
                <Box display="flex" alignItems="center" justifyContent="space-between" my={2}>
                  <Typography variant="h5" fontWeight="bold">
                    {company.price}
                  </Typography>
                  <Box display="flex" alignItems="center">
                    {company.changeType === 'positive' ? (
                      <TrendingUp sx={{ color: '#4caf50', mr: 0.5 }} />
                    ) : (
                      <TrendingDown sx={{ color: '#f44336', mr: 0.5 }} />
                    )}
                    <Typography
                      variant="body2"
                      sx={{
                        color: company.changeType === 'positive' ? '#4caf50' : '#f44336',
                        fontWeight: 'bold',
                      }}
                    >
                      {company.change}
                    </Typography>
                  </Box>
                </Box>

                {/* Market Cap */}
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Market Cap: {company.marketCap}
                </Typography>

                {/* Rating */}
                <Box display="flex" alignItems="center" justifyContent="space-between" mt={2}>
                  <Chip
                    label={company.rating}
                    size="small"
                    sx={{
                      bgcolor: getRatingColor(company.rating),
                      color: 'white',
                      fontWeight: 'bold',
                    }}
                  />
                  <Button size="small" variant="outlined">
                    Analyze
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Add More Companies */}
      <Card sx={{ mt: 4, textAlign: 'center' }}>
        <CardContent sx={{ py: 4 }}>
          <Typography variant="h6" gutterBottom>
            Want to analyze more companies?
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Use our AI research assistant to discover and analyze any public company.
          </Typography>
          <Button variant="contained" size="large">
            Start Research
          </Button>
        </CardContent>
      </Card>
    </Container>
  )
}

export default Companies