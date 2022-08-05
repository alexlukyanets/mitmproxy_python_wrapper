import os
from datetime import datetime
from typing import Optional, NoReturn

from mitmproxy import http
from dotenv import load_dotenv

load_dotenv()
REQUEST_FOLDER = os.getenv('REQUEST_FOLDER')


class PythonView:
    def __init__(self):
        return

    @classmethod
    def wrap_url_func(cls, url: str) -> str:
        return f"""
@classmethod
def url(cls) -> str:
    return '{url}'
"""

    @classmethod
    def wrap_dict_return_func(cls, item_str: str, func_name: str) -> Optional[str]:
        if not item_str:
            return
        symbol_o = '{'
        symbol_c = '}'
        return f"""
@classmethod
def {func_name}(cls) -> dict:
    return {symbol_o}{item_str}{symbol_c}
"""

    @staticmethod
    def save_python_file(method: str, url: str, headers: str, body: str) -> NoReturn:
        file_name = f'{method}_{datetime.now().strftime("%H_%M_%S")}.py'
        with open(REQUEST_FOLDER + file_name, 'w') as file:
            file.write(url)
            file.write(headers)
            if body:
                file.write(body)

    @classmethod
    def convert_field_to_dict(cls, fields: tuple) -> Optional[dict]:
        field_dict = {}
        for key, value in fields:
            try:
                decoded_key = str(key, "utf-8")
                decoded_value = str(value, "utf-8")
            except TypeError:
                decoded_key = key
                decoded_value = value

            if not decoded_key or not decoded_value:
                continue
            field_dict.update({decoded_key: decoded_value})
        return field_dict

    @classmethod
    def convert_dict_to_classmethod_str(cls, field_dict: dict) -> Optional[str]:
        united_list = [f"'{item[0]}' : '{item[1]}'" for item in field_dict.items()]
        return ',\n'.join(united_list)

    def request(self, flow: http.HTTPFlow):
        if 'boca-egov.aspgov.com' not in flow.request.host:
            return
        str_body_items = None
        dict_header_items = self.convert_field_to_dict(flow.request.headers.fields)
        str_header_items = self.convert_dict_to_classmethod_str(dict_header_items)
        if flow.request.urlencoded_form:
            dict_form_items = self.convert_field_to_dict(flow.request.urlencoded_form.fields)
            str_body_items = self.convert_dict_to_classmethod_str(dict_form_items)
            print(str_body_items)

        self.save_python_file(flow.request.method, self.wrap_url_func(flow.request.url),
                              self.wrap_dict_return_func(str_header_items, 'headers'),
                              self.wrap_dict_return_func(str_body_items, 'formdata'))


addons = [PythonView()]
