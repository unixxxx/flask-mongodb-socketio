from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from db import Entities, Entity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('save_entity')
def save_entity(data):
    try:
        entity = Entity(data=data)
        if entity.is_valid:  # check if data is valid
            Entities.insert_one(entity)
        else:
            print(entity.errors)  # all errors during initialization are stored in Entity.errors list
        emit('entity', entity.to_json(), broadcast=True)

    except Exception as ex:
        print(str(ex))


@socketio.on('entities')
def get_entities():
    try:
        result = [r.to_json() for r in Entities.get_last_20_minutes()]
        emit('entities', result)
    except Exception as ex:
        print(str(ex))


if __name__ == '__main__':
    socketio.run(app)