from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Note, Tag
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')  # Gets the note from the HTML
        tag_id = request.form.get('tag_id')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, tag_id=tag_id)  # providing the schema for the note
            db.session.add(new_note)  # adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')

    tags = Tag.query.filter_by(user_id=current_user.id).all()
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template("home.html", user=current_user, tags=tags, notes=notes)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash('You do not have permission to edit this note.', category='error')
        return redirect('/')

    if request.method == 'POST':
        new_data = request.form.get('note')

        if len(new_data) < 1:
            flash('Note is too short!', category='error')
        else:
            note.data = new_data
            db.session.commit()
            flash('Note updated!', category='success')
            return redirect('/')

    return render_template("edit_note.html", user=current_user, note=note)


@views.route('/create-tag', methods=['POST'])
@login_required
def create_tag():
    name = request.form.get('tag_name')

    if len(name) < 1:
        flash('Tag name is too short!', category='error')
    else:
        new_tag = Tag(name=name, user_id=current_user.id)
        db.session.add(new_tag)
        db.session.commit()
        flash('Tag added!', category='success')

    return redirect('/')


@views.route('/delete-tag/<int:tag_id>', methods=['POST'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if tag:
        if tag.user_id == current_user.id:
            # Delete all notes associated with the tag
            for note in tag.notes:
                db.session.delete(note)
            # Delete the tag
            db.session.delete(tag)
            db.session.commit()
            flash('Tag deleted!', category='success')
        else:
            flash('You do not have permission to delete this tag.', category='error')
    else:
        flash('Tag not found.', category='error')

    return redirect('/')


@views.route('/edit-tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if tag.user_id != current_user.id:
        flash('You do not have permission to edit this tag.', category='error')
        return redirect('/')

    if request.method == 'POST':
        new_name = request.form.get('tag_name')

        if len(new_name) < 1:
            flash('Tag name is too short!', category='error')
        else:
            tag.name = new_name
            db.session.commit()
            flash('Tag updated!', category='success')
            return redirect('/')

    return render_template("edit_tag.html", user=current_user, tag=tag)
