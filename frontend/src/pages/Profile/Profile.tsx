import React from 'react'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Avatar,
  Divider,
  Button,
} from '@mui/material'
import {
  Person,
  Email,
  DateRange,
  Edit,
} from '@mui/icons-material'
import { useAuth } from '@hooks/useAuth'

const Profile: React.FC = () => {
  const { user } = useAuth()

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Profile
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={4}>
        Manage your account settings and preferences.
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Info */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <Avatar
                  sx={{
                    width: 80,
                    height: 80,
                    bgcolor: 'primary.main',
                    fontSize: '2rem',
                    mr: 3,
                  }}
                >
                  {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
                </Avatar>
                <Box>
                  <Typography variant="h5" gutterBottom>
                    {user?.first_name} {user?.last_name} {user?.username}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {user?.email}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Profile Details */}
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Person color="action" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="subtitle2">Username</Typography>
                      <Typography variant="body1">
                        {user?.username || 'Not set'}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Email color="action" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="subtitle2">Email</Typography>
                      <Typography variant="body1">
                        {user?.email || 'Not set'}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <DateRange color="action" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="subtitle2">Member Since</Typography>
                      <Typography variant="body1">
                        {user?.created_at 
                          ? new Date(user.created_at).toLocaleDateString()
                          : 'Unknown'
                        }
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>

              <Box mt={3}>
                <Button
                  variant="contained"
                  startIcon={<Edit />}
                  disabled
                >
                  Edit Profile
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Stats
              </Typography>
              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Total Research Queries
                </Typography>
                <Typography variant="h6">147</Typography>
              </Box>
              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Portfolio Value
                </Typography>
                <Typography variant="h6">$124,567</Typography>
              </Box>
              <Box mb={2}>
                <Typography variant="body2" color="text.secondary">
                  Companies Analyzed
                </Typography>
                <Typography variant="h6">23</Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Settings */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Settings
              </Typography>
              <Button fullWidth variant="outlined" sx={{ mb: 1 }} disabled>
                Change Password
              </Button>
              <Button fullWidth variant="outlined" sx={{ mb: 1 }} disabled>
                Notification Settings
              </Button>
              <Button fullWidth variant="outlined" disabled>
                Export Data
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  )
}

export default Profile