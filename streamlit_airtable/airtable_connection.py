
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data

from pyairtable import Api, Base, Table, metadata
import pandas as pd


class AirtableConnection(ExperimentalBaseConnection[Base]):
    # Establish a connection to Airtable using personal access token and base ID
    def _connect(self, **kwargs) -> Base:
        if "personal_access_token" not in kwargs:
            raise ValueError(
                "personal_access_token must be provided"
            )
        
        return Api(kwargs["personal_access_token"])

    # List bases (the personal access token has access to)
    # Uses pyAirtable's metadata.get_base_schema method
    # which calls https://airtable.com/developers/web/api/get-base-schema
    def list_bases(self, ttl: int = 3600, *args) -> dict:
        @cache_data(ttl=ttl)
        def _list_bases() -> dict:
            bases_list = metadata.get_api_bases(self._instance)
            return bases_list

        return _list_bases()

    # Get the base's schema
    # Uses pyAirtable's metadata.get_base_schema method
    # which calls https://airtable.com/developers/web/api/get-base-schema
    def get_base_schema(self, base_id: str, ttl: int = 3600) -> dict:
        @cache_data(ttl=ttl)
        def _get_base_schema(base_id: str = None) -> dict:
            # If base_id is not provided, use the base_id from the secrets file
            if base_id is None:
                raise ValueError(
                    "base_id must be provided or set in Streamlit secrets"
                )
            
            base = self._instance.base(base_id)
            base_schema = metadata.get_base_schema(base)
            return base_schema

        return _get_base_schema(base_id=base_id)

    # Query records from a table using pyAirtable's Table.all method
    # which calls https://airtable.com/developers/web/api/get-records
    # and paginates automatically. Parameters such as max_records, sort, view,
    # formula, and more can be passed in using kwargs and the pyAirtable reference
    # at https://pyairtable.readthedocs.io/en/stable/api.html#parameters
    def query(
        self, table_id: str, base_id: str, ttl: int = 3600, **kwargs
    ) -> pd.DataFrame:
        @cache_data(ttl=ttl)
        def _query(base_id: str, table_id: str, **kwargs) -> pd.DataFrame:
            # If base_id is not provided, use the base_id from the secrets file
            if base_id is None:
                raise ValueError(
                    "base_id must be provided or set in Streamlit secrets"
                )
                
            # If table_id is not provided, use the table_id from the secrets file
            if table_id is None:
                raise ValueError(
                    "table_id must be provided or set in Streamlit secrets"
                )
                

            table = self._instance.table(base_id, table_id)
            all_records = table.all(**kwargs)
            all_records_fields = [record["fields"] for record in all_records]
            return pd.DataFrame.from_records(all_records_fields)

        return _query(table_id=table_id, base_id=base_id, **kwargs)
