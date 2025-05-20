import json
from datetime import timedelta


def json_processor(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)
        
    # Extract just the text part from each
    cleaned_texts = [
        item["text"].strip()
        for item in raw_data
        if isinstance (item, dict) and "text" in item and isinstance(item["text"], str)
    ]
    
    # Join them into a single context block 
    full_context = "\n\n".join(cleaned_texts)
    return full_context

# format the time
def format_time(seconds):
    return str(timedelta(seconds=round(seconds)))

def json_processor_with_time(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        raw_data = json.load(file)
        
    formatted_entries = []
    
    for item in raw_data:
        if not isinstance(item, dict):
            continue # skip malformed entries
        text = item.get("text", "").strip()
        start_time = item.get("start", 0)
        duration = item.get("duration", 0)
        
        if not text:
            continue
        
        time_str = format_time(start_time)
        duration_str = f"{round(duration)}s"
        formatted_entries.append(f"[{time_str} for {duration_str}]\n{text}\n")
    
    
    formatted = "\n".join(formatted_entries) 
    return formatted

