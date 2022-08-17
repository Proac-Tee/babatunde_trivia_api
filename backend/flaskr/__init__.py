# from crypt import methods
# from nis import cat
import os
from unicodedata import category

# import resource
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Questions pagination ---Done
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]

    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # CORS app setup ---Done
    CORS(app, resource={"/": {"origins": "*"}})

    # CORS Headers ---Done
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # Endpoint to handle GET requests for all available categories ---Done

    @app.route("/categories")
    def available_categories():

        # get all categories
        selection = Category.query.order_by(Category.id).all()
        current_category = paginate_questions(request, selection)

        if len(current_category) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in selection},
                "total_categories": len(Category.query.all()),
            }
        )

    # An endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint returns a list of questions, number of total questions, current category, categories.

    @app.route("/questions")
    def available_questions():
        try:
            # get all questions
            selection = Question.query.order_by(Question.id).all()

            # get current questions in a page
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "list_of_questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "current_category": [],
                    "categories": [category.type for category in Category.query.all()],
                }
            )
        except Exception:
            abort(422)

    # An endpoint to DELETE question using a question ID.

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            # fetch question by fithering by the question id
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            # Post the update in the front end
            current_question = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question.id,
                    "questions": current_question,
                    "total_questions": len(Question.query.all()),
                }
            )

        except Exception:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_question():
        # get the body from frontend input as json
        body = request.get_json()

        # input data from the frontend
        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)

        # A POST endpoint to get questions based on a search term. Return any questions for whom the search term is a substring of the question.
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike(f"%{search}%")
                )

                # Post the update in the front end
                current_questions = paginate_questions(request, selection)

                categories = Category.query.all()
                current_category = {
                    category.id: category.type for category in categories
                }

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                        "current_category": current_category,
                    }
                )

            # An endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.
            else:
                question = Question(
                    question=question,
                    answer=answer,
                    category=category,
                    difficulty=difficulty,
                )
                question.insert()

                selection = Question.query.order_by(Question.id).all()

                # Post the update in the front end
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_questions,
                        "question_created": question.question,
                        "total_questions": len(Question.query.all()),
                    }
                )

        except Exception:
            abort(422)

    # A GET endpoint to get questions based on category.
    @app.route("/categories/<int:category_id>/questions")
    def category_question(category_id):
        try:
            c_id = category_id + 1

            # fetch the question of a category by their id
            category = Category.query.filter(Category.id == c_id).one_or_none()

            if category is None:
                abort(404)

            # fetch all question in the selected category
            selection = (
                Question.query.filter(Question.category == category.id)
                .order_by(Question.id)
                .all()
            )

            # Post the update in the front end
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                    "categories": [category.type for category in Category.query.all()],
                    "current_category": category.type,
                }
            )
        except Exception:
            abort(400)

    # A POST endpoint to get questions to play the quiz.
    # This endpoint takes category and previous question parametersand return a random questions within the given category, if provided, and that is not one of the previous questions.

    @app.route("/quizzes", methods=["POST"])
    def get_quiz_question():
        # get the qestion category
        body = request.get_json()
        try:
            previous_questions = body.get("previous_questions")

            quiz_category = body.get("quiz_category")["id"]

            if previous_questions is None:
                abort(400)

            questions = []
            # Filter available questions by all category and new questions
            if quiz_category == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)
                ).all()
            else:
                category = Category.query.get(quiz_category)
                if category is None:
                    abort(404)
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == quiz_category,
                ).all()
            current_question = None

            # randomize the question
            if len(questions) > 0:
                index = random.randrange(0, len(questions))
                current_question = questions[index].format()
            return jsonify(
                {
                    "success": True,
                    "question": current_question,
                    "total_questions": len(questions),
                }
            )
        except Exception:
            abort(400)

    ############# Error handlers #############

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(505)
    def not_found(error):
        return (
            jsonify(
                {"success": False, "error": 505, "message": "Internal server error"}
            ),
            405,
        )

    return app
