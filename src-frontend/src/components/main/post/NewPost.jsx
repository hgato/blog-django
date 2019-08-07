import React from 'react';
import './NewPost.css';
import axios from 'axios';
import { Redirect } from 'react-router-dom';

class NewPost extends React.Component {
    constructor(props) {
        super(props);
        this.submit = this.submit.bind(this)
        this.changeText = this.changeText.bind(this)
        this.changeName = this.changeName.bind(this)
        this.state = {
            name: '',
            text: '',
            redirect: false,
        }
        this.postId = null
    }

    submit(event) {
        event.preventDefault()
        const self = this
        const config = {
            headers: {
                'Authorization': this.props.user.jwt
            }
        }
        axios.put(`/api/posts/`, this.state, config).then(function (response) {
            if (response.status === 200) {
                self.postId = response.data.post.id;
                self.setRedirect()
            }
        }).catch((error) => {alert(error.response.data.message)})
    }

    changeName(event) {
        this.setState({name: event.target.value});
    }

    changeText(event) {
        this.setState({text: event.target.value});
    }

    setRedirect = () => {
        this.setState({
            redirect: true
        })
    }

    renderRedirect = () => {
        if (this.state.redirect) {
            return <Redirect to={`/posts/${this.postId}`}/>
        }
    }

    render() {
        return (
            <div className="NewPost">
                {this.renderRedirect()}
                <form onSubmit={this.submit}>
                    <label>
                        Name: <input type="text" name="name" value={this.state.name} onChange={this.changeName}/>
                    </label>
                    <br/><br/>
                    <label>
                        <textarea name="text" value={this.state.text}
                                         onChange={this.changeText}/>
                    </label>
                    <br/><br/>
                    <input type="submit" value="Submit"/>
                </form>
            </div>
        );
    }
}

export default NewPost;
