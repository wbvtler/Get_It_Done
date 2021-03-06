from flask import Flask, request, redirect
from flask import render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-done:SnappyT5@localhost:8889/get-done'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'asdfasdfasdf'

class Task(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(45), unique=True)
    password = db.Column(db.String(45))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password
        

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            # "remember" that the user has logged in
            session['email'] = email
            flash('logged in')
            print(session)
            return redirect('/')
        else:
            #TODO - explain why login failed
            flash('User password incorrect, or user does not exist', 'error')
            return redirect('/')

    return render_template('login.html')


@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            # "remember" the user
            session['email'] = email
            
            return redirect('/')
        else:
            # TODO - user bertter response messaging
            return "<h1 style='font-family:Sans-serif'>No, you bum nugget, that's a duplicate user</h1>"

    return render_template('register.html')

@app.before_request
def require_login():
    allowed_routs = ['login', 'register']
    if request.endpoint not in allowed_routs and 'email' not in session:
        return redirect('/login')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route("/", methods=['POST', 'GET'])
def index():
    
    owner = User.query.filter_by(email=session['email']).first()
        
    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()

    return render_template('getitdone.html', title="Get it Done!", tasks=tasks, completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()