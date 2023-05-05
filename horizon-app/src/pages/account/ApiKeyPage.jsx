import { Box, Container, Typography } from "@mui/material";
import HorizonAppBar from "../../components/HorizonAppBar";
import AccountDrawer from "../../components/AccountDrawer";
import { DefaultCopyField } from '@eisberg-labs/mui-copy-field';
import { useEffect, useState } from "react";
import { Auth } from "aws-amplify";
import { Navigate } from "react-router-dom";

const drawerWidth = 240;

const initialState = {
    user: undefined,
    isLoggedIn: false,
    loading: true
};

function ApiKeyPage() {
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
                        Horizon API Key
                    </Typography>
                    <Typography variant="body1">
                        Welcome! You have successfully created an account and logged in. Please proceed with creating a Horizon API key using the command line interface as described in the <a href="https://docs.gethorizon.ai/quickstart">documentation</a>. You can then create and deploy projects and tasks!
                    </Typography>
                </Container>
            </Box>
        </Box>
    );
}

export default ApiKeyPage
