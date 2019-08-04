import React from 'react';
import './ListItem.css';
import {Link} from "react-router-dom";

class ListItem extends React.Component {
    render () {
        return (
            <div className="ListItem">
                <Link className="ListItem-Link" to={"/posts/" + this.props.post.id}>
                    <h3 className="ListItem-header">{this.props.post.name}</h3>
                    <div className="ListItem-text">{
                        this.props.post.text.length > 1000
                            ? this.props.post.text.slice(0, 1000)
                            : this.props.post.text}</div>
                    <div className="ListItem-footer">
                        {this.props.post.author.first_name + ' ' + this.props.post.author.last_name}
                    </div>
                </Link>
            </div>
          );
    }

}

export default ListItem;
