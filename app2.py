import openai
import re
import json

from random import randint
from flask import Flask,session, request, send_file,jsonify, render_template, make_response,url_for,redirect
from pymongo import MongoClient
from bson import ObjectId
from io import BytesIO
from PyPDF2 import PdfReader
import spacy
from bs4 import BeautifulSoup
from flask_mail import Mail, Message
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import request




app = Flask(__name__)


app.config['MAIL_SERVER'] = '64.233.184.108'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'prakruthi.1dt19is095@gmail.com'  # Your Gmail email address
app.config['MAIL_PASSWORD'] = 'kpsj cefg xhsg bxux'  
app.config['MAIL_DEFAULT_SENDER'] = ('Innoventures', 'prakruthi.1dt19is095@gmail.com')
mail = Mail(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['hrabc']  # Change 'candidate_database' to your desired database name
candidates_collection = db['candidates']
recruiters_collection = db['recruiters']

openai.api_key = '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'
nlp = spacy.load("en_core_web_sm")

from flask import request

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verify user against recruiters collection
        user = recruiters_collection.find_one({"username": username, "password": password})

        if user:
            # Login successful, redirect to the index page
            
            return render_template('index.html')
        else:
            # Login failed, display an error message
            return render_template('login.html', error_message='Invalid credentials')

    return render_template('login.html')
"""def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verify user against recruiters collection
        user = recruiters_collection.find_one({"username": username, "password": password})

        if user:
            # Login successful, redirect to the index page
            return render_template('index.html')
        else:
            # Login failed, display an error message
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')"""


    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the passwords match
        if password != confirm_password:
            return render_template('signup.html', error_message='Passwords do not match')

        # Check if the username is already taken
        existing_user = recruiters_collection.find_one({"username": username})
        if existing_user:
            return render_template('signup.html', error_message='Username already taken')
        

        # Create a new user in the recruiters collection
        recruiters_collection.insert_one({"username": username, "password": password})
        return render_template('signup.html', success_message='User signed up successfully')

        # Redirect to the login page after successful signup
        return render_template('login.html')

    return render_template('signup.html')








"chart"

"old"

"""def calculate_match_percentage(candidate, search_parts):
    if not search_parts:
        return 0, None  # Return 0 match percentage and None for no match

    total_conditions = sum(':' in part for part in search_parts)
    satisfied_conditions = 0

    matched_key_value = None  # Initialize to None, will be updated if there's a match

    print(f"Total Conditions: {total_conditions}")

    for part in search_parts:
        if ':' in part:
            key, value = part.split(':', 1)
            value_pattern = re.compile(r'\b{}\b'.format(re.escape(value)), re.IGNORECASE)

            if key in candidate:
                if isinstance(candidate[key], list):
                    for item in candidate[key]:
                        if value_pattern.search(str(item)):
                            satisfied_conditions += 1
                            matched_key_value = {key: item}  # Update matched key-value pair
                            break
                elif value_pattern.search(str(candidate[key])):
                    satisfied_conditions += 1
                    matched_key_value = {key: candidate[key]}  # Update matched key-value pair

    print(f"Satisfied Conditions: {satisfied_conditions}")

    # Ensure match percentage is at least 0 and at most 100
    match_percentage = min(round((satisfied_conditions / total_conditions) * 100, 2), 100)

    print(f"Match Percentage: {match_percentage}")

    return match_percentage, matched_key_value"""





"""@app.route('/index')
def index():
    # Get the search keyword from the query parameters
    search_query = request.args.get('search', '')

    # Perform a search query in MongoDB
    if search_query:
        # Check if the search query is for "name" or "email" directly
        if ":" not in search_query.lower():
            # Construct a MongoDB query using case-insensitive regex patterns for name and email
            name_condition = {"name": {"$regex": re.compile(r'\b{}\b'.format(re.escape(search_query)), re.IGNORECASE)}}
            email_condition = {"email": {"$regex": re.compile(r'\b{}\b'.format(re.escape(search_query)), re.IGNORECASE)}}

            # Combine the conditions using the "$or" operator
            query_dict = {"$or": [name_condition, email_condition]}
        else:
            # Split the search query into key-value pairs
            search_parts = search_query.split(',')

            # Initialize search_parts as an empty list
            or_conditions = []
            and_conditions = []

            current_conditions = None

            for part in search_parts:
                if ':' in part:
                    key, value = part.split(':')

                    # Constructing a case-insensitive regex pattern for the whole word
                    value_pattern = re.compile(r'\b{}\b'.format(re.escape(value)), re.IGNORECASE)

                    # Adding the key-value pair to the appropriate conditions list
                    if current_conditions is not None:
                        current_conditions.append({key: {"$regex": value_pattern}})
                    else:
                        or_conditions.append({key: {"$regex": value_pattern}})
                elif part.lower() == 'or':
                    # Switch to 'or' conditions list
                    current_conditions = or_conditions
                elif part.lower() == 'and':
                    # Switch to 'and' conditions list
                    current_conditions = and_conditions

            # Combine the conditions lists using the provided operators
            query_dict = {}
            if or_conditions:
                query_dict["$or"] = or_conditions
            if and_conditions:
                query_dict["$and"] = and_conditions

        # If there is a search query, perform a search based on the regex patterns
        candidates_cursor = candidates_collection.find(query_dict)

        # Calculate match percentage and matched key-value for each candidate
        match_info = []
        for candidate in candidates_cursor:
            # Pass an empty list if ':' is not in search_query
            percentage, matched_key_value = calculate_match_percentage(candidate, search_parts if ":" in search_query.lower() else [])
            match_info.append((candidate, percentage, matched_key_value))
            
            # Print matched key-value for debugging
            print(f"Matched Key-Value for {candidate['_id']}: {matched_key_value}")

        # Sort candidates by match percentage in descending order
        sorted_candidates = sorted(match_info, key=lambda x: x[1], reverse=True)

        # Extract candidates for rendering
        candidates_for_rendering = [info[0] for info in sorted_candidates]

        # Prepare a list of tuples (candidate, match_percentage, matched_key_value) for rendering
        candidates_with_info = [
            (candidate, percentage, matched_key_value) for candidate, percentage, matched_key_value in zip(
                candidates_for_rendering, [info[1] for info in sorted_candidates], [info[2] for info in sorted_candidates]
            )
        ]
    else:
        # If there is no search query, retrieve all candidates
        candidates_cursor = candidates_collection.find()

        # Render the template with all candidates and no search keyword
        candidates_with_info = [(candidate, 0, None) for candidate in candidates_cursor]

    # Render the template with the sorted candidates and search keyword
    return render_template('index.html', candidates=candidates_with_info, search_keyword=search_query)"""



def calculate_match_percentage(candidate, search_parts):
    if not search_parts:
        return 0, None  # Return 0 match percentage and None for no match

    total_conditions = sum(':' in part for part in search_parts)
    satisfied_conditions = 0

    matched_values = []  # Initialize to an empty list, will be updated if there's a match

    print(f"Total Conditions: {total_conditions}")

    # Extract search values
    search_values = [part.split(':')[1].strip() for part in search_parts if ':' in part]

    for part in search_parts:
        if ':' in part:
            key, value = part.split(':', 1)
            value_pattern = re.compile(r'\b{}\b'.format(re.escape(value)), re.IGNORECASE)

            if key in candidate:
                if isinstance(candidate[key], list):
                    for item in candidate[key]:
                        if value_pattern.search(str(item)):
                            satisfied_conditions += 1
                            matched_values.append(item)  # Update matched values
                            break
                elif value_pattern.search(str(candidate[key])):
                    satisfied_conditions += 1
                    matched_values.append(candidate[key])  # Update matched values

    print(f"Satisfied Conditions: {satisfied_conditions}")

    # Ensure match percentage is at least 0 and at most 100
    match_percentage = min(round((satisfied_conditions / total_conditions) * 100, 2), 100)

    # Filter out values not present in search_values
    #matched_values = [value for value in matched_values if any(search_value.lower() == value.lower() for search_value in search_values)]
    
    print(f"Search values:{search_values}")
    print(f"Match Percentage: {match_percentage}")
    print(f"Matched Values for {candidate['name']}: {matched_values}")
    print()

    return match_percentage, matched_values

@app.route('/index')
def index():
    # Get the search keyword from the query parameters
    search_query = request.args.get('search', '')

    # Perform a search query in MongoDB
    if search_query:
        # Check if the search query is for "name" or "email" directly
        if ":" not in search_query.lower():
            # Construct a MongoDB query using case-insensitive regex patterns for name and email
            name_condition = {"name": {"$regex": re.compile(r'\b{}\b'.format(re.escape(search_query)), re.IGNORECASE)}}
            email_condition = {"email": {"$regex": re.compile(r'\b{}\b'.format(re.escape(search_query)), re.IGNORECASE)}}

            # Combine the conditions using the "$or" operator
            query_dict = {"$or": [name_condition, email_condition]}
        else:
            # Split the search query into key-value pairs
            search_parts = search_query.split(',')

            # Initialize search_parts as an empty list
            or_conditions = []
            and_conditions = []

            current_conditions = None

            for part in search_parts:
                if ':' in part:
                    key, value = part.split(':')

                    # Constructing a case-insensitive regex pattern for the whole word
                    value_pattern = re.compile(r'\b{}\b'.format(re.escape(value)), re.IGNORECASE)

                    # Adding the key-value pair to the appropriate conditions list
                    if current_conditions is not None:
                        current_conditions.append({key: {"$regex": value_pattern}})
                    else:
                        or_conditions.append({key: {"$regex": value_pattern}})
                elif part.lower() == 'or':
                    # Switch to 'or' conditions list
                    current_conditions = or_conditions
                elif part.lower() == 'and':
                    # Switch to 'and' conditions list
                    current_conditions = and_conditions

            # Combine the conditions lists using the provided operators
            query_dict = {}
            if or_conditions:
                query_dict["$or"] = or_conditions
            if and_conditions:
                query_dict["$and"] = and_conditions

        # If there is a search query, perform a search based on the regex patterns
        candidates_cursor = candidates_collection.find(query_dict)

        # Calculate match percentage and matched key-value for each candidate
        match_info = []
        for candidate in candidates_cursor:
            # Pass an empty list if ':' is not in search_query
            percentage, matched_values = calculate_match_percentage(candidate, search_parts if ":" in search_query.lower() else [])
            matched_values_json = json.dumps(matched_values)
            match_info.append((candidate, percentage, matched_values_json))

            # Print matched key-value for debugging
            print(f"Matched Values for {candidate['_id']}: {matched_values}")

        # Sort candidates by match percentage in descending order
        sorted_candidates = sorted(match_info, key=lambda x: x[1], reverse=True)

        # Extract candidates for rendering
        candidates_for_rendering = [info[0] for info in sorted_candidates]

        # Prepare a list of tuples (candidate, match_percentage, matched_values) for rendering
        candidates_with_info = [
            (candidate, percentage, matched_values) for candidate, percentage, matched_values in zip(
                candidates_for_rendering, [info[1] for info in sorted_candidates], [info[2] for info in sorted_candidates]
            )
        ]
    else:
        # If there is no search query, retrieve all candidates
        candidates_cursor = candidates_collection.find()

        # Render the template with all candidates and no search keyword
        candidates_with_info = [(candidate, 0, None) for candidate in candidates_cursor]

    # Render the template with the sorted candidates and search keyword
    return render_template('index.html', candidates=candidates_with_info, search_keyword=search_query)



"""@app.route('/index')
def index():
    # Get the search keyword from the query parameters
    search_query = request.args.get('search', '')

    # Perform a search query in MongoDB
    if search_query:
        # Check if the search query is for "name" or "email" directly
        if ":" not in search_query.lower():
            # Construct a MongoDB query using case-insensitive regex patterns for name and email
            name_condition = {"name": {"$regex": re.compile(r'\b{}\b'.format(re.escape(search_query)), re.IGNORECASE)}}
            email_condition = {"email": {"$regex": re.compile(r'\b{}\b'.format(re.escape(search_query)), re.IGNORECASE)}}

            # Combine the conditions using the "$or" operator
            query_dict = {"$or": [name_condition, email_condition]}
        else:
            # Split the search query into key-value pairs
            search_parts = search_query.split(',')

            # Initialize search_parts as an empty list
            or_conditions = []
            and_conditions = []

            current_conditions = None

            for part in search_parts:
                if ':' in part:
                    key, value = part.split(':')

                    # Constructing a case-insensitive regex pattern for the whole word
                    value_pattern = re.compile(r'\b{}\b'.format(re.escape(value)), re.IGNORECASE)

                    # Adding the key-value pair to the appropriate conditions list
                    if current_conditions is not None:
                        current_conditions.append({key: {"$regex": value_pattern}})
                    else:
                        or_conditions.append({key: {"$regex": value_pattern}})
                elif part.lower() == 'or':
                    # Switch to 'or' conditions list
                    current_conditions = or_conditions
                elif part.lower() == 'and':
                    # Switch to 'and' conditions list
                    current_conditions = and_conditions

            # Combine the conditions lists using the provided operators
            query_dict = {}
            if or_conditions:
                query_dict["$or"] = or_conditions
            if and_conditions:
                query_dict["$and"] = and_conditions

        # If there is a search query, perform a search based on the regex patterns
        candidates_cursor = candidates_collection.find(query_dict)

        # Calculate match percentage and matched key-value for each candidate
        match_info = []
        for candidate in candidates_cursor:
            # Pass an empty list if ':' is not in search_query
            search_values = [part.split(':')[1] for part in search_parts if ':' in part]
            percentage, matched_key_value = calculate_match_percentage(candidate, search_parts if ":" in search_query.lower() else [])
            match_info.append((candidate, percentage, matched_key_value))
            candidates_collection.update_one(
        {"_id": candidate["_id"]},
        {"$set": {"matched_keywords": matched_key_value}}  # Set the field to the matched keywords directly
    )
            # Print matched key-value for debugging
        # Sort candidates by match percentage in descending order
        sorted_candidates = sorted(match_info, key=lambda x: x[1], reverse=True)

        # Extract candidates for rendering
        candidates_for_rendering = [info[0] for info in sorted_candidates]

        # Prepare a list of tuples (candidate, match_percentage, matched_key_value) for rendering
        candidates_with_info = [
            (candidate, percentage, matched_key_value) for candidate, percentage, matched_key_value in zip(
                candidates_for_rendering, [info[1] for info in sorted_candidates], [info[2] for info in sorted_candidates]
            )
        ]
    else:
        # If there is no search query, retrieve all candidates
        candidates_cursor = candidates_collection.find()

        # Render the template with all candidates and no search keyword
        candidates_with_info = [(candidate, 0, None) for candidate in candidates_cursor]

    # Render the template with the sorted candidates and search keyword
    return render_template('index.html', candidates=candidates_with_info, search_keyword=search_query)"""








@app.route('/candidate/<candidate_id>')
def candidate_details(candidate_id):
    # Assuming candidates_collection is your MongoDB collection
    candidate = candidates_collection.find_one({'_id': ObjectId(candidate_id)})

    if candidate:
        return render_template('candidate_details.html', candidate=candidate)
    else:
        # Handle the case where the candidate with the given ID is not found
        return render_template('candidate_not_found.html')


@app.route('/addcandidate')
def page1():
    return render_template('page1.html')


@app.route('/removecandidate')
def page2():
    return render_template('page2.html')




import re

def extract_name(response_text):
    name_pattern = re.compile(r"1\. Name:\s*([\s\S]+?)\n", re.IGNORECASE)
    name_match = name_pattern.search(response_text)
    name = ' '.join([line.strip() for line in name_match.group(1).split('\n') if line.strip()]) if name_match else ''
    return name

def extract_email(response_text):
    email_pattern = re.compile(r"2\. Email:\s*([\s\S]+?)\n", re.IGNORECASE)
    email_match = email_pattern.search(response_text)
    email = ' '.join([line.strip() for line in email_match.group(1).split('\n') if line.strip()]) if email_match else ''
    return email



def extract_education(response_text):
    education_pattern = re.compile(r"3\. Education:(.*?)(?=(4\. Skills:|5\. Location:|6\. Experience:|7\. Contact:|8\. Certifications:|$))", re.DOTALL)
    education_match = education_pattern.search(response_text)
    education_section = education_match.group(1).strip() if education_match else ""
    
    # Combine education lines
    education_lines = [line.strip() for line in education_section.split('\n') if line.strip()]
    return education_lines

"""def extract_skills(response_text):
    skills_pattern = re.compile(r"4\. Skills:(.*?)(?=(5\. Location:|6\. Experience:|7\. Contact:|8\. Certifications:|$))", re.DOTALL)
    skills_match = skills_pattern.search(response_text)
    skills_section = skills_match.group(1).strip() if skills_match else ""
    skills_lines = [line.strip() for line in skills_section.split('\n') if line.strip()]
    return skills_lines"""

def extract_skills(response_text):
    skills_pattern = re.compile(r"4\. Skills:(.*?)(?=(5\. Location:|6\. Experience:|7\. Contact:|8\. Certifications:|$))", re.DOTALL)
    skills_match = skills_pattern.search(response_text)
    skills_section = skills_match.group(1).strip() if skills_match else ""
    # Split skills using both commas and new lines as delimiters
    skills_lines = [line.strip() for line in re.split(r'[,\n]', skills_section) if line.strip()]
    return skills_lines

def extract_location(response_text):
    location_pattern = re.compile(r"5\. Location:(.*?)(?=(6\. Experience:|7\. Contact:|8\. Certifications:|$))", re.DOTALL)
    location_match = location_pattern.search(response_text)
    location_section = location_match.group(1).strip() if location_match else ""
    location_lines = [line.strip() for line in location_section.split('\n') if line.strip()]
    return location_lines

def extract_experience(response_text):
    experience_pattern = re.compile(r"6\. Experience:(.*?)(?=(7\. Contact:|8\. Certifications:|$))", re.DOTALL)
    experience_match = experience_pattern.search(response_text)
    experience_section = experience_match.group(1).strip() if experience_match else ""
    experience_lines = [line.strip() for line in experience_section.split('\n') if line.strip()]
    return experience_lines

def extract_contact(response_text):
    contact_pattern = re.compile(r"7\. Contact:(.*?)(?=(8\. Certifications:|$))", re.DOTALL)
    contact_match = contact_pattern.search(response_text)
    contact_section = contact_match.group(1).strip() if contact_match else ""
    contact_lines = [line.strip() for line in contact_section.split('\n') if line.strip()]
    return contact_lines

def extract_certification(response_text):
    certification_pattern = re.compile(r"8\. Certifications:(.*?$)", re.DOTALL)
    certification_match = certification_pattern.search(response_text)
    certification_section = certification_match.group(1).strip() if certification_match else ""
    certification_lines = [line.strip() for line in certification_section.split('\n') if line.strip()]
    return certification_lines


"""@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get the uploaded file content directly from memory
        file_content = request.files['document'].read()

        # Extract text from the PDF
        pdf_text = extract_text_from_pdf(file_content)
        if not pdf_text:
            return render_template('index.html', message='Please Upload correct pdf')

        # Use OpenAI ChatCompletion to process the resume text
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant to provide key value structured info with the same format for all uploaded files. Follow the format: 1. Name, 2. Email, 3. Education, 4. Skills, 5. Location, 6. Experience, 7. Contact, 8. Certifications."},
                {"role": "user", "content": f"Parse the following resume for generating tags on 1. Name, 2. Email, 3. Education, 4. Skills, 5. Location, 6. Experience, 7. Contact, 8. Certifications. {pdf_text}"}
            ],
            max_tokens=4096,
        )

        # Extract key information from the model's response
        parsed_resume = response['choices'][0]['message']['content']

        # Extract information from each section
        education_info = extract_education(parsed_resume)
        skills_info = extract_skills(parsed_resume)
        location_info = extract_location(parsed_resume)
        experience_info = extract_experience(parsed_resume)
        contact_info = extract_contact(parsed_resume)
        certification_info = extract_certification(parsed_resume)
        name = extract_name(parsed_resume)
        email = extract_email(parsed_resume)

        # Calculate the time difference
        upload_date = datetime.now().date()  # Get the current date without the time
        upload_date_str = upload_date.strftime("%d-%m-%Y")  # Convert date to string in "dd-mm-yyyy" format
        upload_datetime = datetime.now()
# Store name, email, and date information separately in MongoDB
        existing_candidate = candidates_collection.find_one({'email': email})

        if existing_candidate:
            return render_template('index.html', message='Candidate already exists!')

        # Store original text, education, skills, location, experience, contact, certification, and date information
        candidate_object = {
            "name": name,
            "email": email,
            "original_resume_text": file_content,
            "education": education_info,
            "skills": skills_info,
            "location": location_info,
            "experience": experience_info,
            "contact": contact_info,
            "certification": certification_info,
            "upload_date": upload_date_str,
            "upload_datetime": upload_datetime
        }
        candidates_collection.insert_one(candidate_object)

        return redirect(url_for('index'))
    except Exception as e:
        return f"Error: {str(e)}"""

@app.route('/upload', methods=['POST'])
def upload():
    try:
        uploaded_files = request.files.getlist('document[]')

        for uploaded_file in uploaded_files:
            # Get the uploaded file content directly from memory
            file_content = uploaded_file.read()

            # Extract text from the PDF
            pdf_text = extract_text_from_pdf(file_content)
            
            # Use OpenAI ChatCompletion to process the resume text
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant to provide key value structured info with the same format for all uploaded files. Follow the format: 1. Name, 2. Email, 3. Education, 4. Skills, 5. Location, 6. Experience, 7. Contact, 8. Certifications."},
                    {"role": "user", "content": f"Parse the following resume for generating tags on 1. Name, 2. Email, 3. Education, 4. Skills, 5. Location, 6. Experience, 7. Contact, 8. Certifications. {pdf_text}"}
                ],
                max_tokens=4096,
            )

            # Extract key information from the model's response
            parsed_resume = response['choices'][0]['message']['content']

            # Extract information from each section
            education_info = extract_education(parsed_resume)
            skills_info = extract_skills(parsed_resume)
            location_info = extract_location(parsed_resume)
            experience_info = extract_experience(parsed_resume)
            contact_info = extract_contact(parsed_resume)
            certification_info = extract_certification(parsed_resume)
            name = extract_name(parsed_resume)
            email = extract_email(parsed_resume)

            # Calculate the time difference
            upload_date = datetime.now().date()  # Get the current date without the time
            upload_date_str = upload_date.strftime("%d-%m-%Y")  # Convert date to string in "dd-mm-yyyy" format
            upload_datetime = datetime.now()

            # Store name, email, and date information separately in MongoDB
            existing_candidate = candidates_collection.find_one({'email': email})

            if existing_candidate:
                return render_template('index.html', message='Candidate already exists!')

            # Store original text, education, skills, location, experience, contact, certification, and date information
            candidate_object = {
                "name": name,
                "email": email,
                "original_resume_text": file_content,
                "education": education_info,
                "skills": skills_info,
                "location": location_info,
                "experience": experience_info,
                "contact": contact_info,
                "certification": certification_info,
                "upload_date": upload_date_str,
                "upload_datetime": upload_datetime
            }
            candidates_collection.insert_one(candidate_object)

        return redirect(url_for('index'))

    except Exception as e:
        return render_template('index.html', message=f"Error: {str(e)}")

