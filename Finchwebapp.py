from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #3 slashes is relative path, 4 is definite path
db = SQLAlchemy(app)

'''
class ClassName(object):
	"""docstring for ClassName"""
	def __init__(self, arg):
		super(ClassName, self).__init__()
		self.arg = arg

		'''
		
class FinchApp(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	content = db.Column(db.String(200), nullable=False)
	completed = db.Column(db.Integer, default=0)
	date_created = db.Column(db.DateTime, default = datetime.utcnow)

	def __repr__(self):
		return '<Task %r>' % self.id 


@app.route('/', methods =  ['POST', 'GET'])

def index():
	if request.method == "POST":
		task_content = request.form['content']
		print(task_content)
		new_task = FinchApp(content=task_content)

		try:
			db.session.add(new_task)
			db.session.commit()
			return redirect('/')
		except:
			return "Cannot Process Request"


		#return 'See below for employee data'
	else:
		tasks = FinchApp.query.order_by(FinchApp.date_created).all()
		print(tasks)
		return render_template('index.html', tasks = tasks)

@app.route('/delete/<int:id>')

def delete(id):
	task_to_delete = FinchApp.query.get_or_404(id)
	print(task_to_delete)
	try:
		db.session.delete(task_to_delete)
		db.session.commit()
		return redirect('/')
	except:
		return "There was a problem deleting that object"

@app.route('/update/<int:id>', methods =  ['POST', 'GET'])
def update(id):
	task =FinchApp.query.get_or_404(id)

	if request.method == 'POST':
		task.content = request.form['content']
		try: 
			db.session.commit()
			return redirect('/')
		except:
			return "Error with Update"
	else:
		return render_template('update.html', task = task)
	

if __name__=="__main__":
	app.run(debug= True)