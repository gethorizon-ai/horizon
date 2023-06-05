import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import { useLocation, useNavigate } from 'react-router-dom';
import TwitterIcon from '@mui/icons-material/Twitter';

function HorizonAppBar({ user = undefined, signOut = undefined }) {
  const navigate = useNavigate();
  const location = useLocation().pathname;

  const goToLoginPage = () => {
    if (location !== "/login") {
      navigate("/login");
    }
  };

  const goToDocumentationPage = () => {
    window.open("http://docs.gethorizon.ai", "_blank")
  };

  const goToOverviewPage = () => {
    if (location !== "/") {
      navigate("/");
    }
  };

  const goToExamplesPage = () => {
    window.open("https://docs.gethorizon.ai/reference/example-use-cases", "_blank");
  };

  const pagesAndHandlers = {
    'Overview': goToOverviewPage,
    'Documentation': goToDocumentationPage,
    'Examples': goToExamplesPage
  };

  const settingsAndHandlers = {
    'Logout': signOut
  };

  return (
    <AppBar position="relative" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#F9FAFB' }}>
      <Container maxWidth="100%" disableGutters sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 2, px:2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography
            variant="h5"
            component="a"
            href="/"
            sx={{
              color: '#1d44b8',
              fontFamily: 'Open Sans, sans-serif',
              fontSize: '1.5rem',
              fontWeight: 1000,
              lineHeight: 1,
              display: 'flex',
              alignItems: 'center',
              textDecoration: 'none',
            }}
          >
            Horizon AI
          </Typography>
          {Object.keys(pagesAndHandlers).map((page) => (
            <Button key={page} onClick={pagesAndHandlers[page]} sx={{ color: '#4B5563', ml: 3, textTransform: "none", fontSize: "1rem", "&:hover": { backgroundColor: "#E5E7EB" } }}>
              {page}
            </Button>
          ))}
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton color="inherit" sx={{ color: '#1F2937' }} onClick={() => window.open('https://twitter.com/HorizonAI_', '_blank')}>
            <TwitterIcon />
          </IconButton>
          <Button
            onClick={settingsAndHandlers['Logout']}
            sx={{
              color: 'rgba(31, 41, 55, 0.5)',
              ml: 2,
              textTransform: 'none',
              fontSize: '1rem',
              '&:hover': {
                backgroundColor: '#E5E7EB',
              },
            }}
          >
            Logout
          </Button>
        </Box>
      </Container>
    </AppBar>
  );
}

export default HorizonAppBar;
