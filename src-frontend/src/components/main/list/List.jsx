import React from 'react';
import './List.css';
import ListItem from "./ListItem";
import axios from 'axios';

class List extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            posts: [],
            total_posts: 0,
        };
        this.limit = 10;
        this.offset = 0;
        this.loadPosts()
    }

    countPages() {
        let self = this;
        return Math.ceil(self.state.total_posts / 10)
    }

    loadPosts() {
        const self = this
        const author = self.props.author ? `&author=${self.props.author }` : '';
        axios.get(`/api/posts/list?limit=${self.limit}&offset=${self.offset}${author}`)
          .then(function (response) {
            self.setState({
                posts: response.data.posts,
                total_posts: response.data.total_posts
            })
          }).catch((error) => {alert(error.response.data.message)})
    }

    pageRange(size) {
        return [...Array(size).keys()].map(i =>
            <span onClick={this.goToPage.bind(this, i)}> {Number(1 + i)} </span>);
    }

    goToPage(page) {
        this.offset = page * 10;
        this.loadPosts();
    }

    render () {
        let toRender = [];
        for (let post of this.state.posts) {
            toRender.push(<ListItem post={post} key={post.id}/>)
        }

        let pages = this.pageRange(this.countPages());
        return (
            <div className="List">
                {toRender}
                <div>
                    <h5>Pages:</h5>
                    {pages}
                </div>
            </div>
          );
    }
}

export default List;
