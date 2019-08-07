import React from 'react';
import './SearchList.css';
import ListItem from "./ListItem";
import axios from 'axios';

class SearchList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            posts: [],
            total_posts: 0,
            query: '',
        };
        this.limit = 10;
        this.offset = 0;
        this.changeQuery = this.changeQuery.bind(this)
        this.loadPosts = this.loadPosts.bind(this)
    }

    countPages() {
        let self = this;
        return Math.ceil(self.state.total_posts / 10)
    }

    loadPosts(event) {
        event.preventDefault()
        const self = this
        axios.get(`/api/search?limit=${self.limit}&offset=${self.offset}&query=${self.state.query}`)
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

    changeQuery(event) {
        this.setState({query: event.target.value});
    }

    render () {
        console.log(this.state)
        let toRender = [];
        for (let post of this.state.posts) {
            toRender.push(<ListItem post={post} key={post.id}/>)
        }

        let pages = this.pageRange(this.countPages());
        return (
            <div className="SearchList">
                <form onSubmit={this.loadPosts}>
                    <label>
                        Search: <input type="text" name="name" value={this.state.query} onChange={this.changeQuery}/>
                    </label>
                    <br/><br/>
                    <input type="submit" value="Submit"/>
                </form>

                {toRender}
                <div>
                    <h5>Pages:</h5>
                    {pages}
                </div>
            </div>
          );
    }
}

export default SearchList;
