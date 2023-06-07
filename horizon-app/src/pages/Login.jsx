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
        </View>
      );
    }
  };

  const [state, setState] = useState(initialState);

  useEffect(() => {
    async function checkUser() {
      await Auth.currentAuthenticatedUser({
        bypassCache: false
      })
        .then((user) => {
          setState({
            ...initialState,
            user: user,
            isLoggedIn: true,
            loading: false
          });
          console.log(user);
        })
        .catch((err) => {
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

  const sendUserToCustomerIO = async (user) => {
    if (window._cio) {
      window._cio.identify({
        // Required attributes
        id: user.attributes.email,
        email: user.attributes.email,
        name: user.attributes.name,

        // Strongly recommended attributes
        // Timestamp when the user first signed up. You'll want to send it as seconds since the epoch.
        created_at: Math.floor(Date.now() / 1000)
      });
    }
  };

  const handleSignUp = async (user) => {
    // Call the function to send user information to Customer.io
    sendUserToCustomerIO(user);

    // Continue with the sign-up process
    try {
      await Auth.signUp({
        username: user.username,
        password: user.password,
        attributes: {
          email: user.attributes.email,
          name: user.attributes.name
        }
      });
      console.log('Sign-up successful');
    } catch (error) {
      console.log('Sign-up error:', error);
    }
  };

  if (state.loading) {
    return (
      <div>
        <p>Loading...</p>
      </div>
    );
  }

  if (state.isLoggedIn) {
    return <Navigate to="/" />;
  }

  console.log("login page");
  return (
    <div>
      <Box sx={{ position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)' }}>
        <Authenticator components={components} onSignUp={handleSignUp}>
          {() => {
            return <Navigate to="/" />;
          }}
        </Authenticator>
      </Box>
    </div>
  );
}

export default Login;