def extract_text_from_pdf(pdf_content):
    pdf_document = BytesIO(pdf_content)
    try:
        pdf_reader = PdfReader(pdf_document)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")




# Inside your update_candidate route
"""@app.route('/update-candidate/<candidate_id>', methods=['POST'])
def update_candidate(candidate_id):
    if request.method == 'POST':
        try:
            # Retrieve the existing candidate from MongoDB
            existing_candidate = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
            if not existing_candidate:
                return render_template('index.html', message='Candidate not found!')

            # Get the uploaded file content directly from memory
            new_file_content = request.files['document'].read()

            # Extract text from the new PDF
            new_pdf_text = extract_text_from_pdf(new_file_content)
            if not new_pdf_text:
                return render_template('index.html', message='Please upload a correct PDF')

            # Use OpenAI ChatCompletion to process the new resume text
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": "Your system message here."},
                    {"role": "user", "content": f"Parse the following resume for generating tags on 1. Name, 2. Email, 3. Education, 4. Skills, 5. Location, 6. Experience, 7. Contact, 8. Certifications. {new_pdf_text}"}
                ],
                max_tokens=4096,
            )

            # Extract key information from the model's response for the new resume
            parsed_new_resume = response['choices'][0]['message']['content']

            # Extract name and email from the parsed resume
            new_name = extract_name(parsed_new_resume)
            new_email = extract_email(parsed_new_resume)

            # Check if the names are the same before updating the full information
            if existing_candidate['name'] == new_name:
                # Update the full candidate information with the new data
                existing_candidate['name'] = new_name
                existing_candidate['email'] = new_email
                existing_candidate['original_resume_text'] = new_file_content
                existing_candidate['education'] = extract_education(parsed_new_resume)
                existing_candidate['skills'] = extract_skills(parsed_new_resume)
                existing_candidate['location'] = extract_location(parsed_new_resume)
                existing_candidate['experience'] = extract_experience(parsed_new_resume)
                existing_candidate['contact'] = extract_contact(parsed_new_resume)
                existing_candidate['certification'] = extract_certification(parsed_new_resume)

                # Update the candidate in MongoDB
                candidates_collection.update_one({'_id': ObjectId(candidate_id)}, {'$set': existing_candidate})

                return redirect(url_for('index'))
            else:
                return render_template('index.html', message='Names do not match. Cannot update information.')

        except Exception as e:
            return render_template('index.html', message=f"Error: {str(e)}")

    return render_template('index.html')  # Render a template or redirect as needed"""




