import React from 'react';
import { Box, Typography } from '@mui/material';

const SimpleDashboard: React.FC = () => {
  console.log('SimpleDashboard component rendering');
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Simple Dashboard
      </Typography>
      <Typography variant="body1">
        This is a simplified dashboard for testing.
      </Typography>
      <Typography variant="body2" sx={{ mt: 2, color: 'success.main' }}>
        ✅ Dashboard component loaded successfully!
      </Typography>
    </Box>
  );
};

export default SimpleDashboard;