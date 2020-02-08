from models import setup_db, Question, Category
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    # response.headers.add('Access-Control-Allow-Credentials','true')
    # response.headers.add('Access-Control-Allow-Origin',"*")
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def show_categories():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    return jsonify({
        'success': True,
        'categories': formatted_categories
      })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retreive_questions():
    page = request.args.get('page',1,type=int)

    questions = Question.query.all()
    current_category = Category.query.get(1).format()
    categories = Category.query.all()
    categories = [category.format() for category in categories]

    start = (page - 1) * QUESTIONS_PER_PAGE
    if(start > len(questions)):
      abort(404)
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in questions[start:end]]
    return jsonify({
        'success':True,
        'questions':formatted_questions,
        'total_questions': len(questions),
        'categories':categories,
        'current_category': current_category
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    deleted_question = Question.query.get(question_id)
    if deleted_question is None:
      abort(404)
    try:
      deleted_question.delete()
      return jsonify({
        'success':True,
        'deleted_question': question_id
      })
    except:
      abort(500)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_new_question():
    data = request.get_json()
    try:
      new_question = Question(data['question'],data['answer'],
                            data['category'],data['difficulty'])
    except:
      abort(400)

    try:
      new_question.insert()
      return jsonify({
          'success': True
        })
    except:
      abort(500)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search',methods=['POST'])
  def search_for_quesrion():
    try:
      search_term = request.get_json()['search_term']
    except:
      abort(400)
    
    try:
      questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
    except:
      abort(500)
    
    formatted_questions = [question.format() for question in questions]
    return jsonify({
        'success':True,
        'questions':formatted_questions
      })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def retreive_category_questions(category_id):
    page = request.args.get('page',1,type=int)

    current_category = Category.query.get(category_id)
    if current_category is None:
      abort(404)

    categories = Category.query.all()
    categories = [category.format() for category in categories]

    questions = Question.query.filter(Question.category == category_id).all()

    start = (page - 1) * QUESTIONS_PER_PAGE
    if(start > len(questions)):
      abort(404)
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in questions[start:end]]
    return jsonify({
        'success':True,
        'questions':formatted_questions,
        'total_questions': len(questions),
        'current_category': current_category.format(),
        'categories': categories
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  
  @app.route('/quizzes',methods=['POST'])
  # @cross_origin()
  def get_quiz_questions():
    data = request.get_json()
    try:
      category_id = data['quiz_category']
      questions_id = data['previous_questions']
    except:
      abort(400)

    required_category = Category.query.get(category_id)
    if required_category is None:
      abort(404)

    try:
      category_questions = Question.query.filter(Question.category == category_id).all()
      if len(category_questions) == len(questions_id):
        return jsonify({
            'success':True,
            'question':None,
            'empty': True
        })
      else:
        random_questions = []
        for question in category_questions:
          if question.id not in questions_id:
            random_questions.append(question.format())
        
        selected_question = random_questions[random.randint(0,len(random_questions))]
        return jsonify({
              'success':True,
              'question':selected_question,
              'empty': False
          })
    except:
      abort(500)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found_404(error):
    return jsonify({
        'success':False,
        'message':"Resource Not Found",
        'error':404
      }),404

  @app.errorhandler(500)
  def server_error_500(error):
    return jsonify({
        'success':False,
        'message':"server error",
        'error':500
      }),500

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
        "success":False,
        "message": "Method Not Alowed",
        "error": 405
      }),405

  @app.errorhandler(400)
  def  bad_request(error):
    return jsonify({
        "success":False,
        "message": "Bad request",
        "error": 400
      }),400

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
        "success":False,
        "message": "unprocessable entity",
        "error": 422
      }),422

  return app

    