@app.route('/update-candidate/<candidate_id>', methods=['POST'])
def update_candidate(candidate_id):
    if request.method == 'POST':
        try:
            # Retrieve the existing candidate from MongoDB
            existing_candidate = candidates_collection.find_one({'_id': ObjectId(candidate_id)})
            if not existing_candidate:
                return render_template('index.html', message='Candidate not found!')

            # Get the uploaded file content directly from memory
            new_file_content = request.files['document'].read()

            # Extract text from the new PDF
            new_pdf_text = extract_text_from_pdf(new_file_content)
            if not new_pdf_text:
                return render_template('index.html', message='Please upload a correct PDF')

            # Use OpenAI ChatCompletion to process the new resume text
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": "Your system message here."},
                    {"role": "user", "content": f"Parse the following resume for generating tags on 1. Name, 2. Email, 3. Education, 4. Skills, 5. Location, 6. Experience, 7. Contact, 8. Certifications. {new_pdf_text}"}
                ],
                max_tokens=4096,
            )

            # Extract key information from the model's response for the new resume
            parsed_new_resume = response['choices'][0]['message']['content']

            # Extract name and email from the parsed resume
            new_name = extract_name(parsed_new_resume)
            new_email = extract_email(parsed_new_resume)
            new_upload_date = datetime.now().date()  # Get the current date without the time
            new_upload_date_str = new_upload_date.strftime("%d-%m-%Y")  # Convert date to string in "dd-mm-yyyy" format
            new_upload_datetime = datetime.now()
            # Check if the names are the same before updating the full information
            if existing_candidate['name'] == new_name:
                # Update the full candidate information with the new data
                existing_candidate['name'] = new_name
                existing_candidate['email'] = new_email
                existing_candidate['original_resume_text'] = new_file_content
                existing_candidate['education'] = extract_education(parsed_new_resume)
                existing_candidate['skills'] = extract_skills(parsed_new_resume)
                existing_candidate['location'] = extract_location(parsed_new_resume)
                existing_candidate['experience'] = extract_experience(parsed_new_resume)
                existing_candidate['contact'] = extract_contact(parsed_new_resume)
                existing_candidate['certification'] = extract_certification(parsed_new_resume)
                existing_candidate['upload_date'] =  new_upload_date_str
                existing_candidate['upload_datetime'] = new_upload_datetime
                
                # Update the candidate in MongoDB
                candidates_collection.update_one({'_id': ObjectId(candidate_id)}, {'$set': existing_candidate})

                return redirect(url_for('index'))
            else:
                return render_template('index.html', message='Names do not match. Cannot update information.')

        except Exception as e:
            return render_template('index.html', message=f"Error: {str(e)}")

    return render_template('index.html')  # Render a template or redirect as needed


