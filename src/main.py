import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
from data_parser import load_conversations

class ChatVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChatGPT Visualizer")
        self.geometry("1000x700")  # Slightly larger for new elements
        
        try:
            self.df = load_conversations('data/conversations.json')
        except FileNotFoundError:
            messagebox.showerror("Error", "conversations.json not found in data/")
            self.destroy()
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.destroy()
            return
        
        self.filtered_df = self.df.copy()
        self.sort_order = 'date_desc'  # Default sort: newest first
        self.keywords = []  # List of active keywords for filtering
        
        # Left pane: Controls and list
        self.left_frame = ttk.Frame(self, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Search bar
        ttk.Label(self.left_frame, text="Search Titles:").pack(anchor=tk.W)
        self.search_entry = ttk.Entry(self.left_frame)
        self.search_entry.pack(fill=tk.X)
        self.search_entry.bind('<KeyRelease>', self.apply_filters)
        
        # Sort dropdown
        ttk.Label(self.left_frame, text="Sort By:").pack(anchor=tk.W, pady=(10,0))
        self.sort_var = tk.StringVar(value='Date (Newest First)')
        sort_options = ['Date (Newest First)', 'Date (Oldest First)', 'Title (A-Z)']
        self.sort_dropdown = ttk.Combobox(self.left_frame, textvariable=self.sort_var, values=sort_options, state='readonly')
        self.sort_dropdown.pack(fill=tk.X)
        self.sort_dropdown.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Keyword filters
        ttk.Label(self.left_frame, text="Add Keyword Filter:").pack(anchor=tk.W, pady=(10,0))
        self.keyword_entry = ttk.Entry(self.left_frame)
        self.keyword_entry.pack(fill=tk.X)
        add_btn = ttk.Button(self.left_frame, text="Add Keyword", command=self.add_keyword)
        add_btn.pack(pady=5)
        
        self.keyword_frame = ttk.Frame(self.left_frame)
        self.keyword_frame.pack(fill=tk.X, pady=5)
        
        # Listbox with scrollbar
        ttk.Label(self.left_frame, text="Conversations:").pack(anchor=tk.W, pady=(10,0))
        self.list_scroll = ttk.Scrollbar(self.left_frame)
        self.listbox = tk.Listbox(self.left_frame, width=50, height=25, yscrollcommand=self.list_scroll.set)
        self.list_scroll.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', self.display_conversation)
        
        # Refresh button
        refresh_btn = ttk.Button(self.left_frame, text="Refresh Data", command=self.refresh_data)
        refresh_btn.pack(pady=10)
        
        self.apply_filters()  # Initial populate
        
        # Right pane: Conversation display with scrollbar
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_scroll = ttk.Scrollbar(self.right_frame)
        self.text_widget = tk.Text(self.right_frame, wrap=tk.WORD, yscrollcommand=self.text_scroll.set)
        self.text_scroll.config(command=self.text_widget.yview)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(state=tk.DISABLED)
        
        self.configure_tags()
    
    def configure_tags(self):
        self.text_widget.tag_config('bold', font=('Arial', 10, 'bold'))
    
    def refresh_data(self):
        try:
            self.df = load_conversations('data/conversations.json')
            self.apply_filters()
        except Exception as e:
            messagebox.showerror("Error", f"Reload failed: {e}")
    
    def add_keyword(self):
        kw = self.keyword_entry.get().strip()
        if kw and kw not in self.keywords:
            self.keywords.append(kw)
            self.update_keyword_display()
            self.keyword_entry.delete(0, tk.END)
            self.apply_filters()
    
    def remove_keyword(self, kw):
        self.keywords.remove(kw)
        self.update_keyword_display()
        self.apply_filters()
    
    def update_keyword_display(self):
        for widget in self.keyword_frame.winfo_children():
            widget.destroy()
        for kw in self.keywords:
            frame = ttk.Frame(self.keyword_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=kw).pack(side=tk.LEFT)
            remove_btn = ttk.Button(frame, text="X", width=2, command=lambda k=kw: self.remove_keyword(k))
            remove_btn.pack(side=tk.RIGHT)
    
    def apply_filters(self, event=None):
        # Filter by search
        search_term = self.search_entry.get().lower()
        df_temp = self.df if not search_term else self.df[self.df['title'].str.lower().str.contains(search_term)]
        
        # Filter by keywords (AND logic on titles)
        for kw in self.keywords:
            df_temp = df_temp[df_temp['title'].str.lower().str.contains(kw.lower())]
        
        # Sort
        sort_choice = self.sort_var.get()
        if sort_choice == 'Date (Newest First)':
            df_temp = df_temp.sort_values('create_time', ascending=False)
        elif sort_choice == 'Date (Oldest First)':
            df_temp = df_temp.sort_values('create_time', ascending=True)
        elif sort_choice == 'Title (A-Z)':
            df_temp = df_temp.sort_values('title', ascending=True)
        
        self.filtered_df = df_temp
        self.update_listbox()
    
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for disp_title in self.filtered_df['display_title']:
            self.listbox.insert(tk.END, disp_title)
    
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

if __name__ == "__main__":
    app = ChatVisualizer()
    app.mainloop()