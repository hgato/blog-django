import React from 'react';
import './Header.css';
import Menu from "./Menu";

function Header(props) {
  return (
    <div className="Header">
        <h1>Different stuff blog</h1>
        <Menu user={props.user}/>
    </div>
  );
}

export default Header;
