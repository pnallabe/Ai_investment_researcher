# AI Investment Research Bot - Frontend

A modern React TypeScript frontend for the AI Investment Research Bot, providing an intuitive interface for financial analysis, portfolio management, and AI-powered research capabilities.

## 🚀 Features

### Core Functionality
- **Authentication System**: Secure login/logout with JWT tokens
- **AI Research Chat**: Interactive chat interface for investment queries
- **Portfolio Management**: Track investments and performance metrics
- **Company Analysis**: Research and analyze public companies
- **Analytics Dashboard**: Advanced portfolio analytics and risk metrics
- **Real-time Updates**: Live market data and notifications

### Technical Features
- **Modern React 18**: Latest React with TypeScript support
- **Material-UI (MUI)**: Professional design system
- **React Router v6**: Client-side routing and navigation
- **React Query**: Efficient data fetching and caching
- **Vite**: Fast development server and build tool
- **Responsive Design**: Mobile-first responsive layout
- **Dark/Light Theme**: Configurable theming system

## 🛠️ Tech Stack

### Core Framework
- **React 18.2.0** - UI library
- **TypeScript 5.2.2** - Type safety
- **Vite 5.4.21** - Build tool and dev server

### UI Components & Styling
- **Material-UI 5.15.10** - Component library
- **@mui/icons-material** - Icon set
- **@emotion/react & @emotion/styled** - CSS-in-JS

### State Management & Data Fetching
- **@tanstack/react-query 4.36.1** - Server state management
- **React Router DOM 6.21.3** - Client-side routing
- **Axios 1.6.7** - HTTP client

### Authentication & Security
- **jwt-decode 4.0.0** - JWT token handling
- **Notistack 3.0.1** - Notification system

### Development & Testing
- **ESLint** - Code linting
- **@types/react & @types/react-dom** - TypeScript definitions
- **Vite plugins** - Development utilities

## 📁 Project Structure

```
frontend/
├── public/
│   ├── favicon.svg
│   └── index.html
├── src/
│   ├── components/
│   │   └── Layout/
│   │       └── Layout.tsx
│   ├── pages/
│   │   ├── Login/
│   │   │   └── Login.tsx
│   │   ├── Dashboard/
│   │   │   └── Dashboard.tsx
│   │   ├── Research/
│   │   │   └── Research.tsx
│   │   ├── Portfolio/
│   │   │   └── Portfolio.tsx
│   │   ├── Companies/
│   │   │   └── Companies.tsx
│   │   ├── Analytics/
│   │   │   └── Analytics.tsx
│   │   └── Profile/
│   │       └── Profile.tsx
│   ├── services/
│   │   └── authService.ts
│   ├── hooks/
│   │   └── useAuth.tsx
│   ├── utils/
│   ├── types/
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   └── vite-env.d.ts
├── .env.local
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── README.md
```

## 🚦 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

5. **Open in browser**:
   ```
   http://localhost:3000
   ```

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint

# Type checking
npm run type-check   # Run TypeScript compiler check
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WEBSOCKET_URL=ws://localhost:8000

# Application Configuration
VITE_APP_NAME=AI Investment Research Bot
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development

# Debug Settings
VITE_DEBUG=true