@app.route('/view_resume/<candidate_id>')
def view_resume(candidate_id):
    # Fetch candidate data from MongoDB using ObjectId
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})

    if candidate:
        # Get the PDF content from the candidate data
        pdf_content = candidate.get('original_resume_text', None)

        if pdf_content:
            # Serve the PDF content
            return send_file(
                BytesIO(pdf_content),
                download_name=f"{candidate['name']}_resume.pdf",
                as_attachment=True
            )
        else:
            return "Resume PDF not found for the candidate", 404
    else:
        return "Candidate not found", 404


@app.route('/success')
def success():
    return 'Added successfully!'


@app.route('/delete-candidate/<candidate_id>', methods=['POST'])
def delete_candidate(candidate_id):
    try:
        # Convert the string to ObjectId
        candidate_id = ObjectId(candidate_id)
        
        # Attempt to delete the candidate by _id
        result = candidates_collection.delete_one({'_id': candidate_id})
        
        if result.deleted_count == 1:
            # Redirect to the index route to show updated candidate list
            return redirect(url_for('index', search=request.args.get('search')))
        else:
            # Candidate not found
            candidates_cursor = candidates_collection.find()
            candidates_with_scores = [(candidate, 0) for candidate in candidates_cursor]
            
            return render_template('index.html', candidates=candidates_with_scores, message='Candidate not found')
    except Exception as e:
        # Handle exceptions
        candidates_cursor = candidates_collection.find()
        candidates_with_scores = [(candidate, 0) for candidate in candidates_cursor]
        
        return render_template('index.html', candidates=candidates_with_scores, error=str(e)), 500




