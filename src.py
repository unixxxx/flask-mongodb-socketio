from flask import Flask, render_template
from flask.ext.pymongo import PyMongo
from flask_socketio import SocketIO, emit
from bson.objectid import ObjectId
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

mongo = PyMongo(app)
socketio = SocketIO(app)


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return obj


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('save_entity')
def save_entity(data):
    try:
        mongo.db.entity.insert_one(data)
        emit('entity', json.dumps(data, cls=Encoder), broadcast=True)
    except:
        pass


@socketio.on('entities')
def get_entities():
    try:
        result = [json.dumps(r, cls=Encoder) for r in mongo.db.entity.find()]
        emit('entities', result)
    except:
        pass


if __name__ == '__main__':
    socketio.run(app)
