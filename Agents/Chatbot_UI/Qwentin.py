import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import json
import os
import uuid
from datetime import datetime
import threading
from memory_manager import MemoryManager

class ChatbotGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("JARVIS - Digital Butler")
        self.window.geometry("800x600")
        self.window.configure(bg='#f0f0f0')
        
        # Configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen2.5:3b"
        self.memory_dir = "memory"
        self.max_context_messages = 10
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Conversation state
        self.current_conversation_id = None
        self.conversations = {}
        self.current_response = ""
        
        # Initialize Memory Manager for continuous learning
        self.memory_manager = MemoryManager(self.memory_dir)
        
        # Load existing conversations
        self.load_conversations()
        
        # Setup UI
        self.setup_ui()
        self.start_new_conversation()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="🤖 Qwentin", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="New Chat", command=self.start_new_conversation).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="History", command=self.show_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Memory", command=self.show_memory_manager).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save", command=self.save_conversation).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Load", command=self.load_conversation_dialog).pack(side=tk.LEFT, padx=2)
        
        # Chat area
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="5")
        chat_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=('Arial', 10),
            bg='white',
            state=tk.DISABLED
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for different message types
        self.chat_display.tag_configure('user', background='#e3f2fd', foreground='#1976d2', font=('Arial', 10, 'bold'))
        self.chat_display.tag_configure('assistant', background='#f5f5f5', foreground='#424242', font=('Arial', 10))
        self.chat_display.tag_configure('system', background='#fff3e0', foreground='#f57c00', font=('Arial', 9, 'italic'))
        
        # Input area
        input_frame = ttk.LabelFrame(main_frame, text="Your Message", padding="5")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_box = ttk.Entry(input_frame, font=('Arial', 10))
        self.input_box.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.input_box.bind('<Return>', lambda e: self.send_query())
        
        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_query)
        self.send_button.grid(row=0, column=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Check Ollama status
        self.check_ollama_status()
        
    def check_ollama_status(self):
        """Check if Ollama is running and Qwen is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                qwen_available = any(model['name'].startswith('qwen2.5') for model in models)
                if qwen_available:
                    self.status_var.set("✅ Connected to Qwen model")
                else:
                    self.status_var.set("⚠️ Ollama running but Qwen not found")
            else:
                self.status_var.set("❌ Ollama not responding")
        except requests.exceptions.RequestException:
            self.status_var.set("❌ Ollama not running. Start with: ollama serve")
    
    def load_conversations(self):
        """Load all existing conversations from memory directory"""
        for filename in os.listdir(self.memory_dir):
            if filename.endswith('.json'):
                conversation_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(self.memory_dir, filename), 'r', encoding='utf-8') as f:
                        self.conversations[conversation_id] = json.load(f)
                except Exception as e:
                    print(f"Error loading conversation {conversation_id}: {e}")
    
    def save_conversation_to_file(self, conversation_id, conversation_data):
        """Save conversation to file"""
        filename = os.path.join(self.memory_dir, f"{conversation_id}.json")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            self.conversations[conversation_id] = conversation_data
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def get_conversation(self, conversation_id):
        """Get conversation by ID"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        return {
            'id': conversation_id,
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def add_message(self, conversation_id, role, content):
        """Add message to conversation"""
        conversation = self.get_conversation(conversation_id)
        conversation['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        conversation['updated_at'] = datetime.now().isoformat()
        self.save_conversation_to_file(conversation_id, conversation)
        return conversation
    
    def get_context_messages(self, conversation_id):
        """Get recent messages for context"""
        conversation = self.get_conversation(conversation_id)
        messages = conversation['messages']
        return messages[-self.max_context_messages:] if len(messages) > self.max_context_messages else messages
    
    def query_ollama(self, prompt, context_messages=[], callback=None):
        """Query Ollama API with intelligent context from MemoryManager"""
        # Get relevant context from MemoryManager
        memory_context = self.memory_manager.get_relevant_context(prompt)
        
        # Build the full prompt with intelligent context
        full_prompt = ""
        if memory_context:
            full_prompt += f"=== MEMORY CONTEXT ===\n{memory_context}\n\n"
        
        if context_messages:
            full_prompt += "=== CURRENT CONVERSATION ===\nPrevious conversation:\n"
            for msg in context_messages[-5:]:  # Include last 5 messages for context
                full_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
        
        full_prompt += f"\n=== CURRENT MESSAGE ===\nUser: {prompt}\n\nYou are JARVIS - a formal AI Butler. Be concise and professional.\n\nKey traits:\n- Address user as 'Sir' or 'Madam'\n- Use formal, brief responses\n- Be direct and efficient\n- Maintain British etiquette\n- Stay calm and professional\n- Avoid unnecessary conversation\n\nUse memory context when relevant. Respond briefly and precisely."
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": True,  # Enable streaming
            "options": {
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=30, stream=True)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        chunk = data.get('response', '')
                        if chunk:
                            full_response += chunk
                            # Call callback with each chunk if provided
                            if callback:
                                self.window.after(0, callback, chunk)
                    except json.JSONDecodeError:
                        continue
            
            return full_response
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Ollama: {str(e)}. Please make sure Ollama is running."
            if callback:
                self.window.after(0, callback, error_msg)
            return error_msg
    
    def start_new_conversation(self):
        """Start a new conversation"""
        self.current_conversation_id = str(uuid.uuid4())
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.add_message_to_display('assistant', 'Sir?')
        self.chat_display.config(state=tk.DISABLED)
        self.status_var.set(f"New conversation started: {self.current_conversation_id[:8]}...")
    
    def send_query(self):
        """Send user query to chatbot"""
        query = self.input_box.get().strip()
        if not query:
            return
        
        # Clear input and disable send button
        self.input_box.delete(0, tk.END)
        self.send_button.config(state=tk.DISABLED)
        self.status_var.set("Thinking...")
        
        # Add user message to display
        self.add_message_to_display('user', query)
        
        # Process in separate thread to avoid freezing UI
        threading.Thread(target=self.process_query, args=(query,), daemon=True).start()
    
    def process_query(self, query):
        """Process query in background thread with streaming"""
        try:
            # Get context messages
            context_messages = self.get_context_messages(self.current_conversation_id)
            
            # Add user message to memory immediately
            self.add_message(self.current_conversation_id, 'user', query)
            
            # Start streaming response
            self.current_response = ""
            self.start_assistant_message()
            
            # Query Ollama with streaming callback
            response = self.query_ollama(query, context_messages, self.stream_response_chunk)
            
            # Finalize the response
            self.window.after(0, self.finalize_response, response)
            
        except Exception as e:
            self.window.after(0, self.display_error, str(e))
    
    def start_assistant_message(self):
        """Start a new assistant message for streaming"""
        timestamp = datetime.now().strftime("%H:%M")
        prefix = f"[{timestamp}] Assistant: "
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, prefix, 'assistant')
        self.chat_display.mark_set("stream_start", tk.END)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def stream_response_chunk(self, chunk):
        """Stream a chunk of text to the display"""
        self.current_response += chunk
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, chunk, 'assistant')
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def finalize_response(self, response):
        """Finalize the streaming response"""
        # Add complete response to memory
        self.add_message(self.current_conversation_id, 'assistant', response)
        
        # Add conversation to MemoryManager for continuous learning
        conversation = self.get_conversation(self.current_conversation_id)
        self.memory_manager.add_conversation(self.current_conversation_id, conversation['messages'])
        
        # Re-enable send button and update status
        self.send_button.config(state=tk.NORMAL)
        self.status_var.set("Ready")
        
        # Add final spacing
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_error(self, error):
        """Display error message"""
        self.add_message_to_display('system', f"Error: {error}")
        self.send_button.config(state=tk.NORMAL)
        self.status_var.set("Error occurred")
    
    def add_message_to_display(self, role, content):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        prefix = {
            'user': f"[{timestamp}] You: ",
            'assistant': f"[{timestamp}] Assistant: ",
            'system': f"[{timestamp}] System: "
        }.get(role, f"[{timestamp}] {role}: ")
        
        self.chat_display.insert(tk.END, prefix, role)
        self.chat_display.insert(tk.END, content + "\n\n", role)
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def save_conversation(self):
        """Save current conversation"""
        if self.current_conversation_id and self.current_conversation_id in self.conversations:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"chat_{self.current_conversation_id[:8]}.json"
            )
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.conversations[self.current_conversation_id], f, indent=2, ensure_ascii=False)
                    messagebox.showinfo("Success", f"Conversation saved to {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save: {e}")
    
    def load_conversation_dialog(self):
        """Load a conversation from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
                
                # Generate new ID and save to memory
                new_id = str(uuid.uuid4())
                conversation_data['id'] = new_id
                self.save_conversation_to_file(new_id, conversation_data)
                
                # Load and display
                self.load_conversation(new_id)
                messagebox.showinfo("Success", "Conversation loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")
    
    def load_conversation(self, conversation_id):
        """Load and display a conversation"""
        self.current_conversation_id = conversation_id
        conversation = self.get_conversation(conversation_id)
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        
        for msg in conversation['messages']:
            self.add_message_to_display(msg['role'], msg['content'])
        
        self.chat_display.config(state=tk.DISABLED)
        self.status_var.set(f"Loaded conversation: {conversation_id[:8]}...")
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversations:
            messagebox.showinfo("History", "No saved conversations found")
            return
        
        # Create history window
        history_window = tk.Toplevel(self.window)
        history_window.title("Conversation History")
        history_window.geometry("600x400")
        
        # Create treeview for history
        columns = ('ID', 'Messages', 'Last Updated')
        tree = ttk.Treeview(history_window, columns=columns, show='headings')
        tree.heading('ID', text='Conversation ID')
        tree.heading('Messages', text='Messages')
        tree.heading('Last Updated', text='Last Updated')
        
        tree.column('ID', width=150)
        tree.column('Messages', width=100)
        tree.column('Last Updated', width=200)
        
        # Add conversations to tree
        for conv_id, conv_data in self.conversations.items():
            last_updated = conv_data.get('updated_at', 'Unknown')
            try:
                # Format timestamp
                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_time = last_updated
            
            message_count = len(conv_data.get('messages', []))
            tree.insert('', tk.END, values=(conv_id[:8] + '...', message_count, formatted_time))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(history_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def load_selected():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                conv_id = item['values'][0].replace('...', '')  # Remove dots to get partial ID
                # Find full ID
                for full_id in self.conversations.keys():
                    if full_id.startswith(conv_id):
                        self.load_conversation(full_id)
                        history_window.destroy()
                        break
        
        def delete_selected():
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                conv_id = item['values'][0].replace('...', '')
                # Find full ID
                for full_id in self.conversations.keys():
                    if full_id.startswith(conv_id):
                        if messagebox.askyesno("Delete", "Delete this conversation?"):
                            # Delete file
                            filename = os.path.join(self.memory_dir, f"{full_id}.json")
                            try:
                                os.remove(filename)
                                del self.conversations[full_id]
                                tree.delete(selection[0])
                                if self.current_conversation_id == full_id:
                                    self.start_new_conversation()
                            except Exception as e:
                                messagebox.showerror("Error", f"Failed to delete: {e}")
                        break
        
        ttk.Button(button_frame, text="Load", command=load_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=history_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_memory_manager(self):
        """Show memory management interface"""
        memory_window = tk.Toplevel(self.window)
        memory_window.title("Memory Manager - Continuous Learning")
        memory_window.geometry("800x600")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(memory_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Stats tab
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Memory Stats")
        
        stats = self.memory_manager.get_memory_stats()
        
        stats_text = f"""
