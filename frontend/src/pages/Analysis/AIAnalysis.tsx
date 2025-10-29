import React, { useState, useEffect } from 'react';
import {
    Container,
    Paper,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    TextField,
    Button,
    Chip,
    CircularProgress,
    Alert,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    LinearProgress
} from '@mui/material';
import { 
    Psychology, 
    TrendingUp, 
    Warning, 
    Lightbulb, 
    Assessment,
    ExpandMore,
    SmartToy,
    Insights,
    RecommendOutlined
} from '@mui/icons-material';

interface AIInsight {
    type: string;
    confidence: number;
    recommendation: string;
    reasoning: string;
    key_factors: string[];
    risk_level: string;
    time_horizon: string;
    action_items: string[];
}

interface AIAnalysisData {
    symbol: string;
    analysis_type: string;
    overall_recommendation: string;
    confidence_score: number;
    investment_thesis: string;
    key_insights: AIInsight[];
    risk_factors: string[];
    opportunities: string[];
    price_targets: {
        conservative: number;
        fair_value: number;
        optimistic: number;
    };
    summary: string;
    timestamp: string;
}

interface MarketSentiment {
    sentiment: string;
    confidence: number;
    market_direction: string;
    key_themes: string[];
    recommended_positioning: string;
    analysis: string;
    timestamp: string;
}

