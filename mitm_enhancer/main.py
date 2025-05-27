import argparse
import sys
import json
from typing import List, Optional, Any

from .parser import parse_flows
from .models import HTTPFlow, Request, Response
from .exporter import export_to_markdown # Added for export functionality

def display_flow(flow: HTTPFlow):
    """Prints the details of a single HTTPFlow object in a readable format."""
    print("\n--------------------------------------------------")
    print(f"Flow ID: {flow.id}")
    print(f"Annotation: {flow.annotation if flow.annotation else '<No annotation>'}")
    print(f"Timestamp Created: {flow.timestamp_created if flow.timestamp_created else 'N/A'}")
    print(f"Client Conn ID: {flow.client_conn_id if flow.client_conn_id else 'N/A'}")
    print(f"Server Conn ID: {flow.server_conn_id if flow.server_conn_id else 'N/A'}")

    # Display Request
    req = flow.request
    print("\n--- Request ---")
    print(f"Timestamp: {req.timestamp_start}")
    print(f"Method: {req.method}")
    print(f"URL: {req.url}")
    print("Headers:")
    for key, value in req.headers.items():
        print(f"  {key}: {value}")
    
    body_content_type = req.content_type if req.content_type else "N/A"
    print(f"Body ({body_content_type}):")
    if isinstance(req.body, (dict, list)):
        print(json.dumps(req.body, indent=2))
    elif isinstance(req.body, bytes):
        try:
            print(req.body.decode('utf-8'))
        except UnicodeDecodeError:
            print(f"<bytes_content_len:{len(req.body)}> (non-UTF-8)")
    elif isinstance(req.body, str):
        print(req.body)
    elif req.body is None:
        print("<empty_body>")
    else:
        print(f"<unknown_body_type: {type(req.body)}>")

    # Display Response (if present)
    res = flow.response
    if res:
        print("\n--- Response ---")
        print(f"Timestamp: {res.timestamp_end}")
        print(f"Status Code: {res.status_code}")
        print("Headers:")
        for key, value in res.headers.items():
            print(f"  {key}: {value}")

        res_body_content_type = res.content_type if res.content_type else "N/A"
        print(f"Body ({res_body_content_type}):")
        if isinstance(res.body, (dict, list)):
            print(json.dumps(res.body, indent=2))
        elif isinstance(res.body, bytes):
            try:
                print(res.body.decode('utf-8'))
            except UnicodeDecodeError:
                print(f"<bytes_content_len:{len(res.body)}> (non-UTF-8)")
        elif isinstance(res.body, str):
            print(res.body)
        elif res.body is None:
            print("<empty_body>")
        else:
            print(f"<unknown_body_type: {type(res.body)}>")
    else:
        print("\n--- No Response ---")
    print("--------------------------------------------------")

