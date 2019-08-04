import React from 'react';
import './Main.css';
import List from "./list/List";
import Signup from "./auth/Signup";
import Login from "./auth/Login";
import { Route } from "react-router-dom";
import Post from "./post/Post";
import EditPost from "./post/EditPost";
import NewPost from "./post/NewPost";
import SearchList from "./list/SearchList";

class Main extends React.Component {
    render () {
        return (
            <div className="Main">
                <Route exact path="/" render={(props) => <List {...props} />}/>
                <Route exact path="/search" render={(props) => <SearchList {...props} />}/>
                <Route exact path="/posts/my" render={(props) => <List author={this.props.user.id} {...props} />}/>
                <Route exact path="/signup" render={(props) => <Signup {...props} />}/>
                <Route exact path="/login" render={(props) => <Login {...props} user={this.props.user} setUser={this.props.setUser}/>}/>
                <Route exact path="/posts/:id(\d+)" render={(props) => <Post {...props} user={this.props.user} />}/>
                <Route exact path="/posts/:id(\d+)/edit" render={(props) => <EditPost {...props} user={this.props.user} />}/>
                <Route exact path="/posts/new" render={(props) => <NewPost {...props} user={this.props.user} />}/>
            </div>
          );
    }
}

export default Main;
