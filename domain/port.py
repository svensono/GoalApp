from abc import ABCMeta, abstractmethod

from domain.model.goal import Goal


class GoalRegistry(metaclass=ABCMeta):

    @abstractmethod
    def add(self, goal: Goal) -> None:
        pass