🧠 Personal Assistant Memory Statistics

Total Conversations: {stats['total_conversations']}
Total Messages: {stats['total_messages']}
Personal Facts Learned: {stats['personal_facts_count']}
Topics Discussed: {stats['topics_count']}

User Name: {stats['user_name'] or 'Not learned yet'}
Last Updated: {stats['last_updated'] or 'Never'}

📚 Memory Files:
• global_memory.json - All conversations
• personal_facts.json - User preferences and facts
• topics.json - Topic discussions
        """
        
        stats_display = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD, width=80, height=20)
        stats_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        stats_display.insert(tk.END, stats_text)
        stats_display.config(state=tk.DISABLED)
        
        # Personal Facts tab
        facts_frame = ttk.Frame(notebook)
        notebook.add(facts_frame, text="Personal Facts")
        
        facts_display = scrolledtext.ScrolledText(facts_frame, wrap=tk.WORD, width=80, height=20)
        facts_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        facts_text = "=== PERSONAL INFORMATION ===\n\n"
        if self.memory_manager.personal_facts["name"]:
            facts_text += f"Name: {self.memory_manager.personal_facts['name']}\n\n"
        
        facts_text += "=== PREFERENCES ===\n\n"
        preferences = self.memory_manager.personal_facts["preferences"]
        
        if preferences.get("likes"):
            facts_text += "Likes:\n"
            for like in preferences["likes"]:
                facts_text += f"  • {like}\n"
            facts_text += "\n"
        
        if preferences.get("dislikes"):
            facts_text += "Dislikes:\n"
            for dislike in preferences["dislikes"]:
                facts_text += f"  • {dislike}\n"
            facts_text += "\n"
        
        facts_text += "=== FACTS LEARNED ===\n\n"
        for fact_key, fact_data in self.memory_manager.personal_facts["facts_learned"].items():
            facts_text += f"• {fact_data['fact']}\n"
            facts_text += f"  (Learned: {fact_data['timestamp'][:10]})\n\n"
        
        facts_display.insert(tk.END, facts_text)
        facts_display.config(state=tk.DISABLED)
        
        # Topics tab
        topics_frame = ttk.Frame(notebook)
        notebook.add(topics_frame, text="Topics")
        
        topics_display = scrolledtext.ScrolledText(topics_frame, wrap=tk.WORD, width=80, height=20)
        topics_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        topics_text = "=== TOPICS DISCUSSED ===\n\n"
        for topic, data in self.memory_manager.topics["topics"].items():
            topics_text += f"📁 {topic.title()}\n"
            topics_text += f"   Messages: {data['message_count']}\n"
            topics_text += f"   Last discussed: {data['last_discussed'][:10] if data['last_discussed'] else 'Never'}\n"
            
            if data.get("key_points"):
                topics_text += "   Recent points:\n"
                for point in data["key_points"][-3:]:  # Show last 3 points
                    topics_text += f"     • {point['content'][:80]}...\n"
            topics_text += "\n"
        
        topics_display.insert(tk.END, topics_text)
        topics_display.config(state=tk.DISABLED)
        
        # Search tab
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="Search Memory")
        
        # Search controls
        search_controls = ttk.Frame(search_frame)
        search_controls.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_controls, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_controls, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self.search_memory_callback(search_entry.get(), search_results))
        
        ttk.Button(search_controls, text="Search", 
                  command=lambda: self.search_memory_callback(search_entry.get(), search_results)).pack(side=tk.LEFT, padx=5)
        
        # Search results
        search_results = scrolledtext.ScrolledText(search_frame, wrap=tk.WORD, width=80, height=15)
        search_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(memory_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=lambda: self.show_memory_manager()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=memory_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def search_memory_callback(self, query, results_display):
        """Callback for memory search"""
        if not query.strip():
            return
        
        results = self.memory_manager.search_memory(query, limit=10)
        
        results_display.config(state=tk.NORMAL)
        results_display.delete(1.0, tk.END)
        
        if results:
            results_display.insert(tk.END, f"🔍 Search Results for: '{query}'\n\n")
            
            for i, result in enumerate(results, 1):
                results_display.insert(tk.END, f"📄 Result {i} (Relevance: {result['relevance_score']})\n")
                results_display.insert(tk.END, f"Conversation ID: {result['conversation_id'][:8]}...\n")
                results_display.insert(tk.END, f"Date: {result['created_at'][:10]}\n\n")
                
                for msg in result['matching_messages']:
                    results_display.insert(tk.END, f"{msg['role'].title()}: {msg['content']}\n\n")
                
                results_display.insert(tk.END, "-" * 50 + "\n\n")
        else:
            results_display.insert(tk.END, f"🔍 No results found for: '{query}'")
        
        results_display.config(state=tk.DISABLED)
    
    def run(self):
        """Start the GUI"""
        self.window.mainloop()

def main():
    """Launch the Personal Assistant GUI with error handling"""
    try:
        # Create and run the GUI
        chatbot_gui = ChatbotGUI()
        chatbot_gui.run()
        
    except ImportError as e:
        # Show error in GUI if import fails
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror("Import Error", 
                           f"Failed to import required modules:\n{e}\n\n"
                           "Please ensure all required files are present:\n"
                           "- memory_manager.py\n"
                           "- requirements.txt installed")
        sys.exit(1)
        
    except Exception as e:
        # Show error in GUI if anything else fails
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror("Startup Error", 
                           f"Failed to start Personal Assistant:\n{e}\n\n"
                           "Please check:\n"
                           "- Ollama is running (ollama serve)\n"
                           "- Qwen model is installed (ollama pull qwen2.5:3b)")
        sys.exit(1)

if __name__ == "__main__":
    main()
