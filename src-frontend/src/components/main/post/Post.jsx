import React from 'react';
import './Post.css';
import axios from 'axios';
import {Link} from "react-router-dom";

class Post extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            post: null,
        };
        this.loadPost()
    }

    countPages() {
        let self = this;
        return Math.ceil(self.state.total_posts / 10)
    }

    loadPost() {
        let self = this
        axios.get(`/api/posts/${this.props.match.params.id}`)
          .then(function (response) {
            self.setState({
                post: response.data.post,
            })
          })
    }

    render () {
        if (!this.state.post) {
            return <div/>
        }
        let editLink = null;
        console.log([this.props.user, this.state.post.author.id])
        if (this.props.user && this.props.user.id === this.state.post.author.id) {
            editLink = <Link to={"/posts/" + this.props.match.params.id + "/edit"}>Edit</Link>
        }

        return (
            <div className="Post">
                <h3 className="Post-header">{this.state.post.name}</h3>
                <span className="Post-text">{this.state.post.text}</span>
                <p className="Post-footer">{this.state.post.author.first_name + ' ' + this.state.post.author.last_name}</p>
                <p>{editLink}</p>
            </div>
          );
    }
}

export default Post;
