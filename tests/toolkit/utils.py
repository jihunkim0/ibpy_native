"""Utilities for making unittests easier to write."""
# pylint: disable=protected-access
import asyncio
import os
import queue
from typing import Dict, List, Optional, Union

from ibapi import wrapper

from ibpy_native import error
from ibpy_native import models
from ibpy_native.interfaces import delegates
from ibpy_native.interfaces import listeners
from ibpy_native.utils import finishable_queue as fq

#region - General utils
def async_test(fn):
    # pylint: disable=invalid-name
    """Decorator for testing the async functions."""
    def fn_wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()

        return loop.run_until_complete(fn(*args, **kwargs))

    return fn_wrapper
#endregion - General utils

#region - ibpy_native specific
# Constants
IB_HOST: str = os.getenv("IB_HOST", "127.0.0.1")
IB_PORT: int = int(os.getenv("IB_PORT", "4002"))
IB_CLIENT_ID: int = int(os.getenv("IB_CLIENT_ID", "1001"))
IB_ACC_ID: str = os.getenv("IB_ACC_ID", "")

class MockConnectionListener(listeners.ConnectionListener):
    """Mock connection listener."""
    def __init__(self):
        self.connected: Optional[bool] = None

    def on_connected(self):
        self.connected = True

    def on_disconnected(self):
        self.connected = False

class MockNotificationListener(listeners.NotificationListener):
    """Mock notification listener."""
    def __init__(self):
        self.msg_code = -1
        self.msg = ""

    def on_notify(self, msg_code: int, msg: str):
        """Mock callback implementation."""
        self.msg_code = msg_code
        self.msg = msg

class MockAccountsManagementDelegate(delegates.AccountsManagementDelegate):
    """Mock accounts delegate"""
    def __init__(self):
        self._account_list: Dict[str, models.Account] = {}
        self._account_updates_queue: fq.FinishableQueue = fq.FinishableQueue(
            queue_to_finish=queue.Queue()
        )

    @property
    def accounts(self) -> Dict[str, models.Account]:
        return self._account_list

    @property
    def account_updates_queue(self) -> fq.FinishableQueue:
        return self._account_updates_queue

    def on_account_list_update(self, account_list: List[str]):
        for account_id in account_list:
            self._account_list[account_id] = models.Account(account_id)

    async def sub_account_updates(self, account: models.Account):
        pass

    async def unsub_account_updates(self):
        pass

    def on_disconnected(self):
        pass

class MockLiveTicksListener(listeners.LiveTicksListener):
    """Mock notification listener"""
    def __init__(self):
        self.ticks: List[Union[wrapper.HistoricalTick,
                               wrapper.HistoricalTickBidAsk,
                               wrapper.HistoricalTickLast]] = []
        self.finished = False

    def on_tick_receive(self, req_id: int,
                        tick: Union[wrapper.HistoricalTick,
                                    wrapper.HistoricalTickBidAsk,
                                    wrapper.HistoricalTickLast,]):
        self.ticks.append(tick)

    def on_finish(self, req_id: int):
        self.finished = True

    def on_err(self, err: error.IBError):
        raise err
#endregion - ibpy_native specific
