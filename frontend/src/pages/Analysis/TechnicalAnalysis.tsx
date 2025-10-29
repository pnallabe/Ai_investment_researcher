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
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    LinearProgress,
    Divider
} from '@mui/material';
import { TrendingUp, TrendingDown, Analytics, ShowChart, SignalCellularAlt } from '@mui/icons-material';

interface TechnicalAnalysisData {
    symbol: string;
    current_price: number;
    last_updated: string;
    moving_averages: {
        sma_20: number;
        sma_50: number;
        ema_12: number;
        ema_26: number;
    };
    momentum_indicators: {
        rsi: number;
        williams_r: number;
        roc: number;
    };
    macd: {
        macd_line: number;
        signal_line: number;
        histogram: number;
    };
    bollinger_bands: {
        upper: number;
        middle: number;
        lower: number;
    };
    stochastic: {
        k_percent: number;
        d_percent: number;
    };
    volume_analysis: {
        current_volume: number;
        volume_sma_20: number;
    };
    volatility: {
        atr: number;
    };
    signals: {
        rsi: string;
        ma_trend: string;
        macd: string;
        bollinger: string;
    };
}

const TechnicalAnalysis: React.FC = () => {
    const [symbol, setSymbol] = useState('AAPL');
    const [period, setPeriod] = useState('1y');
    const [analysisData, setAnalysisData] = useState<TechnicalAnalysisData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchAnalysis = async () => {
        if (!symbol.trim()) {
            setError('Please enter a stock symbol');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`/v1/analysis/technical/${encodeURIComponent(symbol)}?period=${period}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            setAnalysisData(data.technical_analysis);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch technical analysis');
            console.error('Technical analysis error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnalysis();
    }, []);

    const formatCurrency = (value: number | null | undefined) => {
        if (value === null || value === undefined || isNaN(value)) return 'N/A';
        return `$${value.toFixed(2)}`;
    };

    const formatNumber = (value: number | null | undefined, decimals: number = 2) => {
        if (value === null || value === undefined || isNaN(value)) return 'N/A';
        return value.toFixed(decimals);
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

    const getSignalIcon = (signal: string) => {
        switch (signal?.toUpperCase()) {
            case 'BULLISH':
                return <TrendingUp />;
            case 'BEARISH':
                return <TrendingDown />;
            default:
                return <SignalCellularAlt />;
        }
    };

    const getRSILevel = (rsi: number) => {
        if (rsi >= 70) return { level: 'Overbought', color: 'error' };
        if (rsi <= 30) return { level: 'Oversold', color: 'info' };
        if (rsi >= 50) return { level: 'Bullish', color: 'success' };
        return { level: 'Bearish', color: 'warning' };
    };

    const getBollingerPosition = (price: number, upper: number, lower: number, middle: number) => {
        if (price >= upper) return { position: 'Above Upper Band', color: 'warning' };
        if (price <= lower) return { position: 'Below Lower Band', color: 'info' };
        if (price >= middle) return { position: 'Above Middle', color: 'success' };
        return { position: 'Below Middle', color: 'default' };
    };

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                    <CircularProgress size={60} />
                    <Typography variant="h6" sx={{ ml: 2 }}>
                        Analyzing technical indicators...
                    </Typography>
                </Box>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <ShowChart sx={{ mr: 2, color: 'primary.main' }} />
                    Technical Analysis
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                    <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                label="Stock Symbol"
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                                placeholder="AAPL"
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <TextField
                                fullWidth
                                select
                                label="Time Period"
                                value={period}
                                onChange={(e) => setPeriod(e.target.value)}
                                SelectProps={{
                                    native: true,
                                }}
                            >
                                <option value="3mo">3 Months</option>
                                <option value="6mo">6 Months</option>
                                <option value="1y">1 Year</option>
                                <option value="2y">2 Years</option>
                                <option value="5y">5 Years</option>
                            </TextField>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Button
                                variant="contained"
                                onClick={fetchAnalysis}
                                disabled={loading}
                                startIcon={<Analytics />}
                                fullWidth
                                size="large"
                            >
                                Analyze
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

            {analysisData && (
                <>
                    {/* Overview Card */}
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                {analysisData.symbol} - Technical Overview
                            </Typography>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={3}>
                                    <Typography variant="body2" color="text.secondary">Current Price</Typography>
                                    <Typography variant="h4" color="primary">
                                        {formatCurrency(analysisData.current_price)}
                                    </Typography>
                                </Grid>
                                <Grid item xs={12} md={9}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Trading Signals
                                    </Typography>
                                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                        {Object.entries(analysisData.signals).map(([key, value]) => (
                                            <Chip
                                                key={key}
                                                label={`${key.toUpperCase()}: ${value}`}
                                                color={getSignalColor(value)}
                                                icon={getSignalIcon(value)}
                                                variant="outlined"
                                            />
                                        ))}
                                    </Box>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>

                    <Grid container spacing={3}>
                        {/* Moving Averages */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                        <TrendingUp sx={{ mr: 1 }} />
                                        Moving Averages
                                    </Typography>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>SMA (20)</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.moving_averages.sma_20)}
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={analysisData.current_price > analysisData.moving_averages.sma_20 ? 'Above' : 'Below'}
                                                            color={analysisData.current_price > analysisData.moving_averages.sma_20 ? 'success' : 'error'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>SMA (50)</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.moving_averages.sma_50)}
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={analysisData.current_price > analysisData.moving_averages.sma_50 ? 'Above' : 'Below'}
                                                            color={analysisData.current_price > analysisData.moving_averages.sma_50 ? 'success' : 'error'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>EMA (12)</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.moving_averages.ema_12)}
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={analysisData.current_price > analysisData.moving_averages.ema_12 ? 'Above' : 'Below'}
                                                            color={analysisData.current_price > analysisData.moving_averages.ema_12 ? 'success' : 'error'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>EMA (26)</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.moving_averages.ema_26)}
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={analysisData.current_price > analysisData.moving_averages.ema_26 ? 'Above' : 'Below'}
                                                            color={analysisData.current_price > analysisData.moving_averages.ema_26 ? 'success' : 'error'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Momentum Indicators */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Momentum Indicators
                                    </Typography>
                                    
                                    <Box sx={{ mb: 3 }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                            <Typography variant="body2">RSI (14)</Typography>
                                            <Typography variant="body2">
                                                {formatNumber(analysisData.momentum_indicators.rsi, 1)}
                                            </Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={analysisData.momentum_indicators.rsi}
                                            sx={{ height: 8, borderRadius: 4 }}
                                            color={getRSILevel(analysisData.momentum_indicators.rsi).color as any}
                                        />
                                        <Box sx={{ mt: 1 }}>
                                            <Chip
                                                label={getRSILevel(analysisData.momentum_indicators.rsi).level}
                                                color={getRSILevel(analysisData.momentum_indicators.rsi).color as any}
                                                size="small"
                                            />
                                        </Box>
                                    </Box>

                                    <Divider sx={{ my: 2 }} />

                                    <TableContainer>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>Williams %R</TableCell>
                                                    <TableCell align="right">
                                                        {formatNumber(analysisData.momentum_indicators.williams_r, 1)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Rate of Change</TableCell>
                                                    <TableCell align="right">
                                                        {formatNumber(analysisData.momentum_indicators.roc, 1)}%
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* MACD */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        MACD Analysis
                                    </Typography>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>MACD Line</TableCell>
                                                    <TableCell align="right">
                                                        {formatNumber(analysisData.macd.macd_line, 3)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Signal Line</TableCell>
                                                    <TableCell align="right">
                                                        {formatNumber(analysisData.macd.signal_line, 3)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Histogram</TableCell>
                                                    <TableCell align="right">
                                                        {formatNumber(analysisData.macd.histogram, 3)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><strong>Signal</strong></TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={analysisData.signals.macd}
                                                            color={getSignalColor(analysisData.signals.macd)}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Bollinger Bands */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Bollinger Bands
                                    </Typography>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>Upper Band</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.bollinger_bands.upper)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Middle Band (SMA 20)</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.bollinger_bands.middle)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Lower Band</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.bollinger_bands.lower)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><strong>Position</strong></TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={getBollingerPosition(
                                                                analysisData.current_price,
                                                                analysisData.bollinger_bands.upper,
                                                                analysisData.bollinger_bands.lower,
                                                                analysisData.bollinger_bands.middle
                                                            ).position}
                                                            color={getBollingerPosition(
                                                                analysisData.current_price,
                                                                analysisData.bollinger_bands.upper,
                                                                analysisData.bollinger_bands.lower,
                                                                analysisData.bollinger_bands.middle
                                                            ).color as any}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Stochastic Oscillator */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Stochastic Oscillator
                                    </Typography>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>%K</TableCell>
                                                    <TableCell align="right">
                                                        {formatNumber(analysisData.stochastic.k_percent, 1)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>%D</TableCell>
                                                    <TableCell align="right">
                                                        {formatNumber(analysisData.stochastic.d_percent, 1)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><strong>Level</strong></TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={analysisData.stochastic.k_percent > 80 ? 'Overbought' : 
                                                                   analysisData.stochastic.k_percent < 20 ? 'Oversold' : 'Neutral'}
                                                            color={analysisData.stochastic.k_percent > 80 ? 'warning' : 
                                                                   analysisData.stochastic.k_percent < 20 ? 'info' : 'default'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Volume & Volatility */}
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Volume & Volatility
                                    </Typography>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>Current Volume</TableCell>
                                                    <TableCell align="right">
                                                        {analysisData.volume_analysis.current_volume?.toLocaleString() || 'N/A'}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Volume SMA (20)</TableCell>
                                                    <TableCell align="right">
                                                        {analysisData.volume_analysis.volume_sma_20?.toLocaleString() || 'N/A'}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>ATR (Volatility)</TableCell>
                                                    <TableCell align="right">
                                                        {formatCurrency(analysisData.volatility.atr)}
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell><strong>Volume Status</strong></TableCell>
                                                    <TableCell align="right">
                                                        <Chip
                                                            label={analysisData.volume_analysis.current_volume > analysisData.volume_analysis.volume_sma_20 ? 'Above Average' : 'Below Average'}
                                                            color={analysisData.volume_analysis.current_volume > analysisData.volume_analysis.volume_sma_20 ? 'success' : 'default'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    <Paper sx={{ p: 2, mt: 3, bgcolor: 'grey.50' }}>
                        <Typography variant="caption" color="text.secondary">
                            Last updated: {new Date(analysisData.last_updated).toLocaleString()}
                        </Typography>
                    </Paper>
                </>
            )}
        </Container>
    );
};

export default TechnicalAnalysis;