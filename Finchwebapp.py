from flask import Flask, render_template, url_for, request, redirect
import json
import requests

app = Flask(__name__)

#list of valid providers
providers = ['gusto', 'workday', 'justworks', 'bamboohr', 'paychex_flex']
provider = ''
#global access token
access_token = ''

#define endpoints
directory_endpoint = "https://finch-sandbox-se-interview.vercel.app/api/employer/directory"
individual_endpoint = "https://finch-sandbox-se-interview.vercel.app/api/employer/individual"
employment_endpoint = "https://finch-sandbox-se-interview.vercel.app/api/employer/employment"

#define headers
request_headers={'Authorization': 'Bearer '+ access_token, 'Content-Type': 'application/json'}

@app.route('/', methods =  ['POST', 'GET'])
def index():
	if request.method == "POST":
		global provider 
		provider = request.form['content']

		if provider in providers:	
			
			return get_employees(provider)

		else:
			return "Provider not found"
	else:		
		return render_template('index.html')

# helper function to display employees in given provider
def get_employees(provider):
	url = "https://finch-sandbox-se-interview.vercel.app/api/sandbox/create"

	payload={'provider': provider, 'products': ['company', 'directory', 'individual', 'employment', 'payment', 'pay_statement']}
	header = {'Content-Type': 'application/json'}
	global access_token
	global directory_endpoint
	global request_headers

	#first must request sandbox access token
	response = requests.post(url, headers=header, json=payload)

	#convert response to json dictionary object
	json_dict = response.json()
	
	#get access token
	access_token = response.json().get('access_token')

	#update request headers
	request_headers={'Authorization': 'Bearer '+ access_token, 'Content-Type': 'application/json'}
	
	#get full directory from provider
	request = requests.get(directory_endpoint, headers = request_headers)

	#get array of individuals
	employees = request.json().get('individuals')
	
	return render_template('directory.html', list = employees)

	

# route for individual employee data
@app.route('/individual/<emp_id>', methods =  ['POST', 'GET'])
def get_employee_data(emp_id):

	global provider
	global individual_endpoint
	global access_token
	if request.method == "POST":
		
		provider = request.form['content']
	
		if provider in providers:

			return get_employees(provider)

		else:
			return "Provider not found"


	#get individual employee data
	else:
		request_headers={'Authorization': 'Bearer '+ access_token, 'Content-Type': 'application/json'}
		ind_json = {'requests': [{'individual_id': emp_id}]}

		individual_response = requests.post(individual_endpoint, headers = request_headers, json = ind_json)

		ind_data = individual_response.json().get('responses')[0].get('body')
				
		return render_template('individual.html', data = ind_data)

#route for employment data for an individual employee
@app.route('/employment/<emp_id>', methods =  ['POST', 'GET'])
def get_employment_data(emp_id):

	global provider
	global employment_endpoint
	global access_token
	global request_headers
	if request.method == "POST":
		provider = request.form['content']
		if provider in providers:
			return get_employees(provider)
		else:
			return "Provider not found"


	#See below for employment data
	else:
		request_headers={'Authorization': 'Bearer '+ access_token, 'Content-Type': 'application/json'}

		ind_json = {'requests': [{'individual_id': emp_id}]}
		individual_response = requests.post(employment_endpoint, headers = request_headers, json = ind_json)

		ind_data = individual_response.json().get('responses')[0].get('body')
				
		return render_template('employment.html', data = ind_data)


#helper function to get managers from directory displayed in directory.html
@app.context_processor
def utility_processor():
	def get_manager(manager_id):
		if manager_id is None:
			return 'None'
		else:
			url = "https://finch-sandbox-se-interview.vercel.app/api/sandbox/create"
			global provider
			global request_headers
			global access_token
			global individual_endpoint
			manager_id = manager_id.get('id')
		
			request_headers={'Authorization': 'Bearer '+ access_token, 'Content-Type': 'application/json'}
			ind_json = {'requests': [{'individual_id': manager_id}]}

			individual_response = requests.post(individual_endpoint, headers = request_headers, json = ind_json)

			ind_data = individual_response.json().get('responses')[0].get('body')

			name = ind_data.get('first_name') + ' '+ ind_data.get('last_name')

			return name
	return dict(get_manager=get_manager)
		


if __name__=="__main__":
	app.run(debug= True)