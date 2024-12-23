# Inspiration: https://github.com/apify/crawlee/blob/v3.8.2/packages/types/src/storages.ts#L314:L328

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from crawlee._utils.docs import docs_group

if TYPE_CHECKING:
    from ._base_dataset_client import BaseDatasetClient
    from ._base_dataset_collection_client import BaseDatasetCollectionClient
    from ._base_key_value_store_client import BaseKeyValueStoreClient
    from ._base_key_value_store_collection_client import BaseKeyValueStoreCollectionClient
    from ._base_request_queue_client import BaseRequestQueueClient
    from ._base_request_queue_collection_client import BaseRequestQueueCollectionClient


@docs_group('Abstract classes')
class BaseStorageClient(ABC):
    """Defines an abstract base for storage clients.

    It offers interfaces to get subclients for interacting with storage resources like datasets, key-value stores,
    and request queues.
    """

    @abstractmethod
    def dataset(self, id: str) -> BaseDatasetClient:
        """Gets a subclient for a specific dataset by its ID."""

    @abstractmethod
    def datasets(self) -> BaseDatasetCollectionClient:
        """Gets a subclient for dataset collection operations."""

    @abstractmethod
    def key_value_store(self, id: str) -> BaseKeyValueStoreClient:
        """Gets a subclient for a specific key-value store by its ID."""

    @abstractmethod
    def key_value_stores(self) -> BaseKeyValueStoreCollectionClient:
        """Gets a subclient for key-value store collection operations."""

    @abstractmethod
    def request_queue(self, id: str) -> BaseRequestQueueClient:
        """Gets a subclient for a specific request queue by its ID."""

    @abstractmethod
    def request_queues(self) -> BaseRequestQueueCollectionClient:
        """Gets a subclient for request queue collection operations."""

    @abstractmethod
    async def purge_on_start(self) -> None:
        """Performs a purge of the default storages.

        This method ensures that the purge is executed only once during the lifetime of the instance.
        It is primarily used to clean up residual data from previous runs to maintain a clean state.
        If the storage client does not support purging, leave it empty.
        """
