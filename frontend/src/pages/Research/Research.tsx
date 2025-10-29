import React, { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  IconButton,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Send,
  Mic,
  AttachFile,
  TrendingUp,
  Business,
  Analytics,
} from '@mui/icons-material'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const Research: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your AI investment research assistant. I can help you analyze companies, market trends, and provide investment insights. What would you like to research today?',
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I understand you're asking about "${inputValue}". This is a demo response. In the full application, I would analyze this query using our AI models and provide detailed investment insights, financial metrics, and market analysis.`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMessage])
      setIsLoading(false)
    }, 2000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickActions = [
    { label: 'Analyze AAPL', icon: <Business />, query: 'Analyze Apple Inc. (AAPL) stock' },
    { label: 'Market Overview', icon: <TrendingUp />, query: 'Give me a market overview for today' },
    { label: 'Tech Sector', icon: <Analytics />, query: 'How is the technology sector performing?' },
  ]

  const handleQuickAction = (query: string) => {
    setInputValue(query)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3, height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Research Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ask me anything about investments, companies, or market analysis.
        </Typography>
      </Box>

      {/* Quick Actions */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {quickActions.map((action, index) => (
            <Chip
              key={index}
              label={action.label}
              icon={action.icon}
              onClick={() => handleQuickAction(action.query)}
              clickable
              variant="outlined"
              sx={{ '&:hover': { bgcolor: 'primary.light', color: 'white' } }}
            />
          ))}
        </Box>
      </Box>

      {/* Chat Messages */}
      <Paper 
        sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column',
          mb: 2,
          bgcolor: 'background.default',
        }}
      >
        <Box 
          sx={{ 
            flexGrow: 1, 
            p: 2, 
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
          }}
        >
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                alignSelf: message.type === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
              }}
            >
              <Card
                sx={{
                  bgcolor: message.type === 'user' ? 'primary.main' : 'background.paper',
                  color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
                }}
              >
                <CardContent sx={{ '&:last-child': { pb: 2 } }}>
                  <Typography variant="body1">
                    {message.content}
                  </Typography>
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      opacity: 0.7,
                      display: 'block',
                      mt: 1,
                    }}
                  >
                    {message.timestamp.toLocaleTimeString()}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          ))}
          
          {isLoading && (
            <Box sx={{ alignSelf: 'flex-start', maxWidth: '80%' }}>
              <Card sx={{ bgcolor: 'background.paper' }}>
                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body1" color="text.secondary">
                    AI is thinking...
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          )}
        </Box>

        {/* Input Area */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Box display="flex" gap={1} alignItems="flex-end">
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about stocks, market trends, or investment strategies..."
              disabled={isLoading}
              variant="outlined"
              size="small"
            />
            <IconButton
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              sx={{ p: 1 }}
            >
              <Send />
            </IconButton>
            <IconButton sx={{ p: 1 }} disabled>
              <Mic />
            </IconButton>
            <IconButton sx={{ p: 1 }} disabled>
              <AttachFile />
            </IconButton>
          </Box>
          
          {/* Info Alert */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              This is a demo interface. In the full application, the AI would connect to our backend API 
              to provide real-time market data, financial analysis, and investment insights.
            </Typography>
          </Alert>
        </Box>
      </Paper>
    </Container>
  )
}

export default Research