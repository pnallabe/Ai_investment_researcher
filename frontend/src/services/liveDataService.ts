import axios from 'axios'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// Portfolio data interface
export interface Portfolio {
  id: string
  name: string
  total_value: number
  holdings_count: number
  total_gain_loss_percent: number
  positions: Record<string, Position>
  sectors: Record<string, number>
  top_performers: Performer[]
  last_updated: string
  real_data: boolean
}

export interface Position {
  quantity: number
  current_price: number
  position_value: number
  change_percent: number
  company_name: string
  sector: string
}

export interface Performer {
  ticker: string
  change_percent: number
  position_value: number
}

// Market data interfaces
export interface MarketOverview {
  indices: Record<string, IndexData>
  sectors: Record<string, SectorData>
  trending_stocks: Record<string, StockQuote>
  last_updated: string
}

export interface IndexData {
  price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
}

export interface SectorData {
  change_percent: number
  price: number
}

export interface StockQuote {
  symbol: string
  price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
}

// Company data interface
export interface CompanyData {
  basic_info: {
    ticker: string
    company_name: string
    sector: string
    industry: string
    business_summary: string
    employees: number
    website: string
    cik: string
  }
  market_data: {
    current_price: number
    change: number
    change_percent: number
    market_cap: number
    volume: number
    day_high: number
    day_low: number
    fifty_two_week_high: number
    fifty_two_week_low: number
    beta: number
  }
  valuation_metrics: {
    pe_ratio: number
    forward_pe: number
    price_to_book: number
    dividend_yield: number
    eps: number
    target_price: number
    recommendation: string
  }
  financial_metrics: {
    revenue_yf: number
    gross_profit: number
    net_income_yf: number
    total_cash: number
    total_debt: number
    return_on_equity: number
    return_on_assets: number
    operating_margin: number
    profit_margin: number
    revenue_sec: number
    net_income_sec: number
    total_assets_sec: number
    stockholders_equity_sec: number
  }
  data_sources: {
    yahoo_finance: boolean
    sec_edgar: boolean
    last_updated: string
  }
}

// API service functions
export class LiveDataService {
  // Get portfolio data
  static async getPortfolios(): Promise<Portfolio[]> {
    try {
      const response = await api.get('/v1/portfolio/')
      return response.data.portfolios || []
    } catch (error) {
      console.error('Error fetching portfolios:', error)
      throw error
    }
  }

  // Get market overview
  static async getMarketOverview(): Promise<MarketOverview> {
    try {
      const response = await api.get('/v1/market/overview')
      return response.data.market_overview
    } catch (error) {
      console.error('Error fetching market overview:', error)
      throw error
    }
  }

  // Get individual stock data
  static async getStockData(ticker: string): Promise<CompanyData> {
    try {
      const response = await api.get(`/v1/stock/${ticker}`)
      return response.data.stock_data
    } catch (error) {
      console.error(`Error fetching stock data for ${ticker}:`, error)
      throw error
    }
  }

  // Get system status
  static async getSystemStatus(): Promise<any> {
    try {
      const response = await api.get('/status')
      return response.data
    } catch (error) {
      console.error('Error fetching system status:', error)
      throw error
    }
  }

  // Format currency
  static formatCurrency(value: number): string {
    if (value >= 1e12) {
      return `$${(value / 1e12).toFixed(2)}T`
    } else if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(2)}B`
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(2)}M`
    } else if (value >= 1e3) {
      return `$${(value / 1e3).toFixed(2)}K`
    } else {
      return `$${value.toFixed(2)}`
    }
  }

  // Format percentage
  static formatPercentage(value: number): string {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  // Get color for percentage change
  static getChangeColor(value: number): string {
    if (value > 0) return '#4caf50' // green
    if (value < 0) return '#f44336' // red
    return '#757575' // gray
  }
}

export default LiveDataService