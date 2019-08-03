import React from 'react';
import './App.css';
import './components/header/Header'
import Header from "./components/header/Header";
import Main from "./components/main/Main";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: null,
            jwt: null
        }
        this.setUser = this.setUser.bind(this)
    }

    setUser(user, jwt) {
        user.jwt = jwt;
        this.setState({user: user, jwt: jwt});
    }

    render () {
          return (
              <Router>
                  <div className="App">
                      <header className="App-header">
                          <Header user={this.state.user}/>
                      </header>
                      <main className="App-main"><Main user={this.state.user} setUser={this.setUser}/></main>
                  </div>
              </Router>

          );
    }

}

export default App;
