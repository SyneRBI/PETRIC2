#!/usr/bin/env python
"""
Extract DATA_SLICES dictionary from petric.py without importing heavy dependencies.
"""
import re

def extract_data_slices(filepath='petric.py'):
    """Extract DATA_SLICES dictionary from petric.py using eval on extracted text."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find DATA_SLICES = {...} block spanning multiple lines
    # Look for the start and find the matching closing brace
    start_pattern = r'DATA_SLICES\s*=\s*\{'
    start_match = re.search(start_pattern, content)
    
    if not start_match:
        raise ValueError("Could not find DATA_SLICES in petric.py")
    
    # Find the matching closing brace by counting braces
    start_pos = start_match.start()
    brace_count = 0
    in_dict = False
    end_pos = start_pos
    
    for i, char in enumerate(content[start_pos:], start=start_pos):
        if char == '{':
            brace_count += 1
            in_dict = True
        elif char == '}':
            brace_count -= 1
            if in_dict and brace_count == 0:
                end_pos = i + 1
                break
    
    # Extract the dictionary definition
    dict_text = content[start_pos:end_pos]
    
    # Use eval to parse it (safe since we're reading from a known file)
    # Extract just the dictionary part after the '='
    dict_only = dict_text.split('=', 1)[1].strip()
    
    # Evaluate the dictionary
    data_slices = eval(dict_only)
    
    return data_slices


if __name__ == '__main__':
    # Example usage
    DATA_SLICES = extract_data_slices()
    print("DATA_SLICES =", DATA_SLICES)
    
    # Access example
    print("\nSiemens_mMR_ACR slices:", DATA_SLICES.get("Siemens_mMR_ACR"))
