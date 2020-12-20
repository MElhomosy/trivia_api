import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        formated_categories = [category.format() for category in categories]
        return jsonify({
          'success':True,
          'categories':formated_categories
        })

    @app.route('/questions')
    def retrieve_questions():
        categories = Category.query.order_by(Category.id).all()
        formated_categories = [category.format() for category in categories]
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.order_by(Question.id).all()
        formated_questions = [question.format() for question in questions]
        current_questions = formated_questions[start:end]
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
          'success':True,
          'questions':formated_questions[start:end],
          'total_questions': len(formated_questions),
          'categories': formated_categories,
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_specific_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            questions = Question.query.order_by(Question.id).all()
            formated_questions = [question.format() for question in questions]


            return jsonify({
              'success':True,
              'deleted':question.id,
              'questions': formated_questions
            })

        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question',None)
        new_answer = body.get('answer',None)
        new_category = body.get('category',None)
        new_difficulty = body.get('difficulty',None)
        search = body.get('search', None)
        try:
            if search:
                page = request.args.get('page', 1, type=int)
                start = (page-1) * QUESTIONS_PER_PAGE
                end = start + QUESTIONS_PER_PAGE
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                formated_questions = [question.format() for question in selection]
                current_questions = formated_questions[start:end]
                return jsonify({
                    'success':True,
                    'questions': current_questions
                })
            else:
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()

                return jsonify({
                  'success':True
                })

        except:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_for_specific_category(category_id):
        categories = Category.query.order_by(Category.id).all()
        formated_categories = [category.format() for category in categories]
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.order_by(Question.id).filter(Question.category==category_id)
        formated_questions = [question.format() for question in questions]
        current_questions = formated_questions[start:end]
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
          'success':True,
          'questions':formated_questions[start:end],
          'total_questions': len(formated_questions),
          'categories': formated_categories,
          'current_category': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def retrieve_questions_for_quiz(category_id):
        body = request.get_json()

        category = body.get('quizCategory',None)
        previousquestions = body.get('previousQuestions',None)

        try:
            nextquestion = Question.query.order_by(Question.id).filter(Question.category==category & Question.id not in previousquestions).first()
            return jsonify({
              'success':True,
              'currentQuestion':nextquestion
            })

        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "resource not found"
            }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "method not allowed"
            }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Unprocessable Entity"
            }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "Internal Server Error"
            }), 500

    return app
