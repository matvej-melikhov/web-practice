from flask import render_template, request, redirect, url_for, session, flash, make_response
from flask_babel import Babel, _

from functools import wraps
from datetime import datetime
from flask import session, redirect, url_for

from . import app, db
from .models import User, Habit, HabitEntry


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_('You need to log in first!'), 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


FREQUENCY_MAPPING = {
    "daily": 1,
    "weekly": 2,
    "monthly": 3
}

@login_required
@app.route('/')
def index():
    if 'user_id' in session:
        order = request.args.get('order', 'asc')

        if order == 'desc':
            habits = Habit.query.filter_by(user_id=session['user_id']).all()
            habits = sorted(habits, key=lambda h: FREQUENCY_MAPPING[h.frequency], reverse=(order == 'desc'))
        else:
            habits = Habit.query.filter_by(user_id=session['user_id']).all()
            habits = sorted(habits, key=lambda h: FREQUENCY_MAPPING[h.frequency], reverse=(order == 'desc'))

        return render_template('index.html', habits=habits)
    return render_template('index.html')

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            flash(_('Passwords do not match!'), 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash(_('Username already exists!'), 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash(_('You have successfully registered!'), 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(_('Login successful!'), 'success')
            return redirect(url_for('index'))
        else:
            flash(_('Invalid username or password!'), 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash(_('You have been logged out!'), 'info')
    return redirect(url_for('login'))


# Добавить привычку
@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if 'user_id' not in session:
        flash(_('You need to log in first!'), 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        frequency = request.form['frequency']
        new_habit = Habit(name=name, frequency=frequency, user_id=session['user_id'])
        db.session.add(new_habit)
        db.session.commit()
        flash(_('Habit added successfully!'), 'success')
        return redirect(url_for('index'))

    return render_template('add_habit.html')

# Отметить выполнение привычки
@app.route('/mark_completed/<int:habit_id>', methods=['POST'])
def mark_completed(habit_id):
    if 'user_id' not in session:
        flash(_('You need to log in first!'), 'danger')
        return redirect(url_for('login'))

    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != session['user_id']:
        flash(_('Unauthorized access!'), 'danger')
        return redirect(url_for('index'))

    # Проверим, существует ли уже запись для этой привычки на сегодняшний день
    today = datetime.utcnow().date()  # Получаем текущую дату
    existing_entry = HabitEntry.query.filter_by(habit_id=habit_id, date=today).first()

    if existing_entry:
        flash(_('You already marked this habit as completed today.'), 'info')
    else:
        # Если записи нет, создаем новую
        habit_entry = HabitEntry(habit_id=habit_id, date=today, completed=True)
        db.session.add(habit_entry)
        db.session.commit()
        flash(_('Habit marked as completed!'), 'success')

    return redirect(url_for('index'))


@app.route('/habit/<int:habit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    # Убедимся, что только владелец привычки может редактировать её
    if habit.user_id != session['user_id']:
        flash(_('You cannot edit another user\'s habit!'), 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        habit.name = request.form['name']
        habit.frequency = request.form['frequency']
        db.session.commit()
        flash(_('Habit updated successfully!'), 'success')
        return redirect(url_for('index'))

    return render_template('edit_habit.html', habit=habit)


@app.route('/habit/<int:habit_id>/delete', methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    # Убедимся, что только владелец привычки может удалить её
    if habit.user_id != session['user_id']:
        flash(_('You cannot delete another user\'s habit!'), 'danger')
        return redirect(url_for('index'))

    db.session.delete(habit)
    db.session.commit()

    return {'status': 'success', 'habit_id': habit_id}



@app.route('/set_language/<lang>')
def set_language(lang):
    response = make_response(redirect(url_for('index')))  # Перенаправляем на главную страницу
    response.set_cookie('lang', lang)  # Устанавливаем язык в куки
    return response