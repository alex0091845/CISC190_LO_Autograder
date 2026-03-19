from abc import ABC, abstractmethod

from models.requirements.requirement_result import RequirementResult

class RequirementNode(ABC):
    @abstractmethod
    def evaluate(self, **params) -> RequirementResult:
        pass

    @abstractmethod
    def add_child(self, child: 'RequirementNode'):
        pass

    @abstractmethod
    def get_all_children(self) -> list['RequirementNode']:
        pass