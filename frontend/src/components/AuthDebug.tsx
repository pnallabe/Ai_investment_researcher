import React from 'react'
import { Box, Typography, Paper, Button } from '@mui/material'
import { useAuth } from '@hooks/useAuth'

const AuthDebug: React.FC = () => {
  const { user, token, isAuthenticated, loading } = useAuth()

  return (
    <Paper sx={{ p: 3, m: 2 }}>
      <Typography variant="h6" gutterBottom>
        🔧 Authentication Debug Info
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2">
          <strong>Loading:</strong> {loading ? 'Yes' : 'No'}
        </Typography>
        <Typography variant="body2">
          <strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}
        </Typography>
        <Typography variant="body2">
          <strong>Has Token:</strong> {token ? 'Yes' : 'No'}
        </Typography>
        <Typography variant="body2">
          <strong>Has User:</strong> {user ? 'Yes' : 'No'}
        </Typography>
        {user && (
          <Typography variant="body2">
            <strong>User Email:</strong> {user.email}
          </Typography>
        )}
        {token && (
          <Typography variant="body2">
            <strong>Token (first 50 chars):</strong> {token.substring(0, 50)}...
          </Typography>
        )}
      </Box>
      
      <Box>
        <Typography variant="body2">
          <strong>LocalStorage Token:</strong> {localStorage.getItem('access_token') ? 'Present' : 'Missing'}
        </Typography>
        <Typography variant="body2">
          <strong>LocalStorage User:</strong> {localStorage.getItem('user') ? 'Present' : 'Missing'}
        </Typography>
      </Box>
      
      <Button 
        variant="outlined" 
        size="small" 
        sx={{ mt: 2 }}
        onClick={() => {
          console.log('Debug Info:', {
            user,
            token,
            isAuthenticated,
            loading,
            localStorage_token: localStorage.getItem('access_token'),
            localStorage_user: localStorage.getItem('user')
          })
        }}
      >
        Log to Console
      </Button>
    </Paper>
  )
}

export default AuthDebug