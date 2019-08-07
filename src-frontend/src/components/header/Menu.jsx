import React from 'react';
import './Menu.css';
import {Link, Redirect} from "react-router-dom";
import axios from "axios";

class Menu extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            redirect: false,
        }
        this.logout = this.logout.bind(this)
    }

    logout () {
        const self = this
        const config = {
            headers: {
                'Authorization': this.props.user.jwt
            }
        }
        axios.delete('/api/user/logout', config).then(function (response) {
            if (response.status === 200) {
                self.props.setUser(null, null);
                self.setRedirect()
            }
        }).catch((error) => {alert(error.response.data.message)})
    }

    setRedirect = () => {
        this.setState({
            redirect: true
        })
    }

    renderRedirect = () => {
        if (this.state.redirect) {
            return <Redirect to={'/'}/>
        }
    }

    render() {
        const loggedIn = !!this.props.user;
        return (
            <div className="Menu">
                {this.renderRedirect()}
                <div className="MenuInner">
                    <span className="Menu-item"><Link to="/">Home</Link></span>
                    <span className="Menu-item"><Link to="/search">Search</Link></span>
                    {loggedIn ? <span className="Menu-item"><Link to="/posts/new">Write</Link></span> : null}
                    {loggedIn ? <span className="Menu-item"><Link to="/posts/my">My posts</Link></span> : null}
                    {loggedIn ? <span className="Menu-item" onClick={this.logout}>Log out</span> : null}
                    {loggedIn ? null : <span className="Menu-item"><Link to="/login">Log in</Link></span>}
                    {loggedIn ? null : <span className="Menu-item"><Link to="/signup">Sign up</Link></span>}
                </div>
            </div>
        );
    }

}

export default Menu;