const AIAnalysis: React.FC = () => {
    const [symbol, setSymbol] = useState('AAPL');
    const [period, setPeriod] = useState('1y');
    const [provider, setProvider] = useState('mock');
    const [analysisData, setAnalysisData] = useState<AIAnalysisData | null>(null);
    const [marketSentiment, setMarketSentiment] = useState<MarketSentiment | null>(null);
    const [loading, setLoading] = useState(false);
    const [sentimentLoading, setSentimentLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [analysisType, setAnalysisType] = useState<'stock' | 'market'>('stock');

    const fetchAIAnalysis = async () => {
        if (!symbol.trim()) {
            setError('Please enter a stock symbol');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`/v1/analysis/ai/${encodeURIComponent(symbol)}?period=${period}&provider=${provider}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            setAnalysisData(data.ai_analysis);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch AI analysis');
            console.error('AI analysis error:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchMarketSentiment = async () => {
        setSentimentLoading(true);
        setError(null);

        try {
            const response = await fetch(`/v1/analysis/ai-market-sentiment?provider=${provider}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            setMarketSentiment(data.market_sentiment_analysis);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch market sentiment');
            console.error('Market sentiment error:', err);
        } finally {
            setSentimentLoading(false);
        }
    };

    useEffect(() => {
        if (analysisType === 'stock') {
            fetchAIAnalysis();
        } else {
            fetchMarketSentiment();
        }
    }, [analysisType]);

    const getRecommendationColor = (recommendation: string) => {
        switch (recommendation?.toUpperCase()) {
            case 'BUY':
            case 'STRONG BUY':
                return 'success';
            case 'SELL':
            case 'STRONG SELL':
                return 'error';
            case 'HOLD':
                return 'warning';
            default:
                return 'default';
        }
    };

    const getRiskLevelColor = (riskLevel: string) => {
        switch (riskLevel?.toUpperCase()) {
            case 'LOW':
                return 'success';
            case 'MODERATE':
                return 'warning';
            case 'HIGH':
            case 'VERY HIGH':
                return 'error';
            default:
                return 'default';
        }
    };

    const getSentimentColor = (sentiment: string) => {
        switch (sentiment?.toUpperCase()) {
            case 'BULLISH':
            case 'POSITIVE':
                return 'success';
            case 'BEARISH':
            case 'NEGATIVE':
                return 'error';
            case 'NEUTRAL':
                return 'warning';
            default:
                return 'default';
        }
    };

    const formatConfidence = (confidence: number) => {
        return `${(confidence * 100).toFixed(0)}%`;
    };

    if (loading || sentimentLoading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                    <CircularProgress size={60} />
                    <Typography variant="h6" sx={{ ml: 2 }}>
                        {analysisType === 'stock' ? 'Generating AI insights...' : 'Analyzing market sentiment...'}
                    </Typography>
                </Box>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <Psychology sx={{ mr: 2, color: 'primary.main' }} />
                    AI-Powered Investment Analysis
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={2}>
                            <FormControl fullWidth>
                                <InputLabel>Analysis Type</InputLabel>
                                <Select
                                    value={analysisType}
                                    onChange={(e) => setAnalysisType(e.target.value as 'stock' | 'market')}
                                    label="Analysis Type"
                                >
                                    <MenuItem value="stock">Stock Analysis</MenuItem>
                                    <MenuItem value="market">Market Sentiment</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        
                        {analysisType === 'stock' && (
                            <>
                                <Grid item xs={12} md={3}>
                                    <TextField
                                        fullWidth
                                        label="Stock Symbol"
                                        value={symbol}
                                        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                                        placeholder="AAPL"
                                    />
                                </Grid>
                                <Grid item xs={12} md={2}>
                                    <FormControl fullWidth>
                                        <InputLabel>Period</InputLabel>
                                        <Select
                                            value={period}
                                            onChange={(e) => setPeriod(e.target.value)}
                                            label="Period"
                                        >
                                            <MenuItem value="3mo">3 Months</MenuItem>
                                            <MenuItem value="6mo">6 Months</MenuItem>
                                            <MenuItem value="1y">1 Year</MenuItem>
                                            <MenuItem value="2y">2 Years</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                            </>
                        )}
                        
                        <Grid item xs={12} md={2}>
                            <FormControl fullWidth>
                                <InputLabel>AI Provider</InputLabel>
                                <Select
                                    value={provider}
                                    onChange={(e) => setProvider(e.target.value)}
                                    label="AI Provider"
                                >
                                    <MenuItem value="mock">Demo (Mock)</MenuItem>
                                    <MenuItem value="openai">OpenAI GPT-4</MenuItem>
                                    <MenuItem value="anthropic">Anthropic Claude</MenuItem>
                                    <MenuItem value="groq">Groq Mixtral</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        
                        <Grid item xs={12} md={3}>
                            <Button
                                variant="contained"
                                onClick={analysisType === 'stock' ? fetchAIAnalysis : fetchMarketSentiment}
                                disabled={loading || sentimentLoading}
                                startIcon={<SmartToy />}
                                fullWidth
                                size="large"
                            >
                                Generate AI Analysis
                            </Button>
                        </Grid>
                    </Grid>
                </Box>

                {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                        {error}
                    </Alert>
                )}
            </Paper>

            {/* Stock Analysis Results */}
            {analysisType === 'stock' && analysisData && (
                <>
                    {/* Overview Card */}
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                AI Analysis for {analysisData.symbol}
                            </Typography>
                            
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Overall Recommendation
                                        </Typography>
                                        <Chip
                                            label={analysisData.overall_recommendation}
                                            color={getRecommendationColor(analysisData.overall_recommendation)}
                                            size="medium"
                                            sx={{ fontSize: '1.2rem', p: 2, mt: 1 }}
                                        />
                                    </Box>
                                </Grid>
                                
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            AI Confidence
                                        </Typography>
                                        <Typography variant="h4" color="primary" sx={{ mt: 1 }}>
                                            {formatConfidence(analysisData.confidence_score)}
                                        </Typography>
                                        <LinearProgress
                                            variant="determinate"
                                            value={analysisData.confidence_score * 100}
                                            sx={{ mt: 1, height: 8, borderRadius: 4 }}
                                        />
                                    </Box>
                                </Grid>
                                
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Analysis Type
                                        </Typography>
                                        <Typography variant="h6" sx={{ mt: 1, textTransform: 'capitalize' }}>
                                            {analysisData.analysis_type.replace('_', ' ')}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Provider: {provider.toUpperCase()}
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>

                    {/* Investment Thesis */}
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                <Lightbulb sx={{ mr: 1 }} />
                                Investment Thesis
                            </Typography>
                            <Paper 
                                variant="outlined" 
                                sx={{ 
                                    p: 3, 
                                    bgcolor: 'grey.50', 
                                    borderRadius: 2,
                                    maxHeight: 'none',
                                    overflow: 'visible'
                                }}
                            >
                                <Typography 
                                    variant="body1" 
                                    sx={{ 
                                        lineHeight: 1.8,
                                        whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word',
                                        fontSize: '1rem',
                                        textAlign: 'justify',
                                        minHeight: 'auto',
                                        '& p': {
                                            marginBottom: 2
                                        }
                                    }}
                                >
                                    {analysisData.investment_thesis}
                                </Typography>
                            </Paper>
                        </CardContent>
                    </Card>

                    {/* Key Insights */}
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                <Insights sx={{ mr: 1 }} />
                                Key AI Insights
                            </Typography>
                            
                            {analysisData.key_insights.map((insight, index) => (
                                <Accordion key={index} sx={{ mb: 2 }}>
                                    <AccordionSummary expandIcon={<ExpandMore />}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                                            <Typography sx={{ flexGrow: 1, textTransform: 'capitalize' }}>
                                                {insight.type.replace('_', ' ')} Analysis
                                            </Typography>
                                            <Chip
                                                label={insight.recommendation}
                                                color={getRecommendationColor(insight.recommendation)}
                                                size="small"
                                                sx={{ mr: 2 }}
                                            />
                                            <Chip
                                                label={formatConfidence(insight.confidence)}
                                                variant="outlined"
                                                size="small"
                                            />
                                        </Box>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <Grid container spacing={2}>
                                            <Grid item xs={12} md={8}>
                                                <Box sx={{ mb: 2 }}>
                                                    <Typography variant="body2" gutterBottom>
                                                        <strong>Reasoning:</strong>
                                                    </Typography>
                                                    <Typography 
                                                        variant="body2" 
                                                        sx={{ 
                                                            whiteSpace: 'pre-wrap',
                                                            lineHeight: 1.6,
                                                            wordBreak: 'break-word',
                                                            pl: 2,
                                                            borderLeft: '3px solid',
                                                            borderColor: 'primary.light',
                                                            bgcolor: 'grey.50',
                                                            p: 2,
                                                            borderRadius: 1
                                                        }}
                                                    >
                                                        {insight.reasoning}
                                                    </Typography>
                                                </Box>
                                                
                                                <Typography variant="body2" gutterBottom>
                                                    <strong>Key Factors:</strong>
                                                </Typography>
                                                <List dense>
                                                    {insight.key_factors.map((factor, idx) => (
                                                        <ListItem key={idx}>
                                                            <ListItemIcon>
                                                                <Assessment fontSize="small" />
                                                            </ListItemIcon>
                                                            <ListItemText primary={factor} />
                                                        </ListItem>
                                                    ))}
                                                </List>
                                            </Grid>
                                            
                                            <Grid item xs={12} md={4}>
                                                <Box sx={{ mb: 2 }}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Risk Level
                                                    </Typography>
                                                    <Chip
                                                        label={insight.risk_level}
                                                        color={getRiskLevelColor(insight.risk_level)}
                                                        size="small"
                                                    />
                                                </Box>
                                                
                                                <Box sx={{ mb: 2 }}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Time Horizon
                                                    </Typography>
                                                    <Typography variant="body2">
                                                        {insight.time_horizon}
                                                    </Typography>
                                                </Box>
                                                
                                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                                    Action Items:
                                                </Typography>
                                                <List dense>
                                                    {insight.action_items.map((item, idx) => (
                                                        <ListItem key={idx}>
                                                            <ListItemIcon>
                                                                <RecommendOutlined fontSize="small" />
                                                            </ListItemIcon>
                                                            <ListItemText 
                                                                primary={item}
                                                                primaryTypographyProps={{ variant: 'caption' }}
                                                            />
                                                        </ListItem>
                                                    ))}
                                                </List>
                                            </Grid>
                                        </Grid>
                                    </AccordionDetails>
                                </Accordion>
                            ))}
                        </CardContent>
                    </Card>

                    {/* Risk Factors and Opportunities */}
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                        <Warning sx={{ mr: 1, color: 'warning.main' }} />
                                        Risk Factors
                                    </Typography>
                                    <List>
                                        {analysisData.risk_factors.map((risk, index) => (
                                            <ListItem key={index}>
                                                <ListItemIcon>
                                                    <Warning color="warning" />
                                                </ListItemIcon>
                                                <ListItemText primary={risk} />
                                            </ListItem>
                                        ))}
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                        <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                                        Opportunities
                                    </Typography>
                                    <List>
                                        {analysisData.opportunities.map((opportunity, index) => (
                                            <ListItem key={index}>
                                                <ListItemIcon>
                                                    <TrendingUp color="success" />
                                                </ListItemIcon>
                                                <ListItemText primary={opportunity} />
                                            </ListItem>
                                        ))}
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </>
            )}

            {/* Market Sentiment Results */}
            {analysisType === 'market' && marketSentiment && (
                <>
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                AI Market Sentiment Analysis
                            </Typography>
                            
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Market Sentiment
                                        </Typography>
                                        <Chip
                                            label={marketSentiment.sentiment}
                                            color={getSentimentColor(marketSentiment.sentiment)}
                                            size="medium"
                                            sx={{ fontSize: '1.2rem', p: 2, mt: 1 }}
                                        />
                                    </Box>
                                </Grid>
                                
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Confidence
                                        </Typography>
                                        <Typography variant="h4" color="primary" sx={{ mt: 1 }}>
                                            {formatConfidence(marketSentiment.confidence)}
                                        </Typography>
                                    </Box>
                                </Grid>
                                
                                <Grid item xs={12} md={4}>
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Typography variant="body2" color="text.secondary">
                                            Market Direction
                                        </Typography>
                                        <Typography variant="h6" sx={{ mt: 1 }}>
                                            {marketSentiment.market_direction}
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>

                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Key Market Themes
                                    </Typography>
                                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                        {marketSentiment.key_themes.map((theme, index) => (
                                            <Chip key={index} label={theme} variant="outlined" />
                                        ))}
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Recommended Positioning
                                    </Typography>
                                    <Typography variant="body1">
                                        {marketSentiment.recommended_positioning}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    <Card sx={{ mt: 3 }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Detailed Analysis
                            </Typography>
                            <Paper 
                                variant="outlined" 
                                sx={{ 
                                    p: 3, 
                                    bgcolor: 'grey.50', 
                                    borderRadius: 2,
                                    maxHeight: 'none',
                                    overflow: 'visible'
                                }}
                            >
                                <Typography 
                                    variant="body1" 
                                    sx={{ 
                                        whiteSpace: 'pre-wrap', 
                                        lineHeight: 1.8,
                                        wordBreak: 'break-word',
                                        fontSize: '1rem',
                                        textAlign: 'justify',
                                        minHeight: 'auto',
                                        '& p': {
                                            marginBottom: 2
                                        }
                                    }}
                                >
                                    {marketSentiment.analysis}
                                </Typography>
                            </Paper>
                        </CardContent>
                    </Card>
                </>
            )}

            {/* Timestamp */}
            {(analysisData || marketSentiment) && (
                <Paper sx={{ p: 2, mt: 3, bgcolor: 'grey.50' }}>
                    <Typography variant="caption" color="text.secondary">
                        Analysis generated: {new Date(analysisData?.timestamp || marketSentiment?.timestamp || '').toLocaleString()}
                        {' | '}Provider: {provider.toUpperCase()}
                    </Typography>
                </Paper>
            )}
        </Container>
    );
};

export default AIAnalysis;