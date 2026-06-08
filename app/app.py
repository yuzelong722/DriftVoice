#!/usr/bin/env python3
"""
研声漂流 - 研究生匿名朋辈支持平台
支持用户系统、人物画像、卡通头像、联机数据同步
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os, secrets

app = Flask(__name__)
# 确保 instance 目录存在
os.makedirs(app.instance_path, exist_ok=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
DB_PATH = os.path.join(app.instance_path, 'gravelcho.db')
# sqlite:///relative (3 slashes) or sqlite:////absolute (4 slashes)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============ 数据模型 ============

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anonymous_id = db.Column(db.String(50), unique=True, nullable=False)
    avatar_animal = db.Column(db.String(50), default='fox')
    avatar_color = db.Column(db.String(20), default='#8B9E8B')
    grade = db.Column(db.String(20))
    major_category = db.Column(db.String(50))
    interests = db.Column(db.Text)
    persona_tags = db.Column(db.Text)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    questions = db.relationship('Question', backref='user', lazy=True)
    replies = db.relationship('Reply', backref='user', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50))
    grade = db.Column(db.String(20))
    response_type = db.Column(db.String(50))
    allow_public = db.Column(db.Boolean, default=False)
    is_risk = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    replies = db.relationship('Reply', backref='question', lazy=True, cascade='all, delete-orphan')
    target_persona = db.Column(db.Text)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    response_style = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    is_thanked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# ============ 卡通动物头像 ============
ANIMAL_AVATARS = [
    ('fox',     '小狐狸', '#E07A5F'),
    ('panda',   '小熊猫', '#5A6358'),
    ('owl',     '小猫头鹰', '#8B9E8B'),
    ('cat',     '小猫咪', '#D4A853'),
    ('dog',     '小狗狗', '#C8D5C8'),
    ('rabbit',  '小兔子', '#F2D0C7'),
    ('bear',    '小熊',   '#A8C5D6'),
    ('penguin', '小企鹅', '#2D3432'),
    ('koala',   '小考拉', '#9CA89A'),
    ('raccoon', '小浣熊', '#D6B060'),
    ('deer',    '小鹿',   '#C8A2C8'),
    ('arctic_fox', '小北极狐', '#A8D8EA'),
]

COLOR_MAP = {a[0]: a[2] for a in ANIMAL_AVATARS}

def get_animal_svg(animal, size=32):
    """返回动物SVG HTML字符串"""
    animal = animal or 'fox'
    color = COLOR_MAP.get(animal, '#8B9E8B')
    svgs = {
        'fox': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="20" r="18" fill="{color}" opacity="0.3"/><circle cx="20" cy="20" r="14" fill="{color}" opacity="0.5"/><circle cx="15" cy="16" r="3" fill="{color}"/><circle cx="25" cy="16" r="3" fill="{color}"/><circle cx="14" cy="15" r="1.2" fill="#2D3432"/><circle cx="24" cy="15" r="1.2" fill="#2D3432"/></svg>',
        'panda': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="15" fill="#fff" stroke="{color}" stroke-width="1.2"/><circle cx="14" cy="16" r="5" fill="{color}"/><circle cx="26" cy="16" r="5" fill="{color}"/><circle cx="13" cy="15" r="2" fill="#fff"/><circle cx="25" cy="15" r="2" fill="#fff"/></svg>',
        'owl': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="15" fill="{color}"/><circle cx="14" cy="18" r="6" fill="#F0F4F0"/><circle cx="26" cy="18" r="6" fill="#F0F4F0"/><circle cx="14" cy="18" r="3.5" fill="#2D3432"/><circle cx="26" cy="18" r="3.5" fill="#2D3432"/></svg>',
        'cat': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="15" fill="{color}" opacity="0.4"/><path d="M10 10 L6 2 L16 8" fill="{color}" opacity="0.6"/><path d="M30 10 L34 2 L24 8" fill="{color}" opacity="0.6"/><circle cx="15" cy="19" r="2.5" fill="#2D3432"/><circle cx="25" cy="19" r="2.5" fill="#2D3432"/></svg>',
        'dog': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="15" fill="{color}" opacity="0.3"/><ellipse cx="13" cy="12" rx="5" ry="6" fill="{color}" opacity="0.5"/><ellipse cx="27" cy="12" rx="5" ry="6" fill="{color}" opacity="0.5"/><circle cx="15" cy="19" r="2.5" fill="#2D3432"/><circle cx="25" cy="19" r="2.5" fill="#2D3432"/></svg>',
        'rabbit': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><ellipse cx="20" cy="24" rx="12" ry="14" fill="{color}" opacity="0.4"/><path d="M12 14 Q8 -4 18 8" fill="{color}" opacity="0.5"/><path d="M28 14 Q32 -4 22 8" fill="{color}" opacity="0.5"/><circle cx="16" cy="22" r="2" fill="#2D3432"/><circle cx="24" cy="22" r="2" fill="#2D3432"/></svg>',
        'bear': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="15" fill="{color}" opacity="0.3"/><circle cx="14" cy="16" r="5" fill="{color}" opacity="0.5"/><circle cx="26" cy="16" r="5" fill="{color}" opacity="0.5"/><circle cx="15" cy="20" r="2.5" fill="#2D3432"/><circle cx="25" cy="20" r="2.5" fill="#2D3432"/></svg>',
        'penguin': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><ellipse cx="20" cy="26" rx="12" ry="12" fill="#2D3432"/><ellipse cx="20" cy="26" rx="8" ry="10" fill="#F0F4F0"/><circle cx="15" cy="18" r="2.5" fill="#2D3432"/><circle cx="25" cy="18" r="2.5" fill="#2D3432"/></svg>',
        'koala': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="14" fill="{color}" opacity="0.4"/><circle cx="14" cy="16" r="5" fill="{color}" opacity="0.6"/><circle cx="26" cy="16" r="5" fill="{color}" opacity="0.6"/><circle cx="13" cy="15" r="2.5" fill="#2D3432"/><circle cx="25" cy="15" r="2.5" fill="#2D3432"/></svg>',
        'raccoon': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="14" fill="{color}" opacity="0.3"/><ellipse cx="15" cy="16" rx="3" ry="4" fill="{color}" opacity="0.6"/><ellipse cx="25" cy="16" rx="3" ry="4" fill="{color}" opacity="0.6"/><circle cx="14" cy="15" r="1.5" fill="#2D3432"/><circle cx="24" cy="15" r="1.5" fill="#2D3432"/></svg>',
        'deer': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="14" fill="{color}" opacity="0.3"/><path d="M14 10 Q10 -6 16 6" stroke="{color}" stroke-width="2" fill="none"/><path d="M26 10 Q30 -6 24 6" stroke="{color}" stroke-width="2" fill="none"/><circle cx="15" cy="19" r="2.5" fill="#2D3432"/><circle cx="25" cy="19" r="2.5" fill="#2D3432"/></svg>',
        'arctic_fox': f'<svg viewBox="0 0 40 40" width="{size}" height="{size}"><circle cx="20" cy="22" r="14" fill="{color}" opacity="0.3"/><path d="M12 10 Q6 0 16 6 Q13 1 20 3 Q27 1 24 6 Q34 0 28 10" fill="{color}" opacity="0.5"/><circle cx="15" cy="16" r="3" fill="{color}" opacity="0.6"/><circle cx="25" cy="16" r="3" fill="{color}" opacity="0.6"/></svg>',
    }
    return svgs.get(animal, svgs['fox'])

def get_display_name(user):
    if not user:
        return '匿名用户'
    name_map = {a[0]: a[1] for a in ANIMAL_AVATARS}
    animal_name = name_map.get(user.avatar_animal, '匿名')
    return f'{animal_name}#{user.id}'

# ============ 用户辅助函数 ============

def get_current_user():
    if 'user_id' not in session:
        return None
    user = db.session.get(User, session['user_id'])
    if user:
        user.last_active = datetime.now(timezone.utc)
        db.session.commit()
    return user

def require_user():
    return get_current_user()

# ============ 上下文处理器 ============
@app.context_processor
def inject_user():
    user = get_current_user()
    return dict(current_user=user, get_display_name=get_display_name,
                get_animal_svg=get_animal_svg, ANIMAL_AVATARS=ANIMAL_AVATARS, COLOR_MAP=COLOR_MAP)

# ============ 路由 ============

@app.route('/')
def index():
    user = get_current_user()
    stats = {
        'questions': Question.query.filter_by(status='open').count(),
        'replies': Reply.query.count(),
        'experiences': Experience.query.count(),
        'users': User.query.count(),
    }
    # 问题排行榜（按回复数）
    top_questions_raw = Question.query.outerjoin(Reply).group_by(Question.id).order_by(
        db.func.count(Reply.id).desc(), Question.created_at.desc()
    ).limit(5).all()
    # 给每个问题添加 reply_count 属性
    top_questions = []
    for q in top_questions_raw:
        q.reply_count = Reply.query.filter_by(question_id=q.id).count()
        top_questions.append(q)
    return render_template('index.html', user=user, stats=stats, top_questions=top_questions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        anonymous_id = 'user_' + secrets.token_hex(4)
        avatar_animal = request.form.get('avatar_animal', 'fox')
        avatar_color = COLOR_MAP.get(avatar_animal, '#8B9E8B')
        interests = ','.join(request.form.getlist('interests'))
        persona_tags = ','.join(request.form.getlist('persona_tags'))
        major = request.form.get('major_category', '')
        if major == '__custom__':
            major = request.form.get('custom_major', '').strip()
        user = User(
            anonymous_id=anonymous_id,
            avatar_animal=avatar_animal,
            avatar_color=avatar_color,
            grade=request.form.get('grade', ''),
            major_category=major,
            interests=interests,
            persona_tags=persona_tags,
            bio=request.form.get('bio', ''),
        )
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash('欢迎加入研声漂流！')
        return redirect(url_for('index'))
    return render_template('register.html', animals=ANIMAL_AVATARS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uid = request.form.get('user_id', '').strip()
        user = None
        if uid.isdigit():
            user = db.session.get(User, int(uid))
        if not user:
            user = User.query.filter_by(anonymous_id=uid).first()
        if user:
            session['user_id'] = user.id
            flash(f'欢迎回来，{get_display_name(user)}！')
            return redirect(url_for('index'))
        flash('未找到该用户，请检查ID')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('已退出登录')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = require_user()
    if not user:
        return redirect(url_for('register'))
    if request.method == 'POST':
        avatar_animal = request.form.get('avatar_animal', user.avatar_animal)
        user.avatar_animal = avatar_animal
        user.avatar_color = COLOR_MAP.get(avatar_animal, '#8B9E8B')
        user.grade = request.form.get('grade', user.grade)
        major = request.form.get('major_category', user.major_category)
        if major == '__custom__':
            major = request.form.get('custom_major', '').strip() or user.major_category
        user.major_category = major
        user.interests = ','.join(request.form.getlist('interests'))
        user.persona_tags = ','.join(request.form.getlist('persona_tags'))
        user.bio = request.form.get('bio', user.bio)
        db.session.commit()
        flash('资料已更新')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user, animals=ANIMAL_AVATARS)

@app.route('/question/create', methods=['GET', 'POST'])
def create_question():
    user = require_user()
    if not user:
        return redirect(url_for('register'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            flash('标题和内容不能为空')
            return redirect(url_for('create_question'))
        q = Question(
            user_id=user.id,
            title=title,
            content=content,
            category=request.form.get('category', ''),
            subcategory=request.form.get('subcategory', ''),
            grade=request.form.get('grade', ''),
            response_type=request.form.get('response_type', ''),
            allow_public=bool(request.form.get('allow_public')),
            status='open',
        )
        db.session.add(q)
        db.session.commit()
        flash('问题已发布！')
        return redirect(url_for('index'))
    return render_template('create_question.html', user=user)

@app.route('/questions/pending')
def pending_questions():
    user = require_user()
    return render_template('pending_questions.html', user=user)

@app.route('/question/<int:question_id>/reply', methods=['GET', 'POST'])
def reply_to_question(question_id):
    user = require_user()
    if not user:
        return redirect(url_for('register'))
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash('回复内容不能为空')
            return redirect(url_for('reply_to_question', question_id=question_id))
        reply = Reply(
            question_id=question_id,
            user_id=user.id,
            content=content,
            response_style=request.form.get('response_style', ''),
        )
        db.session.add(reply)
        db.session.commit()
        flash('回复已发送！')
        return redirect(url_for('pending_questions'))
    return render_template('create_reply.html', question=question, user=user)

@app.route('/my/messages')
def my_messages():
    user = require_user()
    if not user:
        return redirect(url_for('register'))
    my_questions = Question.query.filter_by(user_id=user.id).order_by(Question.created_at.desc()).all()
    my_replies = Reply.query.filter_by(user_id=user.id).order_by(Reply.created_at.desc()).all()
    received_replies = []
    for q in my_questions:
        for r in q.replies:
            if r.user_id != user.id:
                received_replies.append((q, r))
    received_replies.sort(key=lambda x: x[1].created_at, reverse=True)
    return render_template('my_messages.html',
                           user=user,
                           my_questions=my_questions,
                           my_replies=my_replies,
                           received_replies=received_replies)

@app.route('/experience')
def experience_library():
    user = require_user()
    return render_template('experience_library.html', user=user)

# ============ API 端点 ============

@app.route('/api/questions/pending')
def api_pending_questions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort = request.args.get('sort', 'new')
    category = request.args.get('category', '')
    grade = request.args.get('grade', '')
    major = request.args.get('major', '')
    q = request.args.get('q', '').strip()
    user = get_current_user()

    query = Question.query.filter_by(status='open')

    # 分类筛选
    if category:
        query = query.filter(Question.category == category)
    # 年级筛选
    if grade:
        query = query.filter(Question.grade == grade)
    # 专业筛选（通过关联 user 的 major_category）
    if major:
        query = query.join(User).filter(User.major_category == major)
    # 模糊搜索（标题 + 内容）
    if q:
        like_pattern = f'%{q}%'
        query = query.filter(db.or_(
            Question.title.like(like_pattern),
            Question.content.like(like_pattern)
        ))

    if sort == 'hot':
        query = query.outerjoin(Reply).group_by(Question.id).order_by(
            db.func.count(Reply.id).desc(), Question.created_at.desc()
        )
    else:
        query = query.order_by(Question.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    result = []
    for q_obj in items:
        result.append({
            'id': q_obj.id,
            'title': q_obj.title,
            'content': q_obj.content[:120] + '...' if len(q_obj.content) > 120 else q_obj.content,
            'category': q_obj.category,
            'grade': q_obj.grade,
            'response_type': q_obj.response_type,
            'created_at': q_obj.created_at.strftime('%Y-%m-%d'),
            'created_at_raw': int(q_obj.created_at.timestamp()),
            'reply_count': Reply.query.filter_by(question_id=q_obj.id).count(),
            'user_avatar': q_obj.user.avatar_animal if q_obj.user else 'fox',
            'user_display': get_display_name(q_obj.user) if q_obj.user else '匿名',
            'user_major': q_obj.user.major_category if q_obj.user else '',
        })
    return jsonify({'questions': result, 'has_more': pagination.has_next})

@app.route('/api/questions/top')
def api_questions_top():
    questions = Question.query.outerjoin(Reply).group_by(Question.id).order_by(
        db.func.count(Reply.id).desc(), Question.created_at.desc()
    ).limit(20).all()
    result = []
    for q in questions:
        rc = Reply.query.filter_by(question_id=q.id).count()
        result.append({
            'id': q.id,
            'title': q.title,
            'category': q.category,
            'reply_count': rc,
            'created_at': q.created_at.strftime('%Y-%m-%d'),
        })
    return jsonify(result)

@app.route('/api/questions/<int:question_id>')
def api_get_question(question_id):
    q = Question.query.get_or_404(question_id)
    replies = Reply.query.filter_by(question_id=question_id).order_by(Reply.created_at.asc()).all()
    return jsonify({
        'id': q.id,
        'title': q.title,
        'content': q.content,
        'category': q.category,
        'grade': q.grade,
        'response_type': q.response_type,
        'created_at': q.created_at.strftime('%Y-%m-%d'),
        'allow_public': q.allow_public,
        'is_public': q.is_public,
        'status': q.status,
        'user_avatar': q.user.avatar_animal if q.user else 'fox',
        'user_display': get_display_name(q.user) if q.user else '匿名',
        'replies': [{
            'id': r.id,
            'content': r.content,
            'response_style': r.response_style,
            'created_at': r.created_at.strftime('%Y-%m-%d'),
            'is_thanked': r.is_thanked,
            'user_grade': r.user.grade if r.user else '',
            'user_avatar': r.user.avatar_animal if r.user else 'fox',
            'user_display': get_display_name(r.user) if r.user else '匿名',
        } for r in replies]
    })

@app.route('/api/questions/<int:question_id>/replies', methods=['POST'])
def api_create_reply(question_id):
    user = require_user()
    if not user:
        return jsonify({'error': '请先登录'}), 401
    data = request.get_json(force=True, silent=True) or {}
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'error': '回复内容不能为空'}), 400
    reply = Reply(
        question_id=question_id,
        user_id=user.id,
        content=content,
        response_style=data.get('response_style', ''),
    )
    db.session.add(reply)
    db.session.commit()
    return jsonify({'message': '回复成功', 'reply_id': reply.id}), 201

@app.route('/api/replies/<int:reply_id>/thank', methods=['POST'])
def api_thank_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    reply.is_thanked = True
    db.session.commit()
    return jsonify({'message': '感谢已发送'})

@app.route('/api/experiences')
def api_get_experiences():
    major = request.args.get('major', '')
    q = request.args.get('q', '').strip()

    query = Experience.query.order_by(Experience.created_at.desc())

    if major or q:
        query = query.join(Experience.question)

    # 专业筛选（通过关联问题的提问者专业）
    if major:
        query = query.join(Question.user).filter(User.major_category == major)
    # 模糊搜索（问题标题 + 内容 + 回复内容）
    if q:
        like_pattern = f'%{q}%'
        query = query.filter(db.or_(
            Question.title.like(like_pattern),
            Question.content.like(like_pattern),
            Reply.content.like(like_pattern)
        ))

    exps = query.all()
    result = []
    for exp in exps:
        q_obj = db.session.get(Question, exp.question_id)
        r = db.session.get(Reply, exp.reply_id)
        if q_obj and r:
            result.append({
                'id': exp.id,
                'category': exp.category,
                'question': {
                    'id': q_obj.id, 'title': q_obj.title, 'content': q_obj.content,
                    'created_at': q_obj.created_at.strftime('%Y-%m-%d'),
                },
                'reply': {'id': r.id, 'content': r.content, 'response_style': r.response_style}
            })
    return jsonify(result)

@app.route('/api/questions/<int:question_id>/close', methods=['POST'])
def api_close_question(question_id):
    q = Question.query.get_or_404(question_id)
    q.status = 'closed'
    db.session.commit()
    return jsonify({'message': '问题已关闭'})

@app.route('/api/questions/<int:question_id>/make_public', methods=['POST'])
def api_make_public(question_id):
    q = Question.query.get_or_404(question_id)
    q.is_public = True
    if not Experience.query.filter_by(question_id=question_id).first():
        first_reply = Reply.query.filter_by(question_id=question_id).order_by(Reply.created_at.asc()).first()
        if first_reply:
            exp = Experience(question_id=question_id, reply_id=first_reply.id, category=q.category or '综合')
            db.session.add(exp)
    db.session.commit()
    return jsonify({'message': '已申请公开，审核通过后展示在经验库'})

# ============ 数据库初始化 ============

def init_db():
    db.create_all()
    if User.query.first() is not None:
        return

    users_data = [
        ('user_001', '研一', '计算机科学', '导师与课题组,科研与论文,职业规划', '刚入学新生,需要方向指导', 'fox', '#E07A5F'),
        ('user_002', '研三', '计算机科学', '职业规划,科研与论文,情绪与压力', '经历过秋招,发过论文,实验室矛盾', 'panda', '#5A6358'),
        ('user_003', '博士', '人工智能', '科研与论文,职业规划,情绪与压力', '被拒稿多次,延期风险,求职焦虑', 'owl', '#8B9E8B'),
        ('user_004', '研二', '电子信息', '人际关系,生活适应,导师与课题组', '实验室矛盾,跨专业适应', 'cat', '#D4A853'),
        ('user_005', '研一', '机械工程', '生活适应,科研与论文', '跨专业考研,基础薄弱', 'dog', '#C8D5C8'),
        ('user_006', '研二', '生物医学', '职业规划,情绪与压力', '想转行,科研压力大,失眠', 'rabbit', '#F2D0C7'),
        ('user_007', '博士', '计算机科学', '导师与课题组,职业规划', '博四延毕风险,考虑退学', 'bear', '#A8C5D6'),
        ('user_008', '研三', '金融', '职业规划,情绪与压力', '拿到offer,实习经历,求职成功', 'penguin', '#2D3432'),
        ('user_009', '研一', '计算机科学', '生活适应,人际关系', '刚入学迷茫,宿舍关系', 'koala', '#9CA89A'),
        ('user_010', '研二', '电子信息', '科研与论文,导师与课题组', '论文写作困难,导师push', 'raccoon', '#D6B060'),
        ('user_011', '博士', '生物医学', '科研与论文,情绪与压力', '实验反复失败,想放弃', 'deer', '#C8A2C8'),
        ('user_012', '研三', '机械工程', '职业规划,生活适应', '找工作焦虑,跨专业求职', 'arctic_fox', '#A8D8EA'),
        ('user_013', '研一', '金融', '生活适应,人际关系', '住宿不适应,同学关系', 'fox', '#E07A5F'),
        ('user_014', '研二', '人工智能', '科研与论文,职业规划', '顶会论文,实习经历,大厂offer', 'panda', '#5A6358'),
        ('user_015', '博士', '计算机科学', '导师与课题组,情绪与压力', '和导师关系紧张,考虑换导师', 'owl', '#8B9E8B'),
    ]

    users = []
    for uid, grade, major, interests, persona, animal, color in users_data:
        u = User(
            anonymous_id=uid, grade=grade, major_category=major,
            interests=interests, persona_tags=persona,
            avatar_animal=animal, avatar_color=color,
        )
        db.session.add(u)
        users.append(u)
    db.session.commit()

    # 80+ 问题
    questions_data = [
        # 导师与课题组 (15)
        (1, '导师方向与我的兴趣不匹配，该怎么办？', '研一刚入学，发现导师的研究方向和我在本科时的兴趣不太一样。现在做实验总是提不起兴趣，也不知道该怎么和导师沟通...', '导师与课题组', '导师方向不匹配', '研一', '经验建议', True, 'open'),
        (1, '和导师沟通总被怼，是不是我太笨了？', '每次组会汇报，导师都会挑出很多问题，有时当着全组的面说我逻辑不清。现在一要组会就紧张得睡不着...', '导师与课题组', '师生沟通', '研一', '情绪支持', True, 'open'),
        (1, '导师让我延期毕业，我该怎么办？', '博三了，导师暗示我文章不够，建议延期一年。但我已经签了工作offer，很纠结...', '导师与课题组', '延期毕业', '博士', '现实方法', False, 'open'),
        (2, '导师压着不让实习怎么办？', '研二了想出去实习，但导师说实验室项目离不开人，不让去。可是同门都去实习了...', '导师与课题组', '实习与科研冲突', '研二', '经验建议', True, 'open'),
        (7, '想换导师但怕被针对', '和现在的导师方向完全不合，想换但听说这个老师会记仇，以前有学生换导师后被穿小鞋...', '导师与课题组', '换导师', '研一', '经验建议', False, 'open'),
        (15, '导师关系紧张，每天实验室如坐针毡', '博一进来就和导师在一些学术观点上有分歧，现在导师对我很冷淡，不知道还能不能顺利毕业...', '导师与课题组', '师生关系', '博士', '情绪支持', True, 'open'),
        (9, '导师让我做不感兴趣的横向项目', '导师接了很多横向项目，每天就是写文档做汇报，完全没有时间做自己的研究...', '导师与课题组', '横向项目', '研一', '现实方法', True, 'open'),
        (7, '导师建议我转博，但我不想', '硕士期间导师一直暗示我转博，说我的条件很好。但我真的很想工作，不知道怎么拒绝...', '导师与课题组', '是否转博', '研二', '经验建议', False, 'open'),
        (1, '导师对我的指导很少，感觉被放养', '入学快一年了，导师很少给我指导，每次问问题都是让我自己看论文。是不是导师不喜欢我？', '导师与课题组', '导师指导', '研一', '情绪支持', True, 'open'),
        (15, '导师抢我一作怎么办？', '文章终于写完了，导师说要当一作，说这样有利于文章录用。但我做了绝大部分工作...', '导师与课题组', '作者排序', '博士', '现实方法', False, 'open'),
        (4, '实验室师兄师姐对我爱答不理', '刚进实验室，师兄师姐都很冷漠，问问题也不太愿意回答。是我做错了什么吗？', '导师与课题组', '实验室人际关系', '研一', '情绪支持', True, 'open'),
        (2, '导师人品有问题，要不要举报？', '发现导师有学术不端的行为，很纠结要不要举报，但又怕影响自己毕业...', '导师与课题组', '学术伦理', '博士', '现实方法', False, 'open'),
        (9, '导师让我帮忙带孩子和做家务', '导师经常让我帮她接孩子、买菜、处理家庭事务，感觉自己不像研究生像保姆...', '导师与课题组', '导师边界', '研一', '情绪支持', False, 'open'),
        (7, '和导师性格不合，每次沟通都很痛苦', '导师是那种很强势的人，我是比较内向的性格，每次交流都很有压力，不知道怎么改善...', '导师与课题组', '师生性格', '博士', '经验建议', True, 'open'),
        (1, '导师给我的研究方向太冷门了', '导师让我做一个非常冷门的方向，说是前沿，但我担心毕业不好找工作...', '导师与课题组', '研究方向', '研一', '职业规划', True, 'open'),
        # 科研与论文 (15)
        (3, '论文被拒了三次，越来越没信心', '博士二年级，论文已经被拒了三次，每次审稿意见都很打击人。现在一看到邮件就心慌...', '科研与论文', '论文被拒', '博士', '情绪支持', False, 'open'),
        (3, '实验做了半年，发现方向错了', '博二了，实验做了半年，最近才发现整个方向有问题。现在要推翻重来，感觉时间不够了...', '科研与论文', '研究方向错误', '博士', '情绪支持', True, 'open'),
        (10, '论文写作太痛苦了，每天写不出几行', '研二了，毕业论文开题后一直写不出东西，对着空白文档发呆，deadline越来越近...', '科研与论文', '论文写作', '研二', '经验建议', True, 'open'),
        (11, '实验反复失败，是不是我不适合读博？', '博一快结束了，实验一直没有正结果，看着同门都有进展，很怀疑自己的能力...', '科研与论文', '实验失败', '博士', '情绪支持', False, 'open'),
        (3, '顶会论文压力太大，每天焦虑失眠', '导师要求必须发顶会才能毕业，但现在竞争太激烈了，感觉自己做不到...', '科研与论文', '顶会压力', '博士', '情绪支持', True, 'open'),
        (14, '论文被师兄抄袭了怎么办？', '发现我之前分享给师兄的idea，被他写成了论文投出去了，作者只有他自己...', '科研与论文', '学术不端', '研二', '现实方法', False, 'open'),
        (10, '不懂怎么读文献，效率很低', '研一了还不知道怎么高效读文献，每天花很多时间但感觉没吸收什么...', '科研与论文', '文献阅读', '研一', '经验建议', True, 'open'),
        (11, '数据不够，论文发不出来', '实验数据一直不够支撑论文，导师说再不行就延毕，很焦虑...', '科研与论文', '数据不足', '博士', '现实方法', False, 'open'),
        (3, '论文审稿周期太长，耽误毕业', '论文投出去已经8个月了还没有结果，导师说可能赶不上毕业了...', '科研与论文', '审稿周期', '博士', '情绪支持', True, 'open'),
        (14, '想发顶会但代码能力不够', '研究方向需要很强的coding能力，但我代码基础很差，现在每天都在恶补但还是很吃力...', '科研与论文', '代码能力', '研一', '经验建议', True, 'open'),
        (10, '导师对论文质量要求太高', '每次给导师看论文草稿都被批得体无完肤，已经改了十几遍了还是不满意...', '科研与论文', '导师要求', '研二', '情绪支持', True, 'open'),
        (11, '实验结果无法复现，是不是我记错了？', '之前的一个关键实验现在怎么都复现不了，怀疑是不是当时出了什么问题...', '科研与论文', '实验复现', '博士', '现实方法', False, 'open'),
        (3, '没有论文创新点，感觉做不出东西', '研究了半年，发现别人已经做过了，现在完全找不到创新点...', '科研与论文', '创新点', '博士', '情绪支持', True, 'open'),
        (14, '论文合作者之间分工不均', '和另一个同学合作论文，但我做了大部分工作，对方却要求共同一作...', '科研与论文', '合作分工', '研二', '现实方法', False, 'open'),
        (10, '毕业论文和期刊论文能同时准备吗？', '导师希望我同时准备期刊论文和毕业论文，但时间根本不够，不知道怎么平衡...', '科研与论文', '时间管理', '研二', '经验建议', True, 'open'),
        # 职业规划 (15)
        (2, '不想读博，该怎么规划就业？', '研二了，发现自己对科研没什么兴趣，不想读博。但看着同门都在准备读博，自己很迷茫...', '职业规划', '不确定是否读博', '研二', '现实方法', True, 'closed'),
        (8, '拿到了大厂offer，但导师不让走', '秋招拿到了不错的offer，但导师说毕业论文可能做不完，暗示我不要去实习...', '职业规划', '就业与科研', '研三', '现实方法', True, 'open'),
        (7, '博士延毕风险大，要不要直接找工作？', '博四了，文章还差一篇，导师暗示可能要延毕。家里催着找工作，但又不甘心...', '职业规划', '延毕与就业', '博士', '现实方法', True, 'open'),
        (6, '想转行，但专业背景不匹配', '生物医学研究生，想转行做程序员，但感觉竞争力不够，需要怎么准备？', '职业规划', '转行', '研二', '经验建议', True, 'open'),
        (12, '机械工程就业前景不好，要不要跨专业求职？', '本专业的岗位太少了，工资也不高，想转行但不知道转什么方向...', '职业规划', '跨专业求职', '研三', '经验建议', False, 'open'),
        (8, '金融机构实习经历怎么找？', '金融专硕，但没有相关实习经历，秋招很担心找不到好工作...', '职业规划', '实习经历', '研二', '经验建议', True, 'open'),
        (2, '秋招准备从什么时候开始？', '研二结束，感觉身边同学都在准备秋招了，但我对求职完全没概念，不知道从哪开始...', '职业规划', '秋招准备', '研二', '经验建议', True, 'open'),
        (14, 'AI方向就业竞争太激烈了', '人工智能方向现在找工作的人太多了，感觉自己没什么优势，要不要转方向？', '职业规划', '就业竞争', '研三', '情绪支持', False, 'open'),
        (6, '科研做不下去了，能找到工作吗？', '文章发不出来，很担心简历上没什么可写的，找工作会不会很困难...', '职业规划', '简历竞争力', '研三', '情绪支持', True, 'open'),
        (12, '考公还是去企业？很纠结', '家人希望我考公务员，但自己更想去企业。两边都很羡慕，不知道怎么选...', '职业规划', '职业选择', '研三', '经验建议', False, 'open'),
        (8, '拿到了多个offer，怎么选？', '秋招拿到了3个offer，各有优劣，不知道该怎么权衡...', '职业规划', 'offer选择', '研三', '经验建议', True, 'open'),
        (2, '读博的就业优势到底有多大？', '看到很多博士毕业后收入和硕士差不多，不知道读博的性价比还值不值得...', '职业规划', '读博性价比', '研二', '现实方法', False, 'open'),
        (6, '生物医药行业值得去吗？', '拿到一个医美公司的offer，工资不错但感觉不是正统科研路线...', '职业规划', '行业选择', '研三', '经验建议', True, 'open'),
        (4, '电子信息有哪些好的就业方向？', '研一结束，想提前了解本专业的就业方向，好有针对性地准备...', '职业规划', '就业方向', '研一', '经验建议', True, 'open'),
        (14, '实习被压榨，还要继续吗？', '大厂实习每天加班到很晚，感觉学不到东西，但担心退出后简历有gap...', '职业规划', '实习体验', '研二', '情绪支持', False, 'open'),
        # 人际关系 (10)
        (4, '实验室氛围很压抑，每天都不想去', '组内师兄师姐关系很复杂，导师也很严厉。每天走进实验室都觉得喘不过气...', '人际关系', '实验室氛围', '研二', '情绪支持', True, 'open'),
        (4, '和同门竞争关系很严重', '同一个导师下的同门，在资源分配和论文合作上竞争很激烈，感觉大家都很有心机...', '人际关系', '同门竞争', '研二', '情绪支持', False, 'open'),
        (5, '宿舍关系紧张，怎么办？', '和室友性格不合，经常有小摩擦，现在回宿舍都很不舒服...', '人际关系', '宿舍关系', '研一', '情绪支持', True, 'open'),
        (9, '和导师性格不合，每次沟通都很痛苦', '导师是那种很强势的人，我是比较内向的性格，每次交流都很有压力...', '人际关系', '师生沟通', '研一', '经验建议', True, 'open'),
        (4, '被师兄性骚扰了，不敢说', '实验室师兄经常说一些不合适的话，有时候还会有肢体接触，很害怕但不敢声张...', '人际关系', '性骚扰', '研一', '现实方法', False, 'open'),
        (12, '同学之间互相攀比，很累', '同门之间总是在比较谁的文章多、谁的实习好，感觉氛围很不好...', '人际关系', '同辈压力', '研三', '情绪支持', True, 'open'),
        (9, '和导师沟通总被误解', '每次和导师讨论问题，TA似乎都理解不了我的意思，是不是我表达有问题？', '人际关系', '沟通障碍', '研一', '经验建议', True, 'open'),
        (4, '实验室小团体排挤我', '实验室有几个人形成了一个小团体，有事都不带我，感觉被排挤了...', '人际关系', '小团体', '研二', '情绪支持', False, 'open'),
        (5, '导师对我和对其他学生双重标准', '导师对同一个实验室的本地学生很宽松，对我和几个外校来的学生要求特别严格...', '人际关系', '不公平对待', '研一', '情绪支持', True, 'open'),
        (10, '和合作者产生了矛盾', '和其他实验室合作一个项目，但在作者排序和工作分工上产生了分歧...', '人际关系', '合作矛盾', '研二', '现实方法', False, 'open'),
        # 情绪与压力 (10)
        (6, '科研压力大，经常失眠，是不是该去看医生？', '最近一个月几乎每周都有两三天睡不着，躺在床上脑子里全是实验和数据...', '情绪与压力', '心理压力', '研二', '情绪支持', False, 'open'),
        (3, '博三了还没发文章，家里压力很大', '爸妈一直问我什么时候毕业，每次回家都很焦虑，不知道怎么和他们沟通...', '情绪与压力', '家庭压力', '博士', '情绪支持', True, 'open'),
        (6, '感觉自己什么都不如别人', '看着同门文章发了、实习找到了，自己却什么都没有，很自卑...', '情绪与压力', '自卑心理', '研二', '情绪支持', True, 'open'),
        (11, '实验反复失败，快抑郁了', '博一快结束了实验还没有正结果，每天在实验室都很煎熬，是不是该去看心理医生？', '情绪与压力', '科研抑郁', '博士', '情绪支持', False, 'open'),
        (3, '对科研完全失去了兴趣', '博二了，以前对研究还挺有兴趣的，现在看到论文就烦，是不是该退学？', '情绪与压力', '科研倦怠', '博士', '情绪支持', True, 'open'),
        (6, '父母不支持我读研，觉得浪费时间', '本科毕业时父母希望我直接工作，我说想考研他们很反对，现在读研了他们还经常说风凉话...', '情绪与压力', '家庭不支持', '研一', '情绪支持', False, 'open'),
        (12, '同龄人都已经工作结婚了，我很慌', '本科同学好多都工作了，还有结婚生孩子的，感觉自己还在上学很失败...', '情绪与压力', '同辈压力', '研三', '情绪支持', True, 'open'),
        (11, '博一博二浪费了太多时间', '博一博二没有完全投入到科研中，现在博三了感觉时间不够用，很后悔...', '情绪与压力', '时间焦虑', '博士', '情绪支持', True, 'open'),
        (6, '实验室没有人关心你的情绪', '每次在实验室表现出焦虑或低落，大家都会避开，感觉没有人情味...', '情绪与压力', '孤独感', '研二', '情绪支持', False, 'open'),
        (3, '博四了还没达到毕业要求', '博士读了四年，文章还不够，每次想到毕业就失眠，是不是该放弃了？', '情绪与压力', '延毕焦虑', '博士', '情绪支持', True, 'open'),
        # 生活适应 (10)
        (5, '跨专业考研上岸，现在跟不上课业怎么办', '本科是机械，考研跨到了计算机。现在上课听不懂，编程基础也差...', '生活适应', '跨专业适应', '研一', '经验建议', True, 'open'),
        (13, '研究生住宿条件太差了', '宿舍是老旧楼房，冬天冷夏天热，和本科时的住宿条件差太多了...', '生活适应', '住宿条件', '研一', '情绪支持', False, 'open'),
        (5, '不会用Linux和命令行，很慌', '本科用的Windows，现在实验室服务器都是Linux系统，完全不会用...', '生活适应', '技术适应', '研一', '经验建议', True, 'open'),
        (13, '研究生生活太单调了', '每天就是宿舍-实验室-食堂三点一线，感觉生活完全没有乐趣...', '生活适应', '生活单调', '研一', '情绪支持', True, 'open'),
        (9, '不会社交，研究生要不要交朋友？', '性格比较内向，本科时朋友就不多，研究生更不知道怎么和人交往了...', '生活适应', '社交困难', '研一', '情绪支持', True, 'open'),
        (5, '研究生补助太低了', '每个月只有几百块补助，生活很拮据，又要向家里要钱，感觉很不好意思...', '生活适应', '经济压力', '研一', '情绪支持', False, 'open'),
        (12, '研究生还要上课吗？感觉和本科没区别', '研一课上了一堆，和本科没什么区别，什么时候才能做自己的研究？', '生活适应', '课程压力', '研一', '经验建议', True, 'open'),
        (9, '导师要求打卡考勤，像上班一样', '导师要求每天早九晚十打卡，感觉完全没有研究生的自由...', '生活适应', '时间管理', '研一', '情绪支持', False, 'open'),
        (13, '研究生和本科生的生活方式差别太大', '本科时还有很多社团活动和朋友聚会，研究生后感觉完全是两个世界...', '生活适应', '生活方式改变', '研一', '情绪支持', True, 'open'),
        (5, '不会写学术论文，本科完全没训练过', '本科是工科，几乎没有写过学术论文，现在要写论文完全不知道从何下手...', '生活适应', '学术写作', '研一', '经验建议', True, 'open'),
        # 其他 (5)
        (1, '研究生要不要谈恋爱？', '研一了，感觉生活很单调，想谈恋爱但又怕影响科研，很纠结...', '其他', '感情问题', '研一', '经验建议', False, 'open'),
        (6, '家里经济困难，要不要辍学工作？', '家里突发变故，经济上需要我支持，但放弃研究生又很不甘心...', '其他', '经济困难', '研二', '现实方法', False, 'open'),
        (4, '研究生期间要不要考证书？', '看到很多同学在考CPA、司法考试等证书，我要不要也考一个增加竞争力？', '其他', '证书考试', '研一', '经验建议', True, 'open'),
        (8, '研究生期间能不能创业？', '有一个不错的创业想法，但导师肯定不支持，要不要瞒着导师去尝试？', '其他', '创业', '研二', '现实方法', False, 'open'),
        (11, '研究生期间身体垮了', '长期熬夜做实验，现在身体出现了很多问题，要不要休学养病？', '其他', '健康问题', '博士', '情绪支持', False, 'open'),
    ]

    questions = []
    for data in questions_data:
        user_id, title, content, category, subcategory, grade, response_type, allow_public, status = data
        q = Question(
            user_id=user_id, title=title, content=content,
            category=category, subcategory=subcategory,
            grade=grade, response_type=response_type,
            allow_public=allow_public, status=status,
        )
        db.session.add(q)
        questions.append(q)
    db.session.commit()

    # 给每个问题添加回复（确保经验库有足够数据）
    # 先定义一些通用回复模板
    reply_templates = [
        ('我经历过类似情况', '这个问题我也遇到过。建议你可以先和导师/同学沟通，说明你的困惑。很多时候别人也经历过类似的事情，你不是一个人。给自己一点时间，慢慢来。'),
        ('我提供一个现实建议', '建议你可以从以下几个方面考虑：1. 先了解清楚基本情况；2. 和信任的人聊聊；3. 制定一个可行的计划；4. 不要害怕求助。研究生阶段遇到困难是正常的，关键是要有解决问题的勇气。'),
        ('我只想给你一些支持', '我能理解你的感受，这种困惑和焦虑是很正常的。不要对自己太苛刻，给自己一点时间适应。如果需要倾诉，随时可以找人聊聊。你不是一个人在战斗。'),
        ('我有一些经验分享', '分享一下我的经验：当初我也是这样过来的。关键是不要放弃，保持积极的心态。可以多和师兄师姐交流，他们往往能给你很多有用的建议。加油！'),
        ('我提供一个不同视角', '换个角度想想：这个问题也许没有你想象的那么糟糕。有时候我们太陷入细节，反而看不到更大的画面。建议你可以暂时放下，过一段时间再回来看，也许会有新的启发。'),
    ]

    import random
    all_questions = Question.query.all()
    all_users = User.query.all()
    user_ids = [u.id for u in all_users]

    for q in all_questions:
        # 每个问题添加1-3条回复
        num_replies = random.randint(1, 3)
        for i in range(num_replies):
            uid = random.choice(user_ids)
            if uid == q.user_id:
                uid = random.choice([u.id for u in all_users if u.id != q.user_id]) or uid
            style, content = random.choice(reply_templates)
            r = Reply(
                question_id=q.id,
                user_id=uid,
                content=content,
                response_style=style,
                is_read=(i == 0),
                is_thanked=(i == 0 and random.random() > 0.5),
            )
            db.session.add(r)

    db.session.commit()

    # 经验库：确保每个分类 Tab 都有数据
    # 按类别查找已创建的问题，并取有回复的问题加入经验库
    exp_categories = ['导师与课题组', '科研与论文', '职业规划', '人际关系', '情绪与压力', '生活适应', '其他']
    all_questions = Question.query.all()
    all_replies = Reply.query.all()
    # 建立 question_id -> first_reply 的映射
    qid_to_reply = {}
    for r in all_replies:
        if r.question_id not in qid_to_reply:
            qid_to_reply[r.question_id] = r

    # 先按类别分组收集候选问题
    from collections import defaultdict
    cat_questions = defaultdict(list)
    for q in all_questions:
        if q.id in qid_to_reply:
            cat = q.category or '其他'
            cat_questions[cat].append(q)

    # 每个类别至少保留 6 条经验（确保每个 Tab 都有数据展示）
    for cat in exp_categories:
        candidates = cat_questions.get(cat, [])
        # 如果该类别不足 6 条，从"其他"类别补充
        if len(candidates) < 6:
            extra_needed = 6 - len(candidates)
            others = [q for q in cat_questions.get('其他', []) if q not in candidates]
            candidates = candidates + others[:extra_needed]

        # 每个类别最多取 15 条
        for q in candidates[:15]:
            if q.id in qid_to_reply:
                r = qid_to_reply[q.id]
                existing = Experience.query.filter_by(question_id=q.id).first()
                if not existing:
                    exp = Experience(question_id=q.id, reply_id=r.id, category=cat)
                    db.session.add(exp)

    db.session.commit()
    print("示例数据已创建")

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
