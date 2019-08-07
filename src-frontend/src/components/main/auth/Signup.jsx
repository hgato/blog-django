import React from 'react';
import './Signup.css';
import axios from 'axios';
import {Redirect} from "react-router";

class Signup extends React.Component {
    constructor(props) {
        super(props);
        this.signup = this.signup.bind(this)
        this.changeLastName = this.changeLastName.bind(this)
        this.changeFirstName = this.changeFirstName.bind(this)
        this.changePassword = this.changePassword.bind(this)
        this.changeEmail = this.changeEmail.bind(this)
        this.state = {
            email: '',
            password: '',
            first_name: '',
            last_name: '',
            redirect: false,
        }
    }

    signup (event) {
        const self = this
        event.preventDefault()
        axios.put('api/user/', this.state).
        then(function (response) {
            if (response.status === 201) {
                self.setRedirect()
            }
          }).catch((error) => {alert(error.response.data.message)})
    }

    changeEmail (event) {
        this.setState({email: event.target.value});
    }

    changePassword (event) {
        this.setState({password: event.target.value});
    }

    changeFirstName (event) {
        this.setState({first_name: event.target.value});
    }

    changeLastName (event) {
        this.setState({last_name: event.target.value});
    }

    setRedirect = () => {
        this.setState({
            redirect: true
        })
    }

    renderRedirect = () => {
        if (this.state.redirect) {
            return <Redirect to='/login'/>
        }
    }

    render () {
        return (
            <div className="Signup">
                {this.renderRedirect()}
                <h3>Sign up</h3>

                  <form onSubmit={this.signup}>
                      <label>
                          Email: <input type="text" name="email" value={this.state.email} onChange={this.changeEmail} />
                      </label>
                      <br/><br/>
                      <label>
                          Password: <input type="text" name="password" value={this.state.password} onChange={this.changePassword} />
                      </label>
                      <br/><br/>
                      <label>
                          First name: <input type="text" name="first_name" value={this.state.first_name} onChange={this.changeFirstName} />
                      </label>
                      <br/><br/>
                      <label>
                          Last name: <input type="text" name="last_name" value={this.state.last_name} onChange={this.changeLastName} />
                      </label>
                      <br/><br/>
                      <input type="submit" value="Submit" />
                  </form>
            </div>
          );
    }
}

export default Signup;
