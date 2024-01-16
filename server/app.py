#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        #response needs to include id and the username
        #return make_response(resdict, 200);
        #print("INSIDE LOGIN:");
        #print(request.json);
        mun = None;
        if (len(request.form) < 1):
            mun = request.json["username"];
        else: mun = request.form.get("username");
        #print(f"mun = {mun}");
        musr = None;
        if (mun == None or len(mun) < 1):
            return make_response("Username must not be empty!", 422);
        else:
            musr = User.query.filter(User.username == mun).first();
            #print("created a new user object successfully! Attempting to add it to the DB now!");
            #db.session.add(musr);#not adding new usernames
            #db.session.commit();#not adding new usernames
            #print(f"musr = {musr}");
            session["username"] = "" + mun;
            session["user_id"] = musr.id;
            return make_response(musr.to_dict(), 200);

class GetSessionUserId:
    def getUserSessionId(self, msess):
        if (msess == None): raise ValueError("no session found!");
        else:
            #print(msess.keys());
            #print(msess.values());
            if (len(msess.keys()) < 1 or "user_id" not in msess.keys()): return None;
            else: return msess["user_id"];

gsuid = GetSessionUserId();

class Logout(Resource):
    def delete(self):
        #print("INSIDE LOGOUT:");
        msid = gsuid.getUserSessionId(session);
        #print(f"msid = {msid}");
        if (msid == None): return make_response({}, 401);
        usr = User.query.filter_by(id=msid).first();
        #print(f"usr = {usr}");
        db.session.delete(usr);
        db.session.commit();
        session["username"] = None;
        session["user_id"] = None;
        return make_response("", 204);

class CheckSession(Resource):
    def get(self):
        #print("INSIDE CHECK SESSION:");
        msid = gsuid.getUserSessionId(session);
        #print(f"msid = {msid}");
        if (msid == None): return make_response({}, 401);
        else:
            usr = User.query.filter_by(id=msid).first();
            #print(f"usr = {usr}");
            return make_response(usr.to_dict(), 200);


api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, "/login");
api.add_resource(Logout, "/logout");
api.add_resource(CheckSession, "/check_session");

if __name__ == '__main__':
    app.run(port=5555, debug=True)
