#!/usr/bin/env python3
"""
Clean Quart Todo App example (one-file)
- Uses AsyncNanaSQLite safely (stores only JSON-serializable types)
- Clear helper functions for DB operations
- Datetimes stored as ISO strings (UTC)
- Minimal validation and error handling
"""
import uuid
from datetime import datetime, timezone

from quart import Quart, jsonify, redirect, render_template_string, request, url_for

from nanasqlite import AsyncNanaSQLite

app = Quart(__name__)
DB_PATH = "quart_todo_clean.db"

# Templates
BASE = """
<!doctype html>
<html class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{title}}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            accent: '#60a5fa'
          }
        }
      }
    }
  </script>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
  <div class="container mx-auto p-6 max-w-3xl">{{content|safe}}</div>
</body>
</html>
"""

HOME = """
<div class="bg-gray-800 rounded-lg shadow-lg p-6">
  <h1 class="text-2xl font-bold mb-4 text-white">Todo</h1>
  <form method=post action="/add" class="flex gap-2 mb-4">
    <input name=title required placeholder="What needs to be done?" class="flex-1 p-2 rounded bg-gray-700 border border-gray-600 text-gray-100 placeholder-gray-400">
    <button class="bg-accent hover:bg-blue-500 text-gray-900 px-4 rounded">Add</button>
  </form>
  <div class="mb-4 text-sm text-gray-300">Tasks: <strong class="text-white">{{ total }}</strong> | Completed: <strong class="text-green-400">{{ completed }}</strong></div>
  <ul class="space-y-2">
  {% for t in tasks %}
    <li class="p-3 border rounded flex justify-between items-center border-gray-700 bg-gray-900">
      <div>
        <div class="font-medium {% if t.completed %}text-gray-500 line-through{% else %}text-gray-100{% endif %}">{{ t.title }}</div>
        <div class="text-xs text-gray-400">{{ t.created_at }}</div>
      </div>
      <div class="flex gap-2">
        <form method=post action="/toggle/{{ t.id }}">
          <button class="px-2 py-1 border rounded text-sm border-gray-600 text-gray-100 bg-gray-800 hover:bg-gray-700">{% if t.completed %}Undo{% else %}Done{% endif %}</button>
        </form>
        <form method=post action="/delete/{{ t.id }}" onsubmit="return confirm('Delete?')">
          <button class="px-2 py-1 text-red-400 text-sm hover:text-red-300">Del</button>
        </form>
      </div>
    </li>
  {% endfor %}
  </ul>
</div>
"""

# DB lifecycle
@app.before_serving
async def setup_db():
    app.db = AsyncNanaSQLite(DB_PATH, bulk_load=False)

@app.after_serving
async def close_db():
    await app.db.close()

# Helpers
def now_iso():
    return datetime.now(timezone.utc).isoformat()

async def list_task_keys():
    keys = await app.db.akeys()
    return [k for k in keys if k.startswith('task_')]

async def get_all_tasks():
    tasks = []
    for k in await list_task_keys():
        t = await app.db.aget(k)
        if t is None:
            continue
        # ensure fields exist and are simple types
        tasks.append({
            'id': k,
            'title': str(t.get('title', '')),
            'completed': bool(t.get('completed', False)),
            'created_at': str(t.get('created_at', ''))
        })
    # sort by created_at (ISO strings sort lexicographically)
    tasks.sort(key=lambda x: x['created_at'] or "", reverse=True)
    return tasks

async def save_task(task_id, data):
    # data should be serializable (str, bool, numbers)
    await app.db.aset(task_id, data)

# Routes
@app.route('/')
async def index():
    tasks = await get_all_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t['completed'])
    content = await render_template_string(HOME, tasks=tasks, total=total, completed=completed)
    return await render_template_string(BASE, title='Todo', content=content)

@app.route('/add', methods=['POST'])
async def add():
    form = await request.form
    title = (form.get('title') or '').strip()
    if not title:
        return redirect(url_for('index'))
    tid = 'task_' + str(uuid.uuid4())
    task = {'title': title, 'completed': False, 'created_at': now_iso()}
    await save_task(tid, task)
    return redirect(url_for('index'))

@app.route('/toggle/<task_id>', methods=['POST'])
async def toggle(task_id):
    t = await app.db.aget(task_id)
    if not t:
        return redirect(url_for('index'))
    t['completed'] = not bool(t.get('completed', False))
    # don't change created_at; optionally add updated_at
    await save_task(task_id, t)
    return redirect(url_for('index'))

@app.route('/delete/<task_id>', methods=['POST'])
async def delete(task_id):
    await app.db.adelete(task_id)
    return redirect(url_for('index'))

@app.route('/api/tasks')
async def api_tasks():
    tasks = await get_all_tasks()
    return jsonify({'tasks': tasks, 'total': len(tasks)})

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)

