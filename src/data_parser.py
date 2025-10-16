import json
import datetime
import pandas as pd  # For easier timestamp handling and sorting

def load_conversations(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)  # List of conversation dicts
    
    conversations = []
    for conv in data:
        # Extract key info
        title = conv.get('title', 'Untitled')
        create_time = conv.get('create_time')  # Unix timestamp
        update_time = conv.get('update_time')
        
        # Convert timestamps to datetime for easier sorting/filtering
        create_dt = datetime.datetime.fromtimestamp(create_time) if create_time else None
        update_dt = datetime.datetime.fromtimestamp(update_time) if update_time else None
        
        # Reconstruct conversation thread (simple linear traversal)
        mapping = conv.get('mapping', {})
        current_node = conv.get('current_node')
        thread = []
        
        if current_node and mapping:
            node = mapping.get(current_node)
            while node:
                message = node.get('message')
                if message:
                    role = message['author']['role']
                    content_parts = message['content'].get('parts', [])
                    # Handle case where content_parts contains dictionaries
                    content_lines = []
                    for part in content_parts:
                        if isinstance(part, dict) and 'text' in part:
                            content_lines.append(part['text'])
                        elif isinstance(part, str):
                            content_lines.append(part)
                        else:
                            content_lines.append(str(part))  # Fallback for unexpected types
                    content = '\n'.join(content_lines)  # Join parts if multi-part
                    thread.append((role, content))
                # Go to parent for previous message
                parent_id = node.get('parent')
                node = mapping.get(parent_id) if parent_id else None
        
        # Reverse thread to chronological order (since we built from end)
        thread.reverse()
        
        conversations.append({
            'title': title,
            'create_time': create_dt,
            'update_time': update_dt,
            'thread': thread  # List of (role, content) tuples
        })
    
    # Convert to Pandas DataFrame for easy sorting/filtering
    df = pd.DataFrame(conversations)
    return df