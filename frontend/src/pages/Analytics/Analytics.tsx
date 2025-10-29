import React, { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  Tabs,
  Tab,
} from '@mui/material'
import {
  TrendingUp,
  ShowChart,
  Assessment,
  PieChart,
  Psychology,
  Compare,
  BarChart,
} from '@mui/icons-material'
import AIAnalysis from '../Analysis/AIAnalysis'
import TechnicalAnalysis from '../Analysis/TechnicalAnalysis'
import StockComparison from '../Analysis/StockComparison'

const Analytics: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const metrics = [
    {
      title: 'Portfolio Beta',
      value: '1.23',
      description: 'Market volatility comparison',
      icon: <Assessment color="primary" />,
    },
    {
      title: 'Sharpe Ratio',
      value: '1.45',
      description: 'Risk-adjusted returns',
      icon: <ShowChart color="primary" />,
    },
    {
      title: 'Max Drawdown',
      value: '-8.2%',
      description: 'Largest peak-to-trough decline',
      icon: <TrendingUp color="primary" />,
    },
    {
      title: 'Diversification Ratio',
      value: '0.78',
      description: 'Portfolio diversification measure',
      icon: <PieChart color="primary" />,
    },
  ]

  const renderTabContent = () => {
    switch (tabValue) {
      case 0:
        return <AIAnalysis />
      case 1:
        return <TechnicalAnalysis />
      case 2:
        return <StockComparison />
      case 3:
        return renderTraditionalAnalytics()
      default:
        return <AIAnalysis />
    }
  }

  const renderTraditionalAnalytics = () => (
    <>
      {/* Metrics Cards */}
      <Grid container spacing={3} mb={4}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  {metric.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {metric.title}
                  </Typography>
                </Box>
                <Typography variant="h4" gutterBottom>
                  {metric.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {metric.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts Placeholder */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Box textAlign="center">
              <ShowChart sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Performance Chart
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Interactive charts will be implemented here
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Box textAlign="center">
              <PieChart sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Asset Allocation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pie chart will be implemented here
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Risk Analysis */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Risk Analysis
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Risk Level: Moderate
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Your portfolio has moderate risk compared to market benchmarks.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Volatility: 18.5%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Expected price fluctuation range based on historical data.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Correlation: 0.67
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Portfolio correlation with S&P 500 index.
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </>
  )

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Advanced Analytics & AI Insights
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Comprehensive analysis powered by AI, technical indicators, and advanced portfolio metrics.
      </Typography>

      {/* Navigation Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<Psychology />} 
            label="AI Analysis" 
            sx={{ textTransform: 'none' }}
          />
          <Tab 
            icon={<BarChart />} 
            label="Technical Analysis" 
            sx={{ textTransform: 'none' }}
          />
          <Tab 
            icon={<Compare />} 
            label="Stock Comparison" 
            sx={{ textTransform: 'none' }}
          />
          <Tab 
            icon={<Assessment />} 
            label="Portfolio Metrics" 
            sx={{ textTransform: 'none' }}
          />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box>{renderTabContent()}</Box>

    </Container>
  )
}

export default Analytics