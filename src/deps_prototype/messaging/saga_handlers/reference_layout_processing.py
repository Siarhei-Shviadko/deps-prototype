from ..commands import PerformParsingReply, PerformUnificationReply
from ..error import Error
from ..error_type import ErrorType
from ..sagas_data import ReferenceLayoutProcessingSagaData

__all__ = ["ReferenceLayoutProcessingHandlers"]


class ReferenceLayoutProcessingHandlers:
    @staticmethod
    def evaluate_unification_result(data: ReferenceLayoutProcessingSagaData, reply: PerformUnificationReply) -> None:
        if reply.has_error:
            data.error = Error(ErrorType(reply.error_type), reply.error_message)

    @staticmethod
    def evaluate_parsing_result(
        data: ReferenceLayoutProcessingSagaData,
        reply: PerformParsingReply,
    ) -> None:
        if reply.has_error:
            data.error = Error(ErrorType(reply.error_type), reply.error_message)
