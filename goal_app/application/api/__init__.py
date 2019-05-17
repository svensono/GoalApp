from flask import Flask, request, jsonify

from goal_app.application.containers import Queries, Instrumentations
from goal_app.infrastructure.repositories.goal import SqlAlchemyGoalRepository
from goal_app.infrastructure.orm import database
from goal_app.application.handlers.command import SetGoalCommandHandler, \
    CompleteGoalCommandHandler, DiscardGoalCommandHandler, \
    AddProgressionCommandHandler
from goal_app.domain.messages.command import SetGoalCommand, \
    CompleteGoalCommand, DiscardGoalCommand, AddProgressionCommand
from goal_app.domain.models import DiscardedEntityException

app = Flask('goal')


def http_ok(body={}, headers=None):
    return jsonify(body), 200, headers


def http_no_content(headers=None):
    return "", 204, headers


def http_conflict(body={}, headers=None):
    return jsonify(body), 409, headers


@app.route('/', methods=['GET'])
def home():
    return http_ok("Hi")


@app.route('/goals', methods=['POST'])
def set_goal():
    command = SetGoalCommand(**request.get_json())

    with database.unit_of_work() as session:
        repository = SqlAlchemyGoalRepository(session)
        handler = SetGoalCommandHandler(  # To-do: IoC
            repository=repository,
            instrumentation=Instrumentations.goal())
        handler(command)

    return http_no_content()


@app.route('/goals/<id_>/complete', methods=['PUT'])
def complete_goal(id_):
    command = CompleteGoalCommand(id=id_)

    with database.unit_of_work() as session:
        repository = SqlAlchemyGoalRepository(session)
        handler = CompleteGoalCommandHandler(
            repository=repository,  # To-do: IoC
            instrumentation=Instrumentations.goal())

        try:
            handler(command)
            return http_no_content()
        except DiscardedEntityException as ex:
            return http_conflict(dict(reason=str(ex)))


@app.route('/goals/<id_>', methods=['DELETE'])
def discard_goal(id_):
    command = DiscardGoalCommand(id=id_)

    with database.unit_of_work() as session:
        repository = SqlAlchemyGoalRepository(session)
        handler = DiscardGoalCommandHandler(
            repository=repository,  # To-do: IoC
            instrumentation=Instrumentations.goal())

        try:
            handler(command)
            return http_no_content()
        except DiscardedEntityException as ex:
            return http_conflict(dict(reason=str(ex)))


@app.route('/goals', methods=['GET'])
def list_goals():
    open_goals_query = Queries.list_open_goals()
    return http_ok(open_goals_query())


@app.route('/goals/<goal_id>/progressions', methods=['GET'])
def list_goal_progressions(goal_id):
    query = Queries.list_progressions()
    progressions = query(goal_id=goal_id)
    return http_ok(progressions)


@app.route('/goals/<goal_id>/progressions', methods=['POST'])
def set_goal_progression(goal_id):
    progression_json = request.get_json()
    progression_json['goal_id'] = goal_id

    command = AddProgressionCommand(**progression_json)

    with database.unit_of_work() as session:
        repository = SqlAlchemyGoalRepository(session)
        handler = AddProgressionCommandHandler(repository=repository)
        handler(command)

    return http_no_content()
