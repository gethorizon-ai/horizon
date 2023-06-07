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
      try {
        const user = await Auth.currentAuthenticatedUser({ bypassCache: false });
        setState({
          ...initialState,
          user: user,
          isLoggedIn: true,
          loading: false
        });
        console.log(user);

        // Send user information to Customer.io
        const { name, email } = user.attributes;
        const timestamp = new Date().toISOString();

        // Replace the placeholders below with your actual code to send data to Customer.io
        sendToCustomerIO(name, email, timestamp);
      } catch (error) {
        console.log(error);
        setState({
          ...initialState,
          user: undefined,
          isLoggedIn: false,
          loading: false
        });
      }
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
        <Authenticator components={components}>
          {() => {
            return <Navigate to="/" />
          }}
        </Authenticator>
      </Box>
    </div>
  );
}

export default Login;

function sendToCustomerIO(name, email, timestamp) {
    const customerId = '27552a43b73237d21dff'; // Replace with your actual Customer.io customer ID
    const apiKey = '48939982fc5e84e352f0'; // Replace with your actual Customer.io API key
  
    const data = {
      id: email,
      created_at: Math.floor(new Date(timestamp).getTime() / 1000),
      name: name,
    };
  
    const authHeader = `Basic ${Buffer.from(apiKey + ':').toString('base64')}`;
  
    fetch(`https://track.customer.io/api/v1/customers/${customerId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: authHeader
      },
      body: JSON.stringify(data)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to send data to Customer.io');
        }
        console.log('Data sent to Customer.io successfully');
      })
      .catch(error => {
        console.error('Error sending data to Customer.io:', error);
      });
  }
  

