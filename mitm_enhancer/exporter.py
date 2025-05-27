import json
from typing import List, Dict, Any, Optional

from .models import HTTPFlow, Request, Response

def format_headers_md(headers: Dict[str, str]) -> str:
    """Formats a dictionary of headers into a Markdown code block string."""
    if not headers:
        return "```\n<No headers>\n```"
    header_lines = [f"{key}: {value}" for key, value in headers.items()]
    return "```\n" + "\n".join(header_lines) + "\n```"

def format_body_md(body: Any, content_type: Optional[str]) -> str:
    """Formats a body into a Markdown string, using JSON for appropriate content types."""
    content_type_str = content_type if content_type else "N/A"
    md_parts = [f"**Body (`{content_type_str}`):**\n"]

    if body is None:
        md_parts.append("```\n<Empty body>\n```")
    elif "application/json" in (content_type or "").lower():
        try:
            # If body is already a dict/list (parsed by parser)
            if isinstance(body, (dict, list)):
                json_body = json.dumps(body, indent=2)
            # If body is string or bytes (needs to be loaded first)
            elif isinstance(body, str):
                json_body = json.dumps(json.loads(body), indent=2)
            elif isinstance(body, bytes):
                 # Try to decode then parse
                try:
                    json_body = json.dumps(json.loads(body.decode('utf-8')), indent=2)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    md_parts.append("```text\n<Binary data or malformed JSON in bytes>\n```")
                    return "".join(md_parts)
            else: # Should not happen if parser normalizes JSON to dict/list
                json_body = json.dumps(body, indent=2) # best effort
            
            md_parts.append("```json\n" + json_body + "\n```")
        except json.JSONDecodeError:
            # Fallback if JSON parsing/dumping fails for some reason
            md_parts.append("```text\n<Malformed JSON data>\n```")
        except Exception: # Catch any other error during JSON processing
             md_parts.append("```text\n<Error processing JSON body>\n```")
    elif isinstance(body, bytes):
        try:
            text_body = body.decode('utf-8')
            md_parts.append("```text\n" + text_body + "\n```")
        except UnicodeDecodeError:
            md_parts.append("```\n<Binary data (non-UTF-8)>\n```")
    elif isinstance(body, str):
        md_parts.append("```text\n" + body + "\n```")
    else: # Should ideally not be reached if body is one of the above
        md_parts.append("```\n<Unknown body type>\n```")
    
    return "".join(md_parts)

def export_to_markdown(flows: List[HTTPFlow], output_file_path: str) -> bool:
    """
    Exports a list of HTTPFlow objects to a Markdown file.

    Args:
        flows: A list of HTTPFlow Pydantic model instances.
        output_file_path: The path to the output Markdown file.

    Returns:
        True if export was successful, False otherwise.
    """
    markdown_content = []

    for flow in flows:
        markdown_content.append(f"## Flow ID: `{flow.id}`")
        markdown_content.append(f"**Annotation:** {flow.annotation if flow.annotation else '_N/A_'}")
        markdown_content.append(f"**Timestamp Created:** {flow.timestamp_created if flow.timestamp_created else '_N/A_'}")
        markdown_content.append(f"**Client Connection ID:** {flow.client_conn_id if flow.client_conn_id else '_N/A_'}")
        markdown_content.append(f"**Server Connection ID:** {flow.server_conn_id if flow.server_conn_id else '_N/A_'}")
        markdown_content.append("\n")

        # Request
        markdown_content.append("### Request")
        markdown_content.append(f"**Timestamp:** {flow.request.timestamp_start}")
        markdown_content.append(f"**Method:** `{flow.request.method}`")
        markdown_content.append(f"**URL:** `{flow.request.url}`")
        markdown_content.append("**Headers:**")
        markdown_content.append(format_headers_md(flow.request.headers))
        markdown_content.append(format_body_md(flow.request.body, flow.request.content_type))
        markdown_content.append("\n---\n") # Horizontal rule between request and response

        # Response
        if flow.response:
            markdown_content.append("### Response")
            markdown_content.append(f"**Timestamp:** {flow.response.timestamp_end}")
            markdown_content.append(f"**Status Code:** `{flow.response.status_code}`")
            markdown_content.append("**Headers:**")
            markdown_content.append(format_headers_md(flow.response.headers))
            markdown_content.append(format_body_md(flow.response.body, flow.response.content_type))
            markdown_content.append("\n---\n")
        else:
            markdown_content.append("### No Response\n")
            markdown_content.append("---\n")
        
        markdown_content.append("<br/>\n<hr/>\n<br/>\n") # Separator for next flow

    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))
        return True
    except IOError as e:
        print(f"Error writing to file {output_file_path}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during Markdown export: {e}")
        return False

if __name__ == '__main__':
    # Example Usage (requires models.py to be accessible)
    # Create dummy flow objects for testing
    print("Testing Markdown Exporter...")
    
    # Dummy Request 1
    req1 = Request(
        timestamp_start=1678886400.0, method="GET", url="https://example.com/api/data",
        headers={"X-Test": "true", "Accept": "application/json"}, 
        body=None, content_type=None
    )
    # Dummy Response 1
    res1 = Response(
        timestamp_end=1678886400.5, status_code=200,
        headers={"Content-Type": "application/json", "Server": "TestServer"},
        body={"message": "Success!", "data": [1, 2, 3]}, content_type="application/json"
    )
    # Dummy Flow 1
    flow1 = HTTPFlow(
        request=req1, response=res1, annotation="Test flow 1",
        timestamp_created=1678886399.0
    )

    # Dummy Request 2 (POST with text body)
    req2 = Request(
        timestamp_start=1678886401.0, method="POST", url="https://example.com/api/submit",
        headers={"Content-Type": "text/plain"}, 
        body="This is a sample text body.", content_type="text/plain"
    )
    # Dummy Flow 2 (No Response)
    flow2 = HTTPFlow(
        request=req2, response=None, annotation="Test flow 2 - No response",
        timestamp_created=1678886400.0,
        client_conn_id="cc123", server_conn_id="sc456"
    )
    
    # Dummy Request 3 (Binary data)
    req3 = Request(
        timestamp_start=1678886402.0, method="GET", url="https://example.com/api/image.png",
        headers={}, 
        body=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89', # Tiny PNG
        content_type="image/png"
    )
    flow3 = HTTPFlow(request=req3)


    test_flows = [flow1, flow2, flow3]
    output_path = "test_export.md"

    if export_to_markdown(test_flows, output_path):
        print(f"Successfully exported {len(test_flows)} flows to {output_path}")
        # You can open test_export.md to verify the output
    else:
        print(f"Failed to export flows to {output_path}")

    # Test header formatting
    print("\nTesting header formatting:")
    print(format_headers_md({"Key1": "Value1", "Key2": "Value2"}))
    
    # Test body formatting
    print("\nTesting body formatting (JSON):")
    print(format_body_md({"test": "data"}, "application/json"))
    print("\nTesting body formatting (Text from bytes):")
    print(format_body_md(b"Hello bytes", "text/plain"))
    print("\nTesting body formatting (Binary bytes):")
    print(format_body_md(b"\x00\x01\xff", "application/octet-stream"))
    print("\nTesting body formatting (None):")
    print(format_body_md(None, None))
