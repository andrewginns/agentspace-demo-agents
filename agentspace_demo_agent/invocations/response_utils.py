#!/usr/bin/env python3
"""
Utility functions for processing and displaying agent responses.
"""

from typing import List, Tuple, Any, Iterator, Dict


def process_stream_response(
    stream_events: Iterator[Dict[str, Any]],
) -> List[Tuple[str, Any]]:
    """Process streaming response events and extract response parts.

    Args:
        stream_events: Iterator of streaming response events.

    Returns:
        List of tuples containing (part_type, part_content).
    """
    response_parts = []
    for event in stream_events:
        # Extract all parts from the event
        if isinstance(event, dict) and "content" in event:
            content = event["content"]
            if "parts" in content:
                for part in content["parts"]:
                    if "text" in part:
                        response_parts.append(("text", part["text"].strip()))
                    elif "function_call" in part:
                        func_call = part["function_call"]
                        response_parts.append(
                            (
                                "function_call",
                                {
                                    "name": func_call.get("name", "unknown"),
                                    "args": func_call.get("args", {}),
                                },
                            )
                        )
                    else:
                        # Handle any other part types
                        response_parts.append(("other", part))
    return response_parts


def display_response_parts(response_parts: List[Tuple[str, Any]]) -> None:
    """Display processed response parts in a formatted way.

    Args:
        response_parts: List of tuples containing (part_type, part_content).
    """
    if response_parts:
        for part_type, part_content in response_parts:
            if part_type == "text":
                print(f"Response: {part_content}")
            elif part_type == "function_call":
                print(f"Function Call: {part_content['name']}")
                print(f"  Args: {part_content['args']}")
            else:
                print(f"Other part: {part_content}")
    else:
        print("No response received")
