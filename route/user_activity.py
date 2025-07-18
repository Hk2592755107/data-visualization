from flask import Blueprint, render_template
import json
import os

user_activity_bp = Blueprint('user_activity_bp', __name__)

@user_activity_bp.route('/user_activity')
def user_activity_landing():
    # List all sessions
    log_path = "user_activity_log.jsonl"
    session_ids = set()
    if os.path.exists(log_path):
        with open(log_path) as f:
            for line in f:
                try:
                    event = json.loads(line)
                    session = event.get("session")
                    if session:
                        session_ids.add(session)
                except Exception:
                    continue
    return render_template("user_activity_landing.html", session_ids=sorted(session_ids))

@user_activity_bp.route('/user_activity/<session_id>')
def user_activity_detail(session_id):
    log_path = "user_activity_log.jsonl"
    events = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("session") == session_id:
                        events.append(event)
                except Exception:
                    continue
    events.sort(key=lambda x: x.get('timestamp', ''))
    return render_template("user_activity.html", session_id=session_id, activity=events)

@user_activity_bp.route('/delete_session/<session_id>', methods=['POST'])
def delete_session(session_id):
    log_path = "user_activity_log.jsonl"
    if not os.path.exists(log_path):
        return '', 204

    new_lines = []
    with open(log_path) as f:
        for line in f:
            try:
                event = json.loads(line)
                if event.get("session") != session_id:
                    new_lines.append(line)
            except Exception:
                continue

    with open(log_path, 'w') as f:
        f.writelines(new_lines)
    return '', 204

