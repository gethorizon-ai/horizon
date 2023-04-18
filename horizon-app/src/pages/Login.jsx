import { Authenticator, useTheme } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import { Link, Navigate } from "react-router-dom";
import React, { useEffect, useState } from 'react';
import { Auth } from 'aws-amplify';
import { Box } from '@mui/material';
import { View, Text } from '@aws-amplify/ui-react';

const initialState = {
    user: undefined,
    isLoggedIn: false,
    loading: true
};

function Login() {
    const components = {
        Footer() {
            const { tokens } = useTheme();

            return (
                <View textAlign="center" padding={tokens.space.large}>
                    <Text color={tokens.colors.neutral[80]}>
                        By using Horizon AI, you agree to our <Link to={'/legal/privacy_policy'}>Privacy Policy</Link> and <Link to={'/legal/terms_and_conditions'}>Terms and Conditions</Link>.
                    </Text>
                </View >
            );
        }
    };

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
    if (state.loading) {
        return (
            <div>
                <p>Loading...</p>
            </div>
        )
    }
    if (state.isLoggedIn) {
        return <Navigate to="/" />
    }
    console.log("login page");
    return (
        <div>
            <Box sx={{ position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)' }}>
                <Authenticator hideSignUp={true} components={components}>
                    {() => {
                        return <Navigate to="/" />
                    }}
                </Authenticator>
            </Box>
        </div>
    );
}

export default Login;
