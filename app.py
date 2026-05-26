import json
import math
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

DEFAULT_DATA = {
    "subjects": [
        {"id": "s1", "name": "Mathematics",  "attended": 0, "total": 0},
        {"id": "s2", "name": "Physics",       "attended": 0, "total": 0},
        {"id": "s3", "name": "Chemistry",     "attended": 0, "total": 0},
        {"id": "s4", "name": "English",       "attended": 0, "total": 0},
        {"id": "s5", "name": "CS",            "attended": 0, "total": 0},
        {"id": "s6", "name": "PE",            "attended": 0, "total": 0},
    ]
}

# ── Calculation functions ──────────────────────────────────────────────────────

def classes_can_skip(total, attended):
    """Max classes skippable before dropping below 85%."""
    if total == 0 or (attended / total) * 100 < 85:
        return 0
    return int((attended - 0.85 * total) / 0.85)

def classes_to_attend(total, attended):
    """Consecutive classes needed to climb back to 85%."""
    if total == 0 or (attended / total) * 100 >= 85:
        return 0
    return math.ceil((0.85 * total - attended) / 0.15)

def risk_level(percentage):
    if percentage >= 85: return 'Safe'
    if percentage >= 75: return 'Warning'
    return 'Critical'

def insight(total, attended):
    if total == 0:
        return 'No classes recorded yet'
    pct  = (attended / total) * 100
    skip = classes_can_skip(total, attended)
    need = classes_to_attend(total, attended)
    if pct >= 85:
        if skip == 0:
            return 'Attend a few more to build a skip buffer'
        return f'You can skip {skip} more class{"es" if skip != 1 else ""}'
    return f'Attend {need} consecutive class{"es" if need != 1 else ""} to reach 85%'

def enrich(subject):
    """Add computed fields to a subject dict."""
    t = subject['total']
    a = subject['attended']
    pct = round((a / t) * 100, 1) if t > 0 else 0
    return {
        **subject,
        'percentage':       pct,
        'risk_level':       risk_level(pct) if t > 0 else 'Safe',
        'classes_can_skip': classes_can_skip(t, a),
        'classes_to_attend':classes_to_attend(t, a),
        'insight':          insight(t, a),
    }

# ── Data helpers ───────────────────────────────────────────────────────────────

def load():
    if not os.path.exists(DATA_FILE):
        save(DEFAULT_DATA)
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    data = load()
    subjects = [enrich(s) for s in data['subjects']]
    safe     = sum(1 for s in subjects if s['risk_level'] == 'Safe')
    warning  = sum(1 for s in subjects if s['risk_level'] == 'Warning')
    critical = sum(1 for s in subjects if s['risk_level'] == 'Critical')
    return jsonify({
        'subjects': subjects,
        'summary': {
            'total':    len(subjects),
            'safe':     safe,
            'warning':  warning,
            'critical': critical,
            'safe_pct': round(safe / len(subjects) * 100) if subjects else 0,
        }
    })

@app.route('/api/mark', methods=['POST'])
def mark():
    body    = request.get_json()
    sid     = body.get('subject_id')
    status  = body.get('status')          # 'present' | 'absent'
    data    = load()
    for s in data['subjects']:
        if s['id'] == sid:
            s['total'] += 1
            if status == 'present':
                s['attended'] += 1
            break
    save(data)
    return jsonify({'ok': True})

@app.route('/api/rename', methods=['POST'])
def rename():
    body = request.get_json()
    sid  = body.get('subject_id')
    name = body.get('name', '').strip()
    if not name:
        return jsonify({'ok': False, 'error': 'Name cannot be empty'}), 400
    data = load()
    for s in data['subjects']:
        if s['id'] == sid:
            s['name'] = name
            break
    save(data)
    return jsonify({'ok': True})

@app.route('/api/reset', methods=['POST'])
def reset():
    body = request.get_json()
    sid  = body.get('subject_id')
    data = load()
    for s in data['subjects']:
        if s['id'] == sid:
            s['attended'] = 0
            s['total']    = 0
            break
    save(data)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
