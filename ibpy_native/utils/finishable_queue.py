"""Code implementation for custom `FinishableQueue`."""
import asyncio
import enum
import queue

from typing import Iterator, Any

# Queue status
class Status(enum.Enum):
    """Status codes for `FinishableQueue`"""
    STARTED = 103
    ERROR = 500
    FINISHED = 200
    TIMEOUT = 408

class FinishableQueue():
    """This class takes a built-in `Queue` object to handle the async tasks by
    managing its' status based on elements retrieve from the `Queue` object.

    Args:
        queue_to_finish (:obj:`queue.Queue`): queue object assigned to handle
            the async task
    """
    def __init__(self, queue_to_finish: queue.Queue):
        self.__queue = queue_to_finish
        self.__status = Status.STARTED

    async def get(self) -> list:
        """Returns a list of elements retrieved from queue once the FINISHED
        flag is received, or an exception is retrieved.

        Returns:
            list: The list of element(s) returned from the queue.
        """
        contents_of_queue = []
        loop = asyncio.get_event_loop()

        while not self.__finished():
            current_element = await loop.run_in_executor(
                None, self.__queue.get
            )

            if current_element is Status.FINISHED:
                self.__status = Status.FINISHED
            else:
                if isinstance(current_element, BaseException):
                    self.__status = Status.ERROR

                contents_of_queue.append(current_element)

        return contents_of_queue

    async def stream(self) -> Iterator[Any]:
        """Yields the elements in queue as soon as an element has been put into
        the queue.

        Notes:
            This function will not timeout like the `get(timeout: int)`
            function. Instead, it waits forever until the finish signal is
            received before it breaks the internal loop.
        """
        loop = asyncio.get_event_loop()

        while not self.__finished():
            current_element = await loop.run_in_executor(
                None, self.__queue.get
            )

            if current_element is Status.FINISHED:
                self.__status = current_element
            elif isinstance(current_element, BaseException):
                self.__status = Status.ERROR

            yield current_element

    @property
    def status(self) -> Status:
        """Get status of the finishable queue.

        Returns:
            Status: Enum `Status` represents either the queue has been started,
                finished, timeout, or encountered error.
        """
        return self.__status

    def reset(self):
        """Reset the status to `STARTED` for reusing the queue if the
        status is marked as either `TIMEOUT` or `FINISHED`
        """
        if self.__finished():
            self.__status = Status.STARTED

    def __finished(self) -> bool:
        return (self.__status is Status.TIMEOUT
                or self.__status is Status.FINISHED
                or self.__status is Status.ERROR)
