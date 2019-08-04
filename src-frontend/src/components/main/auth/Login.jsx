import React from 'react';
import './Login.css';
import axios from 'axios';
import { Redirect } from 'react-router-dom';

class Login extends React.Component {
    constructor(props) {
        super(props);
        this.login = this.login.bind(this)
        this.changePassword = this.changePassword.bind(this)
        this.changeEmail = this.changeEmail.bind(this)
        this.state = {
            email: '',
            password: '',
            redirect: false,
        }
    }

    login(event) {
        event.preventDefault()
        const self = this
        axios.post('api/user/', this.state).then(function (response) {
            if (response.status === 200) {
                self.props.setUser(response.data.user, response.data.jwt)
                self.setRedirect()
            }
        })
    }

    changeEmail(event) {
        this.setState({email: event.target.value});
    }

    changePassword(event) {
        this.setState({password: event.target.value});
    }

    setRedirect = () => {
        this.setState({
            redirect: true
        })
    }

    renderRedirect = () => {
        if (this.state.redirect) {
            return <Redirect to='/'/>
        }
    }

    render() {
        return (
            <div className="Login">
                {this.renderRedirect()}
                <h3>Log in</h3>
                <form onSubmit={this.login}>
                    <label>
                        Email: <input type="text" name="email" value={this.state.email} onChange={this.changeEmail}/>
                    </label>
                    <br/><br/>
                    <label>
                        Password: <input type="text" name="password" value={this.state.password}
                                         onChange={this.changePassword}/>
                    </label>
                    <br/><br/>
                    <input type="submit" value="Submit"/>
                </form>
            </div>
        );
    }
}

export default Login;
