import React, { useState, useEffect } from 'react';
import {
    Container,
    Paper,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Button,
    Chip,
    CircularProgress,
    Alert,
    Tabs,
    Tab,
    Divider
} from '@mui/material';
import { TrendingUp, TrendingDown, CompareArrows, Analytics, Assessment } from '@mui/icons-material';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`comparison-tabpanel-${index}`}
            aria-labelledby={`comparison-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

interface StockData {
    symbol: string;
    current_price: number;
    rsi: number;
    pe_ratio: number;
    roe: number;
    revenue_growth: number;
    investment_score: number;
    investment_rating: string;
    technical_signals: {
        rsi: string;
        ma_trend: string;
        macd: string;
        bollinger: string;
    };
    market_cap: number;
}

interface ComparisonData {
    symbols: string[];
    comparison_matrix: { [key: string]: StockData };
    detailed_technical: any;
    detailed_fundamental: any;
}

const StockComparison: React.FC = () => {
    const [symbols, setSymbols] = useState('AAPL,MSFT,GOOGL');
    const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [tabValue, setTabValue] = useState(0);

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    const fetchComparisonData = async () => {
        if (!symbols.trim()) {
            setError('Please enter stock symbols');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`/v1/analysis/stock-comparison?symbols=${encodeURIComponent(symbols)}&period=1y`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            setComparisonData(data.stock_comparison);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch comparison data');
            console.error('Comparison error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchComparisonData();
    }, []);

    const formatCurrency = (value: number | null | undefined) => {
        if (value === null || value === undefined || isNaN(value)) return 'N/A';
        return `$${value.toFixed(2)}`;
    };

    const formatPercentage = (value: number | null | undefined) => {
        if (value === null || value === undefined || isNaN(value)) return 'N/A';
        return `${(value * 100).toFixed(2)}%`;
    };

    const formatNumber = (value: number | null | undefined, decimals: number = 2) => {
        if (value === null || value === undefined || isNaN(value)) return 'N/A';
        return value.toFixed(decimals);
    };

    const formatMarketCap = (value: number | null | undefined) => {
        if (value === null || value === undefined || isNaN(value)) return 'N/A';
        
        if (value >= 1e12) {
            return `$${(value / 1e12).toFixed(2)}T`;
        } else if (value >= 1e9) {
            return `$${(value / 1e9).toFixed(2)}B`;
        } else if (value >= 1e6) {
            return `$${(value / 1e6).toFixed(2)}M`;
        }
        return `$${value.toFixed(0)}`;
    };

    const getSignalColor = (signal: string) => {
        switch (signal?.toUpperCase()) {
            case 'BULLISH':
            case 'BUY':
                return 'success';
            case 'BEARISH':
            case 'SELL':
                return 'error';
            case 'OVERBOUGHT':
                return 'warning';
            case 'OVERSOLD':
                return 'info';
            case 'NEUTRAL':
            case 'HOLD':
            default:
                return 'default';
        }
    };

    const getRatingColor = (rating: string) => {
        switch (rating?.toUpperCase()) {
            case 'STRONG BUY':
                return 'success';
            case 'BUY':
                return 'info';
            case 'HOLD':
                return 'warning';
            case 'SELL':
            case 'WEAK HOLD':
                return 'error';
            default:
                return 'default';
        }
    };

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                    <CircularProgress size={60} />
                    <Typography variant="h6" sx={{ ml: 2 }}>
                        Analyzing stocks...
                    </Typography>
                </Box>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <CompareArrows sx={{ mr: 2, color: 'primary.main' }} />
                    Stock Comparison Analysis
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={8}>
                            <TextField
                                fullWidth
                                label="Stock Symbols (comma-separated)"
                                value={symbols}
                                onChange={(e) => setSymbols(e.target.value)}
                                placeholder="AAPL,MSFT,GOOGL,TSLA"
                                helperText="Enter 2-10 stock symbols separated by commas"
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Button
                                variant="contained"
                                onClick={fetchComparisonData}
                                disabled={loading}
                                startIcon={<Analytics />}
                                fullWidth
                                size="large"
                            >
                                Compare Stocks
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

            {comparisonData && (
                <Paper sx={{ p: 3 }}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                        <Tabs value={tabValue} onChange={handleTabChange} aria-label="comparison tabs">
                            <Tab label="Overview" icon={<Assessment />} />
                            <Tab label="Technical Analysis" icon={<TrendingUp />} />
                            <Tab label="Fundamental Analysis" icon={<Analytics />} />
                        </Tabs>
                    </Box>

                    <TabPanel value={tabValue} index={0}>
                        <Typography variant="h5" gutterBottom>
                            Stock Comparison Overview
                        </Typography>
                        
                        <TableContainer component={Paper} variant="outlined">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell><strong>Metric</strong></TableCell>
                                        {comparisonData.symbols.map((symbol) => (
                                            <TableCell key={symbol} align="center">
                                                <strong>{symbol}</strong>
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    <TableRow>
                                        <TableCell>Current Price</TableCell>
                                        {comparisonData.symbols.map((symbol) => (
                                            <TableCell key={symbol} align="center">
                                                {formatCurrency(comparisonData.comparison_matrix[symbol]?.current_price)}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Market Cap</TableCell>
                                        {comparisonData.symbols.map((symbol) => (
                                            <TableCell key={symbol} align="center">
                                                {formatMarketCap(comparisonData.comparison_matrix[symbol]?.market_cap)}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Investment Score</TableCell>
                                        {comparisonData.symbols.map((symbol) => (
                                            <TableCell key={symbol} align="center">
                                                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                                    <Typography variant="h6">
                                                        {comparisonData.comparison_matrix[symbol]?.investment_score || 'N/A'}
                                                    </Typography>
                                                    <Chip
                                                        label={comparisonData.comparison_matrix[symbol]?.investment_rating || 'N/A'}
                                                        color={getRatingColor(comparisonData.comparison_matrix[symbol]?.investment_rating)}
                                                        size="small"
                                                    />
                                                </Box>
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>P/E Ratio</TableCell>
                                        {comparisonData.symbols.map((symbol) => (
                                            <TableCell key={symbol} align="center">
                                                {formatNumber(comparisonData.comparison_matrix[symbol]?.pe_ratio)}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>ROE</TableCell>
                                        {comparisonData.symbols.map((symbol) => (
                                            <TableCell key={symbol} align="center">
                                                {formatPercentage(comparisonData.comparison_matrix[symbol]?.roe)}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                    <TableRow>
                                        <TableCell>Revenue Growth</TableCell>
                                        {comparisonData.symbols.map((symbol) => (
                                            <TableCell key={symbol} align="center">
                                                {formatPercentage(comparisonData.comparison_matrix[symbol]?.revenue_growth)}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </TabPanel>

                    <TabPanel value={tabValue} index={1}>
                        <Typography variant="h5" gutterBottom>
                            Technical Analysis Comparison
                        </Typography>
                        
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <TableContainer component={Paper} variant="outlined">
                                    <Table>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell><strong>Technical Indicator</strong></TableCell>
                                                {comparisonData.symbols.map((symbol) => (
                                                    <TableCell key={symbol} align="center">
                                                        <strong>{symbol}</strong>
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            <TableRow>
                                                <TableCell>RSI (14)</TableCell>
                                                {comparisonData.symbols.map((symbol) => (
                                                    <TableCell key={symbol} align="center">
                                                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                                            <Typography>
                                                                {formatNumber(comparisonData.comparison_matrix[symbol]?.rsi, 1)}
                                                            </Typography>
                                                            <Chip
                                                                label={comparisonData.comparison_matrix[symbol]?.technical_signals?.rsi || 'N/A'}
                                                                color={getSignalColor(comparisonData.comparison_matrix[symbol]?.technical_signals?.rsi)}
                                                                size="small"
                                                            />
                                                        </Box>
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                            <TableRow>
                                                <TableCell>Trend Direction</TableCell>
                                                {comparisonData.symbols.map((symbol) => (
                                                    <TableCell key={symbol} align="center">
                                                        <Chip
                                                            label={comparisonData.comparison_matrix[symbol]?.technical_signals?.ma_trend || 'N/A'}
                                                            color={getSignalColor(comparisonData.comparison_matrix[symbol]?.technical_signals?.ma_trend)}
                                                            icon={comparisonData.comparison_matrix[symbol]?.technical_signals?.ma_trend === 'BULLISH' ? <TrendingUp /> : <TrendingDown />}
                                                        />
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                            <TableRow>
                                                <TableCell>MACD Signal</TableCell>
                                                {comparisonData.symbols.map((symbol) => (
                                                    <TableCell key={symbol} align="center">
                                                        <Chip
                                                            label={comparisonData.comparison_matrix[symbol]?.technical_signals?.macd || 'N/A'}
                                                            color={getSignalColor(comparisonData.comparison_matrix[symbol]?.technical_signals?.macd)}
                                                        />
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                            <TableRow>
                                                <TableCell>Bollinger Bands</TableCell>
                                                {comparisonData.symbols.map((symbol) => (
                                                    <TableCell key={symbol} align="center">
                                                        <Chip
                                                            label={comparisonData.comparison_matrix[symbol]?.technical_signals?.bollinger || 'N/A'}
                                                            color={getSignalColor(comparisonData.comparison_matrix[symbol]?.technical_signals?.bollinger)}
                                                        />
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </Grid>
                        </Grid>
                    </TabPanel>

                    <TabPanel value={tabValue} index={2}>
                        <Typography variant="h5" gutterBottom>
                            Fundamental Analysis Comparison
                        </Typography>
                        
                        <Grid container spacing={3}>
                            {comparisonData.symbols.map((symbol) => (
                                <Grid item xs={12} md={6} lg={4} key={symbol}>
                                    <Card>
                                        <CardContent>
                                            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                                {symbol}
                                                <Chip
                                                    label={comparisonData.comparison_matrix[symbol]?.investment_rating || 'N/A'}
                                                    color={getRatingColor(comparisonData.comparison_matrix[symbol]?.investment_rating)}
                                                />
                                            </Typography>
                                            <Divider sx={{ mb: 2 }} />
                                            
                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" color="text.secondary">
                                                    Current Price
                                                </Typography>
                                                <Typography variant="h6">
                                                    {formatCurrency(comparisonData.comparison_matrix[symbol]?.current_price)}
                                                </Typography>
                                            </Box>

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" color="text.secondary">
                                                    Market Cap
                                                </Typography>
                                                <Typography variant="body1">
                                                    {formatMarketCap(comparisonData.comparison_matrix[symbol]?.market_cap)}
                                                </Typography>
                                            </Box>

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" color="text.secondary">
                                                    Investment Score
                                                </Typography>
                                                <Typography variant="h6" color="primary">
                                                    {comparisonData.comparison_matrix[symbol]?.investment_score || 'N/A'}/100
                                                </Typography>
                                            </Box>

                                            <Grid container spacing={1}>
                                                <Grid item xs={6}>
                                                    <Typography variant="body2" color="text.secondary">P/E Ratio</Typography>
                                                    <Typography variant="body1">
                                                        {formatNumber(comparisonData.comparison_matrix[symbol]?.pe_ratio)}
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <Typography variant="body2" color="text.secondary">ROE</Typography>
                                                    <Typography variant="body1">
                                                        {formatPercentage(comparisonData.comparison_matrix[symbol]?.roe)}
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </TabPanel>
                </Paper>
            )}
        </Container>
    );
};

export default StockComparison;