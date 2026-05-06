from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Ad, Message, User
from app.forms import AdForm
from app import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    latest_ads = Ad.query.order_by(Ad.date_posted.desc()).limit(4).all()
    return render_template('index.html', ads=latest_ads)

@main.route('/ads')
def ads():
    subject_filter = request.args.get('subject', 'Wszystkie')
    sort_by = request.args.get('sort', 'newest')
    query = Ad.query
    if subject_filter != 'Wszystkie':
        query = query.filter_by(subject=subject_filter)
    
    if sort_by == 'newest':
        query = query.order_by(Ad.date_posted.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Ad.date_posted.asc())
    elif sort_by == 'price_low':
        query = query.order_by(Ad.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Ad.price.desc())
        
    all_ads = query.all()
    subjects = ['Matematyka', 'Język Polski', 'Język Angielski', 'Chemia', 'Fizyka', 'Biologia', 'Historia', 'Geografia', 'Informatyka', 'Język Niemiecki', 'Inny']
    return render_template('ads.html', ads=all_ads, subjects=subjects, current_subject=subject_filter, current_sort=sort_by)

@main.route('/profile/<string:username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_ads = Ad.query.filter_by(author=user).order_by(Ad.date_posted.desc()).all()
    return render_template('public_profile.html', user=user, ads=user_ads, title=f"Profil {user.username}")

@main.route('/ad/<int:ad_id>')
def ad_details(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    return render_template('ad_details.html', title=ad.title, ad=ad)

@main.route('/ad/new', methods=['GET', 'POST'])
@login_required
def new_ad():
    if current_user.role != 'teacher' and not current_user.is_admin:
        flash('Tylko nauczyciele mogą dodawać ogłoszenia.', 'danger')
        return redirect(url_for('main.ads'))
    form = AdForm()
    if form.validate_on_submit():
        ad = Ad(title=form.title.data, subject=form.subject.data, description=form.description.data, price=form.price.data, author=current_user)
        db.session.add(ad)
        db.session.commit()
        flash('Ogłoszenie zostało dodane!', 'success')
        return redirect(url_for('main.ads'))
    return render_template('create_ad.html', title='Nowe ogłoszenie', form=form, legend='DODAJ OGŁOSZENIE')

@main.route('/ad/<int:ad_id>/update', methods=['GET', 'POST'])
@login_required
def update_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    if ad.author != current_user and not current_user.is_admin:
        abort(403)
    form = AdForm()
    if form.validate_on_submit():
        ad.title = form.title.data
        ad.subject = form.subject.data
        ad.description = form.description.data
        ad.price = form.price.data
        db.session.commit()
        flash('Ogłoszenie zostało zaktualizowane!', 'success')
        return redirect(url_for('main.ads'))
    elif request.method == 'GET':
        form.title.data = ad.title
        form.subject.data = ad.subject
        form.description.data = ad.description
        form.price.data = ad.price
    return render_template('create_ad.html', title='Edytuj ogłoszenie', form=form, legend='EDYTUJ OGŁOSZENIE')

@main.route('/ad/<int:ad_id>/delete', methods=['POST'])
@login_required
def delete_ad(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    if ad.author != current_user and not current_user.is_admin:
        abort(403)
    db.session.delete(ad)
    db.session.commit()
    flash('Ogłoszenie zostało usunięte!', 'success')
    return redirect(url_for('main.ads'))

@main.route('/send_message/<int:recipient_id>', methods=['POST'])
@login_required
def send_message(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    msg_body = request.form.get('message_body')
    ad_id = request.form.get('ad_id')
    
    if msg_body:
        msg = Message(sender_id=current_user.id, recipient_id=recipient.id, body=msg_body, ad_id=ad_id if ad_id else None)
        db.session.add(msg)
        db.session.commit()
    return redirect(request.referrer or url_for('main.home'))

@main.route('/messages')
@login_required
def messages():
    all_msgs = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).all()

    conversations = {}
    
    for m in all_msgs:
        other_user_id = m.recipient_id if m.sender_id == current_user.id else m.sender_id
        key = (other_user_id, m.ad_id)
        
        if key not in conversations or m.timestamp > conversations[key]['latest_msg'].timestamp:
            conversations[key] = {
                'other_user': db.session.get(User, other_user_id),
                'ad': db.session.get(Ad, m.ad_id) if m.ad_id else None,
                'latest_msg': m
            }

    sorted_convs = sorted(conversations.values(), key=lambda x: x['latest_msg'].timestamp, reverse=True)
    return render_template('messages.html', conversations=sorted_convs)

@main.route('/chat/<int:user_id>/<int:ad_id>')
@login_required
def chat_with(user_id, ad_id):
    other_user = User.query.get_or_404(user_id)
    ad = Ad.query.get_or_404(ad_id)
    
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user.id) & (Message.ad_id == ad.id)) |
        ((Message.sender_id == other_user.id) & (Message.recipient_id == current_user.id) & (Message.ad_id == ad.id))
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat_room.html', other_user=other_user, messages=messages, ad=ad)

@main.route('/test-500')
def test_500():
    abort(500)

@main.app_errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def error_500(error):
    return render_template('500.html'), 500

@main.app_errorhandler(403)
def error_403(error):
    return render_template('404.html'), 403