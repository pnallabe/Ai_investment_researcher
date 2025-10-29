import React from 'react'
import { Box, Typography, Paper, Button } from '@mui/material'

const SimpleTest: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          🎉 Simple Test Page
        </Typography>
        <Typography variant="body1" gutterBottom>
          If you can see this page, React Router and basic components are working!
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Current URL: {window.location.href}
        </Typography>
        <Button variant="contained" sx={{ mt: 2 }}>
          Test Button
        </Button>
      </Paper>
    </Box>
  )
}

export default SimpleTest