from flask import Blueprint, request, jsonify, send_file
import mimetypes
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.note import Note
from app.models.user import User
from app.utils.helpers import sanitize_input, validate_required_fields, allowed_file, require_role
from app.utils.file_processor import extract_text_from_file
from app.services.ai_service import ai_service
from app.config import Config
import os
import logging

logger = logging.getLogger(__name__)

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')

@notes_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_note():
    """Upload learning material (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can upload notes'}), 403
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get metadata
        title = sanitize_input(request.form.get('title', file.filename))
        subject = sanitize_input(request.form.get('subject', ''))
        topic = sanitize_input(request.form.get('topic', ''))
        description = sanitize_input(request.form.get('description', ''))
        
        # Validate required fields
        is_valid, error = validate_required_fields(
            {'title': title, 'subject': subject},
            ['title', 'subject']
        )
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = __import__('time').time()
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract text
        file_type = filename.rsplit('.', 1)[1].lower()
        text_content = extract_text_from_file(filepath, file_type)
        
        if not text_content:
            os.remove(filepath)
            return jsonify({'error': 'Could not extract text from file'}), 400
        
        # Create note
        note = Note(
            title=title,
            content=text_content,
            teacher_id=user_id,
            file_type=file_type,
            subject=subject,
            topic=topic,
            description=description,
            file_path=filepath
        )
        
        note_id = note.save()
        
        # Add to vector store for RAG
        ai_response = ai_service.add_learning_material(note_id, text_content)
        
        if ai_response['success']:
            # Mark embeddings as stored
            note.mark_embeddings_stored()
        
        return jsonify({
            'message': 'Note uploaded successfully',
            'note': note.to_dict(),
            'embeddings_chunks': ai_response.get('chunks_added', 0)
        }), 201
    
    except Exception as e:
        logger.error(f"Error uploading note: {e}")
        return jsonify({'error': 'Could not upload note'}), 500

@notes_bp.route('', methods=['GET'])
def get_notes():
    """Get all published notes"""
    try:
        subject = request.args.get('subject', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        from app.db import db
        
        query = {'is_published': True}
        if subject:
            query['subject'] = subject
        
        note_collection = db.db['notes']
        total = note_collection.count_documents(query)
        
        notes = note_collection.find(query).sort('created_at', -1).skip((page-1)*limit).limit(limit)
        
        return jsonify({
            'notes': [Note(**note).to_dict() for note in notes],
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        return jsonify({'error': 'Could not fetch notes'}), 500

@notes_bp.route('/<note_id>', methods=['GET'])
def get_note(note_id):
    """Get specific note"""
    try:
        note = Note.find_by_id(note_id)
        
        if not note or not note.is_published:
            return jsonify({'error': 'Note not found'}), 404
        
        return jsonify({
            'note': note.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching note: {e}")
        return jsonify({'error': 'Could not fetch note'}), 500

@notes_bp.route('/teacher/<teacher_id>', methods=['GET'])
def get_teacher_notes(teacher_id):
    """Get all notes by a teacher"""
    try:
        notes = Note.find_by_teacher(teacher_id)
        
        return jsonify({
            'notes': [note.to_dict() for note in notes]
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching teacher notes: {e}")
        return jsonify({'error': 'Could not fetch notes'}), 500

@notes_bp.route('/<note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete note (teacher only)"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Only teachers can delete notes'}), 403
        
        note = Note.find_by_id(note_id)
        
        if not note or str(note.teacher_id) != user_id:
            return jsonify({'error': 'Note not found'}), 404
        
        # Remove from vector store
        ai_service.remove_learning_material(note_id)
        
        # Remove from database
        from app.db import db
        db.db['notes'].delete_one({'_id': note._id})
        
        # Remove file if exists
        if os.path.exists(note.file_path):
            os.remove(note.file_path)
        
        return jsonify({'message': 'Note deleted'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        return jsonify({'error': 'Could not delete note'}), 500

@notes_bp.route('/download/<note_id>', methods=['GET'])
@jwt_required()
def download_note(note_id):
    """Download the original file of a note"""
    try:
        note = Note.find_by_id(note_id)
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        if not note.file_path or not os.path.exists(note.file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        # Determine mimetype
        mime_type, _ = mimetypes.guess_type(note.file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Use original filename from file_path
        original_filename = os.path.basename(note.file_path)
        # Strip timestamp prefix (format: timestamp_originalname)
        parts = original_filename.split('_', 1)
        download_name = parts[1] if len(parts) > 1 else original_filename
        
        from flask import current_app
        absolute_path = os.path.abspath(note.file_path)
        
        return send_file(
            absolute_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=download_name
        )
    
    except Exception as e:
        logger.error(f"Error downloading note: {e}")
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@notes_bp.route('/search', methods=['GET'])
def search_notes():
    """Search notes by content"""
    try:
        query = sanitize_input(request.args.get('q', ''))
        
        if len(query) < 2:
            return jsonify({'error': 'Query too short'}), 400
        
        from app.db import db
        
        note_collection = db.db['notes']
        notes = note_collection.find({
            'is_published': True,
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}},
                {'subject': {'$regex': query, '$options': 'i'}}
            ]
        }).limit(20)
        
        return jsonify({
            'results': [Note(**note).to_dict() for note in notes]
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        return jsonify({'error': 'Could not search notes'}), 500

@notes_bp.route('/rag-search', methods=['GET'])
def rag_search():
    """Search notes using RAG"""
    try:
        query = sanitize_input(request.args.get('q', ''))
        
        if len(query) < 2:
            return jsonify({'error': 'Query too short'}), 400
        
        results = ai_service.vector_store.search(query, top_k=5)
        
        return jsonify({
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"Error in RAG search: {e}")
        return jsonify({'error': 'Could not perform search'}), 500
