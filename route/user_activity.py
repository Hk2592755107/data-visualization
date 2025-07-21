from flask import Blueprint, render_template
import json
import os

user_activity_bp = Blueprint('user_activity_bp', __name__)

def duration_human(ms):
    try:
        ms = int(ms)
    except Exception:
        return "-"
    seconds = ms // 1000
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 2:
        return "1 min ago"
    if minutes < 60:
        return f"{minutes} mins ago"
    hours = minutes // 60
    if hours < 2:
        return "about 1 hour ago"
    if hours < 24:
        return f"{hours} hours ago"
    days = hours // 24
    if days < 2:
        return "about 1 day ago"
    return f"{days} days ago"


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
                        # Attach friendly duration if available
                        details = event.get('details', {})
                        duration = (details.get('duration_ms') or 
                                    details.get('duration_seconds') or 
                                    details.get('duration'))
                        if duration is not None:
                            # Convert seconds to ms if needed
                            if 'duration_seconds' in details:
                                duration = int(float(details['duration_seconds']) * 1000)
                            details['duration_human'] = duration_human(duration)
                        event['details'] = details
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

