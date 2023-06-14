import { Box, Container, Typography, Link, List, ListItem } from "@mui/material";
import HorizonAppBar from "../../components/HorizonAppBar";
import { useEffect, useState } from "react";
import { Auth } from "aws-amplify";
import { Navigate } from "react-router-dom";

const initialState = {
  user: undefined,
  isLoggedIn: false,
  loading: true,
};

const items = [
  {
    title: "Quickstart Tutorial",
    href: "https://docs.gethorizon.ai/quickstart",
    description: "Learn how to use Horizon by building an LLM function.",
  },
  {
    title: "Installation",
    href: "https://docs.gethorizon.ai/reference/command-line-interface",
    description: "Learn how to install Horizon and use it in production.",
  },
  {
    title: "Examples",
    href: "https://docs.gethorizon.ai/reference/example-use-cases",
    description: "Explore common tasks and use cases solved by Horizon.",
  },
];

function WelcomePage() {
  const [state, setState] = useState(initialState);
  useEffect(() => {
    async function checkUser() {
      try {
        const user = await Auth.currentAuthenticatedUser({
          bypassCache: false,
        });
        setState({
          ...initialState,
          user: user,
          isLoggedIn: true,
          loading: false,
        });
        console.log(user);
      } catch (err) {
        console.log(err);
        setState({
          ...initialState,
          user: undefined,
          isLoggedIn: false,
          loading: false,
        });
      }
    }
    checkUser();
  }, []);

  const signOut = async () => {
    try {
      await Auth.signOut({ global: true });
      setState({ ...initialState, loading: false });
    } catch (error) {
      console.log('error signing out: ', error);
    }
  };

  if (state.loading) {
    return (
      <div className="main-box">
        <HorizonAppBar />
        <p>Loading...</p>
      </div>
    );
  }

  if (!state.isLoggedIn) {
    return <Navigate to="/login" />;
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', flexDirection: 'column', mb: 10 }}>
      <HorizonAppBar user={state.user} signOut={signOut} />
      <Box component="main" sx={{ flexGrow: 1, mt: 3, mb: 5 }}>
        <Container maxWidth="xl">
        <Box sx={{ height: '30px' }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 5 }}>
            <Box sx={{ maxWidth: '60%', textAlign: 'center', px: { xs: 2, sm: 3, md: 10, mb: 20 } }}>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                Welcome to Horizon AI
              </Typography>
              <Box sx={{ height: '20px' }} />
              <Typography variant="body1">
                Horizon provides production-grade LLM deployments with its high-level abstraction to simplify your deployment process while improving quality, cost, and latency.
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Box
              sx={{
                background: 'linear-gradient(180deg, #DB4E66 0%, #A24688 39.57%, #4E3ABA 100%)',
                p: 4,
                borderRadius: '8px',
                minHeight: 300,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: 4,
                '&:hover': {
                  backgroundColor: '#E5E7EB',

                },
                '&:active': {
                  backgroundColor: '#CBD5E0',
                },
              }}
            >
              <Typography variant="h6" sx={{ color: '#fff' }}>
                Start with Horizon
              </Typography>
              <Typography variant="body2" sx={{ color: '#fff' }}>
                Quickly ramp up to use Horizon
              </Typography>
            </Box>
            <List sx={{
              color: '#1d44b8',
              fontFamily: 'Open Sans, sans-serif',
              fontSize: '1.5rem',
              fontWeight: 1000,
              lineHeight: 1,
              alignItems: 'center',
              textDecoration: 'none',
              borderRadius: '8px',
            }}>
              {items.map((item, index) => (
                <Box
                  key={index}
                  component="div"
                  sx={{
                    '&:hover': {
                      backgroundColor: '#E5E7EB',
                      cursor: 'pointer',
                      borderRadius: '8px',
                    },
                    '&:active': {
                      backgroundColor: '#CBD5E0',
                    },
                  }}
                >
                  <ListItem>
                    <Link href={item.href} target="_blank" underline="none" sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                      <Box
                        sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'flex-start',
                          padding: '16px',
                        }}
                      >
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {item.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'rgba(0, 0, 0, 0.54)' }}>
                          {item.description}
                        </Typography>
                      </Box>
                    </Link>
                  </ListItem>
                </Box>
              ))}
            </List>
          </Box>
        </Container>
      </Box>
      <Box component="footer" sx={{ backgroundColor: 'rgba(236, 239, 241, 0.15)', color: 'rgba(15,23,42,0.75)', borderRadius: 1, py: 2, px: 2, mt: 'auto', textAlign: 'center' }}>
        <Typography variant="body1">Need help? Contact Us:</Typography>
        <Link href="mailto:team@gethorizon.ai" underline="hover" sx={{ color: 'rgba(15,23,42,0.75)' }}>team@gethorizon.ai</Link>
      </Box>
    </Box>
  );
}

export default WelcomePage;