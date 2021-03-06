from goal_service.application.handlers import RelatedEntityNotFoundException
from goal_service.domain.messages.command import SetGoalCommand, \
    CompleteGoalCommand, DiscardGoalCommand, AddProgressionCommand, \
    DiscardProgressionCommand, EditProgressionCommand, SetSubGoalCommand
from goal_service.infrastructure.repositories import EntityNotFoundException


class CommandHandler:
    def __init__(self, repository, instrumentation):
        self.repository = repository
        self.instrumentation = instrumentation


class FactoryCommandHandler:
    def __init__(self, factory, repository, instrumentation):
        self.factory = factory
        self.repository = repository
        self.instrumentation = instrumentation


class SetGoalCommandHandler(FactoryCommandHandler):
    def __call__(self, command: SetGoalCommand):
        goal = self.factory(
            name=command.name,
            description=command.description,
            due_date=command.due_date)
        self.repository.add(goal)
        self.instrumentation.goal_set(goal)


class CompleteGoalCommandHandler(CommandHandler):
    def __call__(self, command: CompleteGoalCommand):
        try:
            goal = self.repository.get(command.id)
            goal.complete()
            self.instrumentation.goal_completed(goal)
        except EntityNotFoundException:
            self.instrumentation.goal_lookup_failed(command.id)
            raise RelatedEntityNotFoundException


class DiscardGoalCommandHandler(CommandHandler):
    def __call__(self, command: DiscardGoalCommand):
        try:
            goal = self.repository.get(command.id)
            goal.discard()
            self.instrumentation.goal_discarded(goal)
        except EntityNotFoundException:
            self.instrumentation.goal_lookup_failed(command.id)
            raise RelatedEntityNotFoundException


class AddProgressionCommandHandler(FactoryCommandHandler):
    def __call__(self, command: AddProgressionCommand):
        try:
            goal = self.repository.get(command.goal_id)
            progression = self.factory(note=command.note,
                                       percentage=command.percentage)
            goal.add_progression(progression)
            self.instrumentation.add_progression(goal)
        except EntityNotFoundException:
            self.instrumentation.goal_lookup_failed(command.goal_id)
            raise RelatedEntityNotFoundException


class DiscardProgressionCommandHandler(CommandHandler):
    def __call__(self, command: DiscardProgressionCommand):
        try:
            progression = self.repository.get(command.id)
            progression.discard()
            self.instrumentation.discard_progression(progression)
        except EntityNotFoundException:
            self.instrumentation.progression_lookup_failed(command.id)
            raise EntityNotFoundException


class EditProgressionCommandHandler(CommandHandler):
    def __call__(self, command: EditProgressionCommand):
        try:
            progression = self.repository.get(command.id)
            progression.note = command.note
            progression.percentage = command.percentage
            self.instrumentation.edit_progression(progression)
        except EntityNotFoundException:
            self.instrumentation.progression_lookup_failed(command.id)
            raise EntityNotFoundException


class SetSubGoalCommandHandler(FactoryCommandHandler):
    def __call__(self, command: SetSubGoalCommand):
        try:
            main_goal = self.repository.get(command.main_goal_id)
            goal = self.factory(
                name=command.name,
                description=command.description,
                due_date=command.due_date)
            main_goal.set_subgoal(goal)
            self.instrumentation.goal_set(goal)
        except EntityNotFoundException:
            self.instrumentation.goal_lookup_failed(command.main_goal_id)
            raise RelatedEntityNotFoundException
