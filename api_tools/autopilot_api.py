from flask_socketio import join_room, leave_room, SocketIO, send, emit, rooms
from flask import Blueprint, current_app, jsonify
from flask_login import current_user
from datetime import datetime, timedelta
from database.models import Game
from database.db import db
from server_utils import load_game_json

autopilot_api = Blueprint("autopilot_api", __name__)
socketio = SocketIO()
# @socketio.on('join')
# def on_join(data):
#     # username = data['username']
#     # room = data['room']
#     # join_room(room)
#     send(username + ' has entered the room.', to=room)

active_rooms = {}

def remove_inactive_rooms():
    """ Utility to remove inactive rooms
    """
    now = datetime.utcnow()
    inactive_rooms = [room_id for room_id, last_activity in active_rooms.items()
                      if now - last_activity > timedelta(minutes=10)]
    for room_id in inactive_rooms:
        del active_rooms[room_id]

def get_active_rooms_display(active_rooms: 'list[str]'):
    print(active_rooms)
    return load_game_json(db.session.query(Game).filter(Game.Game_ID.in_(active_rooms)).all())

@autopilot_api.route('/endzone/ingame/palantir/active', methods = ["GET"])
def getActiveRooms():
    remove_inactive_rooms()
    return jsonify({'active_rooms': get_active_rooms_display(active_rooms)})

@socketio.on('add_play', namespace="/endzone/ingame/palantir")
def send_message_to_room(room, playData):
    print(playData)
    emit('get_play', playData, room=room)

@socketio.on('leave')
def on_leave(room):
    leave_room(room)
    if room in active_rooms:
        del active_rooms[room]

@socketio.on('join', namespace="/endzone/ingame/palantir")
def on_join(room):
    join_room(room)
    active_rooms.setdefault(room, datetime.utcnow())
