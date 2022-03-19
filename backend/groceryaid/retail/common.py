"""Common definitions for retail chains"""

import enum
import uuid


class RetailChain(enum.Enum):
    """Identifies grocery store chain

    Each chain is assumed to have distinct API to fetch products/prices.
    """

    SOK = "sok"


# TODO: store in environment
_store_root_namespace = uuid.uuid4()

_store_namespaces = {
    chain: uuid.uuid5(_store_root_namespace, str(chain)) for chain in RetailChain
}


def get_store_id(chain: RetailChain, external_id) -> uuid.UUID:
    """Generate store id from retail chain info and external id

    Arguments:
        chain: retail chain
        external_id: store id from retail chain API

    Returns:
        UUID identifying the store
    """
    return uuid.uuid5(_store_namespaces[chain], str(external_id))
