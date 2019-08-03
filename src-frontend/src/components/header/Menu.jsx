import React from 'react';
import './Menu.css';
import {Link} from "react-router-dom";

function Menu(props) {
    const loggedIn = !!props.user
    return (
        <div className="Menu">
            <div className="MenuInner">
                <span className="Menu-item"><Link to="/">Home</Link></span>
                {loggedIn ? <span className="Menu-item"><Link to="/posts/new">Write</Link></span> : null}
                {loggedIn ? null : <span className="Menu-item"><Link to="/login">Log in</Link></span>}
                {loggedIn ? null : <span className="Menu-item"><Link to="/signup">Sign up</Link></span>}
            </div>
        </div>
    );
}

export default Menu;