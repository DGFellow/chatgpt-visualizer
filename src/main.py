import tkinter as tk
from tkinter import ttk
from data_parser import load_conversations
import pandas as pd

class ChatVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChatGPT Visualizer")
        self.geometry("800x600")
        
        self.df = load_conversations('data/conversations.json')  # Load data
        self.filtered_df = self.df.copy()  # For filtering
        
        # Left pane: Conversation list
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.listbox = tk.Listbox(self.left_frame, width=40, height=30)
        self.listbox.pack(fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', self.display_conversation)
        
        self.update_listbox()  # Populate initially
        
        # Right pane: Conversation display
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_widget = tk.Text(self.right_frame, wrap=tk.WORD, height=30)
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.config(state=tk.DISABLED)  # Read-only
    
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for title in self.filtered_df['title']:
            self.listbox.insert(tk.END, title)
    
    def display_conversation(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            thread = self.filtered_df.iloc[index]['thread']
            
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            
            for role, content in thread:
                self.text_widget.insert(tk.END, f"{role.upper()}: ", 'bold')
                self.text_widget.insert(tk.END, f"{content}\n\n")
            
            self.text_widget.config(state=tk.DISABLED)
    
    # Tags for formatting (optional)
    def configure_tags(self):
        self.text_widget.tag_config('bold', font=('Arial', 10, 'bold'))

if __name__ == "__main__":
    app = ChatVisualizer()
    app.configure_tags()
    app.mainloop()