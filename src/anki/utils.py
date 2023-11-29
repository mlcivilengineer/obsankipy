from typing import List, Any, Union, Dict, TypeVar

import requests

from anki.requests import AnkiMultiRequest

T = TypeVar("T", bound="ToAnkiJson")  # Type T has to implement the method to_anki_dict


def _create_multi_request(list_of: List[T], request_type: Any) -> AnkiMultiRequest:
    """
    gets a list of objects and a request type, and returns a multi request containing the requests of the specified type
    the signature of the request type should be:
    def __init__(self, object: T)
    that means it can only accept one parameter
    """
    return AnkiMultiRequest([request_type(object) for object in list_of])


def _parse(response: Union[requests.Response, Dict]) -> Any:
    """Parse the received response by getting the object inside the result of a response."""
    if isinstance(response, requests.Response):
        response = response.json()
    if len(response) != 2:
        raise Exception("response has an unexpected number of fields")
    if "error" not in response:
        raise Exception("response is missing required error field")
    if "result" not in response:
        raise Exception("response is missing required result field")
    if response["error"] is not None:
        raise Exception(response["error"])
    return response["result"]
