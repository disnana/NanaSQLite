#!/usr/bin/env python3
"""
Flask Integration Example with NanaSQLite

This example demonstrates how to use NanaSQLite with Flask
for a simple blog API.
"""

from flask import Flask, request, jsonify, abort
from nanasqlite import NanaSQLite
from datetime import datetime, timezone
import uuid


app = Flask(__name__)


# Database initialization
def get_db():
    """Get or create database instance"""
    if not hasattr(app, 'database'):
        app.database = NanaSQLite("blog.db", bulk_load=False)
    return app.database


# Cleanup on app shutdown
@app.teardown_appcontext
def close_db(error):
    """Cleanup on app context teardown (no database close)"""
    pass


# Helper functions
def get_post(post_id: str):
    """Get a post by ID or abort with 404"""
    db = get_db()
    post = db.get(f"post_{post_id}")
    if not post:
        abort(404, description="Post not found")
    return post


# Routes
@app.route('/posts', methods=['GET'])
def list_posts():
    """List all blog posts"""
    db = get_db()
    posts = []
    
    for key in db.keys():
        if key.startswith("post_"):
            post_id = key[5:]
            post_data = db.get(key)
            if post_data:
                posts.append({
                    "id": post_id,
                    **post_data
                })
    
    # Sort by created_at (newest first)
    posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return jsonify(posts)


@app.route('/posts', methods=['POST'])
def create_post():
    """Create a new blog post"""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'title' not in data or 'content' not in data:
        abort(400, description="Title and content are required")
    
    db = get_db()
    post_id = str(uuid.uuid4())
    
    post_data = {
        "title": data['title'],
        "content": data['content'],
        "author": data.get('author', 'Anonymous'),
        "tags": data.get('tags', []),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    db[f"post_{post_id}"] = post_data
    
    return jsonify({"id": post_id, **post_data}), 201


@app.route('/posts/search', methods=['GET'])
def search_posts():
    """Search posts by tag or keyword"""
    query = request.args.get('q', '').lower()
    tag = request.args.get('tag', '').lower()
    
    if not query and not tag:
        abort(400, description="Query parameter 'q' or 'tag' required")
    
    db = get_db()
    results = []
    
    for key in db.keys():
        if key.startswith("post_"):
            post_id = key[5:]
            post = db.get(key)
            if not post:
                continue
            
            # Search by tag
            if tag and tag in [t.lower() for t in post.get('tags', [])]:
                results.append({"id": post_id, **post})
                continue
            
            # Search by keyword in title or content
            if query:
                title = post.get('title', '').lower()
                content = post.get('content', '').lower()
                if query in title or query in content:
                    results.append({"id": post_id, **post})
    
    return jsonify(results)


@app.route('/posts/<post_id>', methods=['GET'])
def get_post_route(post_id):
    """Get a specific post"""
    post = get_post(post_id)
    return jsonify({"id": post_id, **post})


@app.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """Update a post"""
    post = get_post(post_id)
    data = request.get_json()
    
    if not data:
        abort(400, description="No data provided")
    
    # Update fields
    if 'title' in data:
        post['title'] = data['title']
    if 'content' in data:
        post['content'] = data['content']
    if 'author' in data:
        post['author'] = data['author']
    if 'tags' in data:
        post['tags'] = data['tags']
    
    post['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    db = get_db()
    db[f"post_{post_id}"] = post
    
    return jsonify({"id": post_id, **post})


@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a post"""
    get_post(post_id)  # Verify post exists
    
    db = get_db()
    del db[f"post_{post_id}"]
    
    return '', 204


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get blog statistics"""
    db = get_db()
    
    post_count = sum(1 for key in db.keys() if key.startswith("post_"))
    
    # Get all tags
    all_tags = set()
    for key in db.keys():
        if key.startswith("post_"):
            post = db.get(key)
            if post:
                all_tags.update(post.get('tags', []))
    
    return jsonify({
        "total_posts": post_count,
        "unique_tags": len(all_tags),
        "tags": sorted(list(all_tags))
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error.description)}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error.description)}), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print("Starting Flask server...")
    print("Blog API: http://localhost:5000")
    print("\nExample requests:")
    print("  GET    /posts          - List all posts")
    print("  POST   /posts          - Create a post")
    print("  GET    /posts/<id>     - Get a post")
    print("  PUT    /posts/<id>     - Update a post")
    print("  DELETE /posts/<id>     - Delete a post")
    print("  GET    /posts/search?q=keyword  - Search posts")
    print("  GET    /stats          - Get statistics")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
