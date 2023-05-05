import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

import { Amplify } from 'aws-amplify';
import "@aws-amplify/ui-react/styles.css";
import awsExports from "./aws-exports";

// Page imports
import ApiKeyPage from "./pages/account/ApiKeyPage";
import Login from './pages/Login';
import PageNotFound from './pages/PageNotFound';
import PrivacyPolicyPage from './pages/legal/PrivacyPolicyPage';
import TermsAndConditionsPage from './pages/legal/TermsAndConditionsPage';

// Theme imports
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import '@fontsource/open-sans/300.css';
import '@fontsource/open-sans/400.css';
import '@fontsource/open-sans/500.css';
import '@fontsource/open-sans/600.css';

Amplify.configure(awsExports);
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#fafafa',
    },
    secondary: {
      main: '#B6C8FF',
    },
    text: {
      primary: '#222828',
      secondary: '#4d5253',
    },
    background: {
      default: '#fafafa',
      paper: '#fafafa',
    },
  },
  typography: {
    fontFamily: 'Open Sans',
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ThemeProvider theme={theme}>
    <CssBaseline enableColorScheme />
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />

        <Route path="/login" element={<Login />} />

        <Route path="/account" element={<Navigate to="/account/api_key" />} />
        <Route path="/account/api_key" element={<ApiKeyPage />} />

        <Route path="/legal/privacy_policy" element={<PrivacyPolicyPage />} />
        <Route path="/legal/terms_and_conditions" element={<TermsAndConditionsPage />} />

        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </BrowserRouter>
  </ThemeProvider>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