def main_cli():
    parser = argparse.ArgumentParser(description="Mitmproxy Enhancement Tool - Interactive Flow Viewer & Annotator")
    parser.add_argument("flow_file", help="Path to the mitmproxy flow file.")
    args = parser.parse_args()

    try:
        flows: List[HTTPFlow] = parse_flows(args.flow_file)
    except FileNotFoundError:
        print(f"Error: Flow file not found at '{args.flow_file}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing flow file: {e}", file=sys.stderr)
        sys.exit(1)

    if not flows:
        print("No HTTP flows found in the file.")
        sys.exit(0)

    current_flow_index = 0
    
    while True:
        if not flows: # Should be caught earlier, but as a safeguard
            print("No flows to display.")
            break

        display_flow(flows[current_flow_index])
        
        print("\nCommands:")
        print("  (n)ext          Go to the next flow")
        print("  (p)revious      Go to the previous flow")
        print("  (a)nnotate <text> Add/update annotation for the current flow")
        print("  (j)ump <index>  Jump to a specific flow by index (0-based)")
        print("  (s)earch <term> Search annotations, URLs, request/response bodies")
        print("  (e)xport <filename.md> Export all flows to a Markdown file")
        print("  (q)uit          Exit the program")
        
        try:
            command_input = input(f"\nEnter command (Flow {current_flow_index + 1}/{len(flows)}): ").strip()
            command_parts = command_input.split(" ", 1)
            command = command_parts[0].lower()
            argument = command_parts[1] if len(command_parts) > 1 else None

            if command == 'n':
                if current_flow_index < len(flows) - 1:
                    current_flow_index += 1
                else:
                    print("Already at the last flow.")
            elif command == 'p':
                if current_flow_index > 0:
                    current_flow_index -= 1
                else:
                    print("Already at the first flow.")
            elif command == 'a':
                if argument is not None:
                    flows[current_flow_index].annotation = argument
                    print(f"Annotation updated for flow ID {flows[current_flow_index].id}.")
                else:
                    print("Usage: a <text_of_annotation>")
            elif command == 'j':
                if argument is not None:
                    try:
                        target_index = int(argument)
                        if 0 <= target_index < len(flows):
                            current_flow_index = target_index
                        else:
                            print(f"Invalid index. Must be between 0 and {len(flows) - 1}.")
                    except ValueError:
                        print("Invalid index format. Must be an integer.")
                else:
                    print("Usage: j <index>")
            elif command == 's':
                if argument is not None:
                    search_term = argument.lower()
                    print(f"\n--- Search Results for '{search_term}' ---")
                    found_count = 0
                    for idx, flow_item in enumerate(flows):
                        match = False
                        if search_term in flow_item.annotation.lower():
                            match = True
                        if search_term in flow_item.request.url.lower():
                            match = True
                        
                        # Search request body
                        if flow_item.request.body:
                            if isinstance(flow_item.request.body, (dict, list)):
                                if search_term in json.dumps(flow_item.request.body).lower():
                                    match = True
                            elif isinstance(flow_item.request.body, bytes):
                                try:
                                    if search_term in flow_item.request.body.decode('utf-8', 'ignore').lower():
                                        match = True
                                except: pass # Ignore decode errors for search
                            elif isinstance(flow_item.request.body, str):
                                if search_term in flow_item.request.body.lower():
                                    match = True
                        
                        # Search response body
                        if flow_item.response and flow_item.response.body:
                            if isinstance(flow_item.response.body, (dict, list)):
                                if search_term in json.dumps(flow_item.response.body).lower():
                                    match = True
                            elif isinstance(flow_item.response.body, bytes):
                                try:
                                    if search_term in flow_item.response.body.decode('utf-8', 'ignore').lower():
                                        match = True
                                except: pass
                            elif isinstance(flow_item.response.body, str):
                                if search_term in flow_item.response.body.lower():
                                    match = True

                        if match:
                            found_count +=1
                            print(f"  Match {found_count} (Index {idx}): ID={flow_item.id}, URL={flow_item.request.url[:70]}..., Annotation='{flow_item.annotation[:50]}...'")
                    if found_count == 0:
                        print("No flows found matching your search term.")
                    print("--- End of Search Results ---")
                else:
                    print("Usage: s <search_term>")
            
            elif command == 'e':
                if argument:
                    output_filename = argument
                    if not output_filename.endswith(".md"):
                        output_filename += ".md"
                    
                    success = export_to_markdown(flows, output_filename)
                    if success:
                        print(f"Successfully exported {len(flows)} flows to {output_filename}")
                    else:
                        print(f"Failed to export flows to {output_filename}.")
                else:
                    print("Usage: e <filename.md>")

            elif command == 'q':
                print("Exiting.")
                break
            else:
                print("Invalid command. Type 'n', 'p', 'a', 'j', 's', 'e', or 'q'.")

        except KeyboardInterrupt:
            print("\nExiting due to KeyboardInterrupt.")
            break
        except EOFError: # Handle Ctrl+D
            print("\nExiting due to EOF.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the command loop: {e}", file=sys.stderr)
            # Optionally, continue or break depending on severity
            # break


if __name__ == "__main__":
    # For direct execution, ensure mitm_enhancer package context for imports
    # This might require running as `python -m mitm_enhancer.main <args>` from parent dir
    # or having the project root in PYTHONPATH.
    
    # Ensure exporter.py is found if running directly and it's in the same package
    try:
        from .exporter import export_to_markdown # Test if relative import works
    except ImportError:
        # Fallback if running main.py directly in its directory for dev
        try:
            from exporter import export_to_markdown
        except ImportError as e_local:
             print(f"Warning: Could not perform local exporter import: {e_local}")


    try:
        main_cli()
    except ImportError as e:
        # This complex check is to provide helpful messages if running `python mitm_enhancer/main.py`
        # instead of `python -m mitm_enhancer.main`
        if "parser" in str(e) or "models" in str(e) or "exporter" in str(e):
             print("Could not run main.py directly due to relative import issues. Try running as a module from the project root:")
             print("  python -m mitm_enhancer.main <flow_file_path>")
             print(f"Original error: {e}")
        else:
            # Re-raise other import errors not related to typical relative import issues
            raise
    except NameError as ne: # Catches if export_to_markdown wasn't successfully imported above
        if 'export_to_markdown' in str(ne):
            print("Error: export_to_markdown function not found. Ensure exporter.py is present and correctly imported.")
        else:
            raise
