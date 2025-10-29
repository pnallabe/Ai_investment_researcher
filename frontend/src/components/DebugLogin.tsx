import React, { useState } from 'react';
import { Box, Typography, Button, TextField, Alert } from '@mui/material';
import { authService } from '@services/authService';

const DebugLogin: React.FC = () => {
  const [email, setEmail] = useState('demo@example.com');
  const [password, setPassword] = useState('demo123');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const testLogin = async () => {
    try {
      console.log('Testing login with:', { email, password });
      setError(null);
      setResult(null);
      
      const response = await authService.login(email, password);
      console.log('Login response:', response);
      setResult(response);
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed');
    }
  };

  const testAuth = async () => {
    try {
      console.log('Testing auth check');
      const user = await authService.getProfile();
      console.log('Current user:', user);
      setResult({ currentUser: user });
    } catch (err: any) {
      console.error('Auth check error:', err);
      setError(err.message || 'Auth check failed');
    }
  };

  const testToken = () => {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    console.log('Stored token:', token);
    console.log('Stored user:', user);
    setResult({ storedToken: token, storedUser: user });
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Debug Login
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          margin="normal"
        />
      </Box>

      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button variant="contained" onClick={testLogin}>
          Test Login
        </Button>
        <Button variant="outlined" onClick={testAuth}>
          Test Auth Check
        </Button>
        <Button variant="outlined" onClick={testToken}>
          Check Token
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="h6" gutterBottom>
            Result:
          </Typography>
          <pre style={{ fontSize: '12px', overflow: 'auto' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Box>
      )}
    </Box>
  );
};

export default DebugLogin;