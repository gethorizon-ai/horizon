import { Box, Container, Typography } from "@mui/material";
import HorizonAppBar from "../../components/HorizonAppBar";
import AccountDrawer from "../../components/AccountDrawer";
import { DefaultCopyField } from '@eisberg-labs/mui-copy-field';
import { useEffect, useState } from "react";
import { Auth } from "aws-amplify";
import { Navigate } from "react-router-dom";
import { Code, ThemeProvider, createTheme } from '@mui/material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const drawerWidth = 240;

const initialState = {
    user: undefined,
    isLoggedIn: false,
    loading: true
};

function WelcomePage() {
    const [state, setState] = useState(initialState);
    useEffect(() => {
        async function checkUser() {
            await Auth.currentAuthenticatedUser({
                bypassCache: false
            }).then(user => {
                setState({
                    ...initialState,
                    user: user,
                    isLoggedIn: true,
                    loading: false
                });
                console.log(user)
            }).catch(err => {
                console.log(err);
                setState({
                    ...initialState,
                    user: undefined,
                    isLoggedIn: false,
                    loading: false
                });
            });
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
    }

    if (state.loading) {
        return (<div className="main-box">
            <HorizonAppBar />
            <p>Loading...</p>
        </div>)
    }
    if (!state.isLoggedIn) {
        return (
            <Navigate to="/login" />
        )
    }
    return (
        <Box>
            <HorizonAppBar user={state.user} signOut={signOut} />
            <Box component="drawer" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
                <AccountDrawer />
            </Box>
            <Box component="main" sx={{ flexGrow: 1, mt: 3, ml: { sm: `${drawerWidth}px` } }}>
                <Container maxWidth="xl">
                    <Typography variant="h4" align="left" sx={{ mb: 3, fontWeight: 700 }} >
                        Welcome!
                    </Typography>
                    <Typography variant="body1">
                        First step - go to your command line to get your API key.<br /><br />

                        Detailed guidance on how to use Horizon is provided <a href="https://docs.gethorizon.ai/quickstart#2-install-the-library-and-generate-your-horizon-api-key">here</a>.<br /><br />
                    </Typography>
                    <SyntaxHighlighter language="bash">
                        {`# Install Horizon library via pip
pip install horizonai

# Get your API key
horizonai user api-key`}
                    </SyntaxHighlighter>
                </Container>
            </Box>
        </Box >
    );
}

export default WelcomePage
