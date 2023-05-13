from flask import Response
from typing import Optional, Union

def check_required_params(required_params: 'list[str]', recieved_params: 'list[str]') -> Optional[Union[Response, None]]:
    for param in required_params:
        if param not in recieved_params:
            return Response("Please provide a " + param, status = 400)
    return None
