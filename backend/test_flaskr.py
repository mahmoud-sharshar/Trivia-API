import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format('postgres:20211998','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        print("test passed")
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        '''  test show all categories '''
        res = self.client().get('/categories')
        data = res.get_json()
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))

    def test_retrieve_all_questions_in_existant_page(self):
        ''' test for successful retrival of questions in page 1'''
        res = self.client().get('/questions?page=1')
        data = res.get_json()
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_retrieve_all_questions_in_nonExistant_page(self):
        ''' test for failure of retrival of questions in not found page'''
        res = self.client().get('/questions?page=1000')
        data = res.get_json()
        self.assertEqual(res.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'Resource Not Found')
    
    def test_delete_question_success(self):
        ''' test for successful deletion of a question'''
        deleted_item = Question.query.get(20).format()
        cloned_item = Question(deleted_item['question'],deleted_item['answer'],
                            deleted_item['category'],deleted_item['difficulty'])
        res = self.client().delete('/questions/20')
        data = res.get_json()
        deleted_not_found = Question.query.get(20)
        self.assertEqual(deleted_not_found,None)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_question'],20)
        # restore deleted item
        cloned_item.id = 20
        cloned_item.insert()

    def test_delete_non_existant_question(self):
        ''' test for failure deletion on non_existant question'''
        res = self.client().delete('/questions/2000000')
        data = res.get_json()
        self.assertEqual(res.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'Resource Not Found')


    def test_add_new_question_with_correct_parameters(self):
        ''' test successfull addition of new question'''
        res = self.client().post('/questions',json = {
            "question":"how old is Egyptian civilization?",
            "answer": "seven thousand year",
            "category": 4,
            "difficulty": 3
            })
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code,200)

    def test_bad_request_add_new_question(self):
        ''' test of failure addition'''
        res = self.client().post('/questions',json = {
            "Auestion":"how old is Egyptian civilization?",
            "Answer": "seven thousand year",
            "Category": 4,
            "diffiiiiiculty": 3
            })
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['message'],'Bad request')

    def test_search_for_keyword(self):
        ''' test of successful search for specific question'''
        res = self.client().post('/questions/search',json = {
            "search_term":"title"
            })
        data = res.get_json()
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))

    def test_retrieve_questions_in_specific_category(self):
        ''' test of retreival of questions on specific category'''
        res = self.client().get('/categories/1/questions?page=1')
        data = res.get_json()
        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['success'])
    
    def test_retrieve_questions_in_non_existant_category(self):
        ''' test for retreival questions in non existant category'''
        res = self.client().get('/categories/111/questions?page=1')
        data = res.get_json()
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],"Resource Not Found")
        self.assertFalse(data['success'])

    def test_get_random_question_for_quiz(self):
        ''' test for successful get random question form specific category'''
        res = self.client().post("/quizzes",json = {
            "quiz_category": 2,
            "previous_questions": [17]
        })
        data  = res.get_json()
        self.assertTrue(data['success'])
        self.assertFalse(data['empty'])
        self.assertTrue(data['question']['id'] != 17)

    def test_get_random_question_after_consume_all_questions_for_quiz(self):
        ''' test to get random question from consumed category'''
        res = self.client().post("/quizzes",json = {
            "quiz_category": 2,
            "previous_questions": [16,17,18,19]
        })
        data  = res.get_json()
        print(data)
        self.assertTrue(data['success'])
        self.assertTrue(data['empty'])
        self.assertTrue(data['question'] is None)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()