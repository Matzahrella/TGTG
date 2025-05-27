import uuid
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field

class Request(BaseModel):
    timestamp_start: float
    method: str
    url: str
    headers: Dict[str, str]
    body: Any = None # Body can be None, dict, str, or bytes
    content_type: Optional[str] = None

    # Pydantic v2 validator to extract content_type from headers if not provided
    # For Pydantic v1, you would use @validator with pre=True, always=True
    # from pydantic import model_validator
    # @model_validator(mode='before')
    # def extract_content_type_from_headers(cls, values):
    #     headers = values.get('headers', {})
    #     if 'content_type' not in values or values['content_type'] is None:
    #         values['content_type'] = headers.get('content-type', headers.get('Content-Type'))
    #     return values

class Response(BaseModel):
    timestamp_end: Optional[float] = None
    status_code: int
    headers: Dict[str, str]
    body: Optional[Any] = None # Body can be None, dict, str, or bytes
    content_type: Optional[str] = None

    # Pydantic v2 validator
    # from pydantic import model_validator
    # @model_validator(mode='before')
    # def extract_content_type_from_headers(cls, values):
    #     headers = values.get('headers', {})
    #     if 'content_type' not in values or values['content_type'] is None:
    #         values['content_type'] = headers.get('content-type', headers.get('Content-Type'))
    #     return values

class HTTPFlow(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    request: Request
    response: Optional[Response] = None
    annotation: str = ""
    client_conn_id: Optional[str] = None
    server_conn_id: Optional[str] = None
    timestamp_created: Optional[float] = None

# Example Usage (can be removed or kept for testing)
if __name__ == '__main__':
    # Example Request Data
    req_data = {
        "timestamp_start": 1678886400.0,
        "method": "POST",
        "url": "https://api.example.com/submit",
        "headers": {"Content-Type": "application/json", "X-Auth-Token": "secret"},
        "body": {"key": "value"},
        # content_type will be auto-extracted if validator is used, or can be set explicitly
    }
    request_obj = Request(**req_data)
    # If using the validator, content_type would be set. Manually setting for this example:
    if request_obj.content_type is None:
        request_obj.content_type = request_obj.headers.get('Content-Type')
    print("Request Object:")
    print(request_obj.model_dump_json(indent=2))

    # Example Response Data
    res_data = {
        # "timestamp_end": 1678886401.5, # Timestamp end is now optional
        "status_code": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {"status": "success", "data": {"id": 123}},
    }
    response_obj = Response(**res_data)
    if response_obj.content_type is None: # Manual content_type handling for example
        response_obj.content_type = response_obj.headers.get('Content-Type')
    if response_obj.timestamp_end is None: # Example of adding it if missing
        response_obj.timestamp_end = time.time() # Dummy value for example
    print("\nResponse Object:")
    print(response_obj.model_dump_json(indent=2))

    # Example HTTPFlow Data
    # Need to import time for the example to run
    import time
    http_flow_obj = HTTPFlow(
        request=request_obj,
        response=response_obj,
        annotation="User login successful",
        client_conn_id="client_conn_abc",
        server_conn_id="server_conn_xyz",
        timestamp_created=1678886399.0
    )
    print("\nHTTPFlow Object:")
    print(http_flow_obj.model_dump_json(indent=2))

    # HTTPFlow with no response
    http_flow_no_resp_obj = HTTPFlow(
        request=request_obj,
        annotation="Request sent, no response yet or not applicable",
        timestamp_created=1678886400.0
    )
    print("\nHTTPFlow Object (No Response):")
    print(http_flow_no_resp_obj.model_dump_json(indent=2))

    # Test default ID generation and annotation
    minimal_request_data = {
        "timestamp_start": 1678886500.0,
        "method": "GET",
        "url": "https://api.example.com/health",
        "headers": {},
    }
    minimal_request_obj = Request(**minimal_request_data)
    flow_with_defaults = HTTPFlow(request=minimal_request_obj)
    print("\nHTTPFlow Object (Defaults):")
    print(flow_with_defaults.model_dump_json(indent=2))
    assert flow_with_defaults.id is not None
    assert flow_with_defaults.annotation == ""
