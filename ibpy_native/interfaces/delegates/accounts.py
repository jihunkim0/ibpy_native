"""Internal delegate module for accounts & portfolio related features."""
import abc
from typing import List

class _AccountListDelegate(metaclass=abc.ABCMeta):
    """Internal delegate protocol for accounts & portfolio related features."""
    @property
    @abc.abstractmethod
    def accounts(self) -> List[str]:
        """Abstract getter of a list of account IDs.

        This property should be implemented to return the internal account ID
        list.
        """
        return NotImplemented

    @abc.abstractmethod
    def on_account_list_update(self, account_list: List[str]):
        """Callback on `_IBWrapper.managedAccounts` is triggered by IB API.

        Args:
            account_list (:obj:`List[str]`): List of proceeded account IDs
                updated from IB.
        """
        return NotImplemented