# External Services (Optional)
VITE_SENTRY_DSN=your_sentry_dsn_here
VITE_GOOGLE_ANALYTICS_ID=your_ga_id_here
```

### Vite Configuration

The `vite.config.ts` includes:
- **Proxy setup** for API calls to backend
- **Path aliases** for cleaner imports
- **Build optimization** with code splitting
- **Development server** configuration

### TypeScript Configuration

- **Strict mode** enabled for type safety
- **Path mapping** for organized imports
- **Modern ES2020** target
- **JSX support** with React 18

## 🎨 UI Components & Design

### Material-UI Theme
- **Primary**: Blue (#1976d2)
- **Secondary**: Pink (#dc004e)
- **Custom styling** with rounded corners and shadows
- **Responsive breakpoints** for mobile-first design

### Key Components
- **Layout**: Main application layout with sidebar navigation
- **Login**: Authentication form with validation
- **Dashboard**: Overview with stats cards and charts
- **Research**: AI chat interface for investment queries
- **Portfolio**: Investment tracking and performance
- **Companies**: Company analysis and research
- **Analytics**: Advanced portfolio metrics
- **Profile**: User account management

### Responsive Design
- **Mobile-first** approach
- **Breakpoints**: xs, sm, md, lg, xl
- **Collapsible navigation** on mobile
- **Touch-friendly** interface elements

## 🔐 Authentication

### JWT Token Management
- **Automatic token refresh** before expiration
- **Secure storage** in localStorage
- **Route protection** with PrivateRoute component
- **Axios interceptors** for API authentication

### Auth Flow
1. User logs in with email/password
2. Backend returns JWT access token
3. Token stored and added to API requests
4. Automatic refresh before expiration
5. Logout clears all stored data

## 📡 API Integration

### Services Architecture
- **authService**: Authentication and user management
- **React Query**: Efficient data fetching and caching
- **Axios interceptors**: Request/response handling
- **Error handling**: Comprehensive error management

### API Endpoints
```typescript
// Authentication
POST /v1/auth/login
POST /v1/auth/register
POST /v1/auth/refresh
GET  /v1/auth/me

// Research (Future)
POST /v1/research/query
GET  /v1/research/history

// Portfolio (Future)
GET  /v1/portfolio/
POST /v1/portfolio/positions
```

## 🧪 Development

### Code Organization
- **Feature-based** folder structure
- **Separation of concerns** (components, services, hooks)
- **TypeScript interfaces** for type safety
- **Custom hooks** for reusable logic

### Best Practices
- **Component composition** over inheritance
- **Props interface definitions** for all components
- **Error boundaries** for robust error handling
- **Accessibility** considerations with ARIA labels
- **Performance optimization** with React.memo and useMemo

### Styling Approach
- **Material-UI** system for consistency
- **Custom CSS** for specific styling needs
- **Responsive utilities** for mobile adaptation
- **Theme customization** for brand consistency

## 🚀 Deployment

### Build Process
```bash
npm run build
```

Creates optimized production build in `dist/` directory:
- **Code splitting** for faster loading
- **Asset optimization** (images, CSS, JS)
- **Source maps** for debugging
- **Bundle analysis** for size optimization

### Production Deployment
1. **Build the application**
2. **Configure web server** (nginx, Apache)
3. **Set up environment variables**
4. **Configure reverse proxy** for API calls
5. **Enable HTTPS** for security

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🔍 Monitoring & Analytics

### Error Tracking
- **Error boundaries** for React error handling
- **Sentry integration** (optional) for production monitoring
- **Console logging** for development debugging

### Performance Monitoring
- **React Query DevTools** for data fetching insights
- **Vite bundle analyzer** for build optimization
- **Lighthouse metrics** for performance auditing

## 🧪 Testing (Future Enhancement)

### Testing Strategy
- **Unit tests** with Vitest and React Testing Library
- **Integration tests** for component interactions
- **E2E tests** with Playwright or Cypress
- **API mocking** with MSW

### Test Structure
```
src/
├── __tests__/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── hooks/
└── test/
    ├── setup.ts
    ├── mocks/
    └── utils/
```

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** with proper TypeScript types
4. **Add tests** for new functionality
5. **Submit pull request** with description

### Code Standards
- **ESLint configuration** for code quality
- **Prettier** for code formatting
- **TypeScript strict mode** for type safety
- **Conventional commits** for clear history

## 📄 License

This project is part of the AI Investment Research Bot system. See the main project LICENSE file for details.

## 🆘 Support

### Common Issues

**Development server won't start:**
- Check Node.js version (18+)
- Delete `node_modules` and run `npm install`
- Check port 3000 availability

**API connection issues:**
- Verify backend is running on port 8000
- Check VITE_API_URL in .env.local
- Review network/firewall settings

**Build errors:**
- Run `npm run type-check` for TypeScript issues
- Check for missing dependencies
- Review import paths and aliases

### Getting Help
- **Documentation**: Check inline code comments
- **Issues**: Create GitHub issue with details
- **Development**: Check browser console for errors
- **API**: Verify backend API documentation

---

Built with ❤️ using React, TypeScript, and Material-UI