import React from 'react';
import './EditPost.css';
import axios from 'axios';
import { Redirect } from 'react-router-dom';

class EditPost extends React.Component {
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
        this.loadPost()
    }

    loadPost() {
        let self = this
        axios.get(`/api/posts/${this.props.match.params.id}`)
          .then(function (response) {
            self.setState({
                name: response.data.post.name,
                text: response.data.post.text,
            })
          })
    }

    submit(event) {
        event.preventDefault()
        const self = this
        const config = {
            headers: {
                'Authorization': this.props.user.jwt
            }
        }
        axios.patch(`/api/posts/${this.props.match.params.id}/`, this.state, config).then(function (response) {
            if (response.status === 200) {
                self.setRedirect()
            }
        })
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
            return <Redirect to={`/posts/${this.props.match.params.id}`}/>
        }
    }

    render() {
        return (
            <div className="EditPost">
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

export default EditPost;
