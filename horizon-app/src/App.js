import { Navigate } from "react-router-dom";
import React, { Component } from 'react';
import './App.css';

// Amplify Library imports 
import { Auth } from 'aws-amplify';

const initialState = {
  user: undefined,
  isLoggedIn: false,
  loading: true
};

class App extends Component {
  constructor(props) {
    super(props)
    this.state = initialState;
  };

  async componentDidMount(){
    await Auth.currentAuthenticatedUser({
      bypassCache: false  // Optional, By default is false. If set to true, this call will send a request to Cognito to get the latest user data
    }).then(user => {
      this.setState({...this.state,
        user: user,
        isLoggedIn: true,
        loading: false
      });
      console.log(user)
      return user;
    }).catch(err => {
      console.log(err);
      this.setState({...this.state,
        user: undefined,
        isLoggedIn: false,
        loading: false
      });
    });
  };

  signOut = async () => {
    try {
      await Auth.signOut({ global: true });
      this.setState({...initialState, loading: false});
    } catch (error) {
      console.log('error signing out: ', error);
    }
  };

  render() {
    if(this.state.loading) {
      return (
        <div>
          Loading....
        </div>
      )
    }
    if(this.state.isLoggedIn) {
      return (
        <div>
          <Navigate to="/account" />
        </div>
      );
    }
    else {
      console.log(this.state);
      return (
        <Navigate to="/login" />
      )
    }
  }

}

export default App;