@app.route('/select-candidate/<candidate_id>', methods=['POST'])
def select_candidate(candidate_id):
    try:
        # Perform the logic to select the candidate (modify this based on your needs)
        # For example, you might update a 'selected' field in your database
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id)},
            {'$set': {'selected': True}}
        )

        if result.modified_count == 1:
            # Redirect to the selected candidates page after successful selection
            return redirect(url_for('index'))
        else:
            candidates = candidates_collection.find()  # Retrieve updated candidate list
            return render_template('index.html', candidates=candidates, message='Candidate not found or already selected')
    except Exception as e:
        candidates = candidates_collection.find()  # Retrieve updated candidate list
        return render_template('index.html', candidates=candidates, error=str(e)), 500

@app.route('/selected-candidates')
def selected_candidates():
    selected_candidates = candidates_collection.find({'selected': True})
    return render_template('selected_candidates.html', selected_candidates=selected_candidates)

@app.route('/deselect-candidate/<candidate_id>', methods=['POST'])
def deselect_candidate(candidate_id):
    try:
        # Perform the logic to deselect the candidate (modify this based on your needs)
        # For example, you might update a 'selected' field in your database
        result = candidates_collection.update_one(
            {'_id': ObjectId(candidate_id)},
            {'$set': {'selected': False}}
        )

        if result.modified_count == 1:
            return jsonify({'message': 'Candidate deselected successfully'}), 200
        else:
            return jsonify({'error': 'Candidate not found or already deselected'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/interviews')
def interviews():
    try:
        # Fetch only those candidates for whom the interview is scheduled and not finished
        scheduled_candidates = candidates_collection.find({
            'scheduled_interview': {'$exists': True},
            'status': {'$ne': 'Finished'}
        })

        return render_template('interview.html', scheduled_candidates=scheduled_candidates)
    except Exception as e:
        app.logger.error(f"Error fetching candidates for interview: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500




@app.route('/finish-interview/<candidate_id>', methods=['POST'])
def finish_interview(candidate_id):
    try:
        # Fetch candidate data from MongoDB using ObjectId
        candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})

        if candidate:
            # Implement logic to mark the interview as finished in your data store
            # For example, update a status field in your database
            candidates_collection.update_one(
                {'_id': ObjectId(candidate_id)},
                {'$set': {'status': 'Finished'}}
            )

            # Return success response
            response_data = {
                'message': 'Interview marked as finished successfully',
            }

            return jsonify(response_data), 200
        else:
            # Handle the case where the candidate with the given ID is not found
            return jsonify({'error': 'Candidate not found'}), 404
    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Error marking interview as finished: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/About_us')
def About_us():
    return render_template('About_us.html')


@app.route('/schedule-interview/<candidate_id>', methods=['POST'])
def schedule_interview(candidate_id):
    try:
        candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        if candidate:
            interview_date = request.json.get('interviewDate')
            interview_time = request.json.get('formattedTime')
            meeting_mode = request.json.get('meetingMode')
            if meeting_mode == 'online':
                platform = request.json.get('platform')
                link = request.json.get('link')

                if not platform or not link:
                    return jsonify({'error': 'Missing platform or link for online interviews'}), 400

                candidates_collection.update_one(
                    {'_id': ObjectId(candidate_id)},
                    {'$set': {'scheduled_interview': {'date': interview_date, 'time': interview_time, 'mode': 'online', 'platform': platform, 'link': link}}}
                )

                send_interview_online_mail(candidate, interview_date, interview_time, platform, link)
            else:
                candidates_collection.update_one(
                    {'_id': ObjectId(candidate_id)},
                    {'$set': {'scheduled_interview': {'date': interview_date, 'time': interview_time, 'mode': 'offline'}}}
                )
                send_interview_email(candidate, interview_date, interview_time)
            response_data = {
                'success': True,
                'message': 'Interview scheduled successfully',
                'scheduledDate': interview_date,
                'scheduledTime': interview_time,
                'mode': meeting_mode
            }
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Candidate not found'}), 404
    except Exception as e:
        app.logger.error(f"Error scheduling interview: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
def send_interview_email(candidate, interview_date, interview_time):
    try:
        subject = "Interview Invitation"
        address="First floor ABC building ,4th block XYZ city"
        recruiter="Company"
        # Create the email body
        body = f"Dear {candidate['name']},\n\n"
        body += f"Thank you for your interest. We were impressed with your qualifications and experience, and we would like to invite you to interview for the position.\n\n"
        body += f"The interview will be held on {interview_date} at {interview_time} at our office located at {address}. Please arrive 15 minutes early to allow for check-in.\n\n"
        body += f"Please bring a copy of your resume and any other relevant materials.\n\n"
        body += f"We look forward to meeting you and learning more about your qualifications.\n\n"
        body += f"Sincerely,\n {recruiter}\n[Human Resource Officer]"
        msg = Message(subject, recipients=[candidate['email']], body=body)     
        # Set the email subject, recipients, and sender
        msg.extra_headers = {"From": "xyz@abc.com"}
        mail.send(msg)
        app.logger.info(f"Interview invitation email sent to {candidate['email']}")
    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Error sending interview invitation email: {str(e)}")
        raise ValueError("Error sending interview invitation email")
def send_interview_online_mail(candidate, interview_date, interview_time, platform, link):
    try:
        subject = "Online Interview Invitation"
        recruiter="Company"
        body = f"Dear {candidate['name']},\n\n"
        body += f"Thank you for your interest in the position at our company. We're excited to invite you to interview online!\n\n"
        body += f"Your interview will be held on {interview_date} at {interview_time} via {platform}.\n"
        body += f"Click on the following link to join the interview: {link}\n"
        body += f"Please ensure you have the necessary software and equipment installed and tested before the interview.\n\n"
        body += f"We look forward to meeting you online and learning more about your qualifications.\n\n"
        body += f"Sincerely,\n {recruiter}\n[Human Resource Officer]"
        msg = Message(subject, recipients=[candidate['email']], body=body)
        msg.extra_headers = {"From": "xyz@abc.com"}
        mail.send(msg)
        app.logger.info(f"Online interview invitation email sent to {candidate['email']}")
    except Exception as e:
        app.logger.error(f"Error sending online interview invitation email: {str(e)}")
        raise ValueError("Error sending online interview invitation email")


@app.route('/call-off-interview/<candidate_id>', methods=['POST'])
def call_off_interview(candidate_id):
    try:
        # Fetch candidate data from MongoDB using ObjectId
        candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        if candidate:
            # Implement logic to send an email for calling off the interview
            send_call_off_email(candidate)
            # Remove the scheduled interview information
            candidates_collection.update_one(
                {'_id': ObjectId(candidate_id)},
                {'$unset': {'scheduled_interview': 1}}
            )
            return jsonify({'message': 'Interview called off successfully'}), 200
        else:
            return jsonify({'error': 'Candidate not found'}), 404
    except Exception as e:
        app.logger.error(f"Error calling off interview: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
def send_call_off_email(candidate):
    try: 
        subject = "Interview Canceled"
        body = f"Dear {candidate['name']},\n\nWe regret to inform you that your scheduled interview has been canceled.\n"
        body += "If you have any questions or concerns, please feel free to contact us.\n\nBest Regards,\nYour Company"
        msg = Message(subject, recipients=[candidate['email']], body=body)
        
        # Set the email subject, recipients, and sender
        msg.extra_headers = {"From": "xyz@abc.com"}
        mail.send(msg)
        app.logger.info(f"Interview invitation email sent to {candidate['email']}")
    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Error sending interview invitation email: {str(e)}")
        raise ValueError("Error sending interview invitation email")   


@app.route('/reschedule-interview/<candidate_id>', methods=['POST'])
def reschedule_interview(candidate_id):
    try:
        candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        if candidate:
            new_date = request.json.get('newDate')
            new_time = request.json.get('formattedTime')
            mode_of_interview = request.json.get('meetingMode')
            if mode_of_interview == 'online':
                platform = request.json.get('platform')
                link = request.json.get('link')
                if not platform or not link:
                    return jsonify({'error': 'Missing platform or link for online interviews'}), 400
                candidates_collection.update_one(
                    {'_id': ObjectId(candidate_id)},
                    {'$set': {'scheduled_interview': {'date': new_date, 'time': new_time, 'mode': 'online', 'platform': platform, 'link': link}}}
                )
                send_rescheduled_online_mail(candidate, new_date, new_time, platform, link)
            elif mode_of_interview == 'offline':
                candidates_collection.update_one(
                    {'_id': ObjectId(candidate_id)},
                    {'$set': {'scheduled_interview': {'date': new_date, 'time': new_time, 'mode': 'offline'}}}
                )
                send_rescheduled_mail(candidate, new_date, new_time)
            response_data = {
                'success': True,
                'message': 'Interview rescheduled successfully',
                'scheduledDate': new_date,
                'scheduledTime': new_time,
                'mode': mode_of_interview
            }
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Candidate not found'}), 404
    except Exception as e:
        app.logger.error(f"Error rescheduling interview: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
def send_rescheduled_mail(candidate, new_date, new_time):
    try:
        subject = "Rescheduled Interview Invitation"
        address = "First floor ABC building, 4th block XYZ city"
        recruiter = "John Albert"
        body = f"Dear {candidate['name']},\n\n"
        body += f"We apologize for any inconvenience this may cause, but we need to reschedule your interview.\n\n"
        body += f"The interview will now be held on {new_date} at {new_time} at our office located at {address}. Please arrive 15 minutes early to allow for check-in.\n\n"
        body += f"Please bring a copy of your resume and any other relevant materials.\n\n"
        body += f"We look forward to meeting you and learning more about your qualifications.\n\n"
        body += f"Sincerely,\n {recruiter}\n[Human Resource Officer]"

        msg = Message(subject, recipients=[candidate['email']], body=body)
        msg.extra_headers = {"From": "xyz@abc.com"}
        mail.send(msg)
        app.logger.info(f"Rescheduled interview invitation email sent to {candidate['email']}")
    except Exception as e:
        app.logger.error(f"Error sending rescheduled interview invitation email: {str(e)}")
        raise ValueError("Error sending rescheduled interview invitation email")
def send_rescheduled_online_mail(candidate, new_date, new_time, platform, link):
    try:
        subject = "Rescheduled Online Interview Invitation"
        recruiter = "John Albert"
        body = f"Dear {candidate['name']},\n\n"
        body += f"We apologize for any inconvenience this may cause, but we need to reschedule your online interview.\n\n"
        body += f"The interview will now be held on {new_date} at {new_time} via {platform}.\n"
        body += f"Click on the following link to join thesoftware interview: {link}\n"
        body += f"Please ensure you have the necessary  and equipment installed and tested before the interview.\n\n"
        body += f"We look forward to meeting you online and learning more about your qualifications.\n\n"
        body += f"Sincerely,\n {recruiter}\n[Human Resource Officer]"

        msg = Message(subject, recipients=[candidate['email']], body=body)
        msg.extra_headers = {"From": "xyz@abc.com"}
        mail.send(msg)
        app.logger.info(f"Rescheduled online interview invitation email sent to {candidate['email']}")
    except Exception as e:
        app.logger.error(f"Error sending rescheduled online interview invitation email: {str(e)}")
        raise ValueError("Error sending rescheduled online interview invitation email")









if __name__ == '__main__':
    app.run(port=3000, debug=True)