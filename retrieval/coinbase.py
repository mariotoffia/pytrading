import pandas as pd

from os import getenv
from typing import List, Optional
from datetime import datetime
from coinbaseadvanced.client import CoinbaseAdvancedTradeAPIClient, AuthSchema, ProductType, Granularity


class CoinbaseClient:
    def __init__(self, api_key: str = 'CB_API_KEY_NAME', secret_key='CB_PRIVATE_KEY'):
        if 'organizations' not in api_key:
            api_key = getenv(api_key)

        if '-----BEGIN EC PRIVATE KEY-----' not in secret_key:
            secret_key = getenv(secret_key).replace('\\n', '\n')

        self.client = CoinbaseAdvancedTradeAPIClient(
            api_key=api_key,
            secret_key=secret_key,
            auth_schema=AuthSchema.CLOUD_API_TRADING_KEYS
        )

    def native(self):
        """Returns the native client"""
        return self.client

    def list_products(self,
                      limit: int = None,
                      offset: int = None,
                      product_type: ProductType = None,
                      columns: Optional[List[str]] = None
                      ) -> pd.DataFrame:
        """
        Lists the products and creates a dataframe from the results.

        :param limit: The number of results to return.
        :param offset: The offset for pagination.
        :param product_type: The product type.
        :param columns: The columns to return. If none, all columns 
                        are returned. product_id is required since it is the index

        :return: A dataframe with the results.
        """
        if columns is not None and len(columns) > 0 and 'product_id' not in columns:
            columns.append('product_id')

        products = self.client.list_products(
            limit=limit,
            offset=offset,
            product_type=product_type
        )

        product_dicts = [product_to_dict(product, columns)
                         for product in products]

        df = pd.DataFrame(product_dicts)
        df.set_index('product_id', inplace=True)

        return df

    def get_product_candles(self, product_id: str, start_date: datetime, end_date: datetime, granularity: Granularity) -> pd.DataFrame:
        candles_page = self.client.get_product_candles(
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity)

        # Process the returned data
        candles_data = []
        for candle in candles_page.candles:
            candle_dict = {
                # Convert Unix timestamp to datetime
                'Date': pd.to_datetime(int(candle.start), unit='s'),
                'Low': float(candle.low),
                'High': float(candle.high),
                'Open': float(candle.open),
                'Close': float(candle.close),
                'Volume': float(candle.volume)
            }
            candles_data.append(candle_dict)

        # Create the DataFrame and set 'date' as the index
        df = pd.DataFrame(candles_data)
        df.set_index('date', inplace=True)

        return df


def product_to_dict(product, columns: Optional[List[str]] = None):
    # List of all possible attributes of the Product class
    all_attributes = [
        'product_id', 'price', 'price_percentage_change_24h', 'volume_24h',
        'volume_percentage_change_24h', 'base_increment', 'quote_increment',
        'quote_min_size', 'quote_max_size', 'base_min_size', 'base_max_size',
        'base_name', 'quote_name', 'watched', 'is_disabled', 'new', 'status',
        'cancel_only', 'limit_only', 'post_only', 'trading_disabled',
        'auction_mode', 'product_type', 'quote_currency_id', 'base_currency_id',
        'mid_market_price', 'fcm_trading_session_details', 'alias', 'alias_to',
        'base_display_symbol', 'quote_display_symbol'
    ]

    if columns is None:
        # If no specific columns are requested, use all attributes
        columns = all_attributes

    # Build the dictionary using getattr to fetch attribute values
    return {attr: getattr(product, attr, None) for attr in columns}
