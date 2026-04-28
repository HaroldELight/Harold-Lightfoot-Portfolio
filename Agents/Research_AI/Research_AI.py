import os
from dotenv import load_dotenv, find_dotenv
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import urllib.parse
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from urllib.parse import urlparse
import subprocess
import platform
import time
import google.generativeai as genai

class ResearchAI:
    def __init__(self, model: str = 'qwen2.5:3b'):
        load_dotenv(find_dotenv())
        self.model = model
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = model
        self.stop_requested = False
        self.genai_model = None
        self.working_gemini_model = None
        
        # Setup model based on type
        self.setup_model()

    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def start_ollama(self) -> bool:
        """Attempt to start Ollama service"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                # Try to start Ollama on Windows
                subprocess.Popen(["ollama", "serve"], shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            elif system in ["linux", "darwin"]:
                # Try to start Ollama on Linux/macOS
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a moment for Ollama to start
            time.sleep(3)
            
            # Check if it started successfully
            return self.check_ollama_status()
        except:
            return False

    def check_model_availability(self, model_name: str) -> bool:
        """Check if a specific model is available in Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model.get('name', '').startswith(model_name.split(':')[0]) for model in models)
            return False
        except:
            return False

    def pull_model(self, model_name: str, progress_callback=None) -> bool:
        """Download a model if not available"""
        try:
            if progress_callback:
                progress_callback(f"Downloading {model_name} model...")
            
            # Start the pull process
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # Monitor progress
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output and progress_callback:
                    progress_callback(f"Downloading: {output.strip()}")
            
            return process.returncode == 0
        except:
            return False

    def ensure_ollama_ready(self, progress_callback=None) -> bool:
        """Ensure Ollama is running and Qwen model is available"""
        # Check if Ollama is running
        if not self.check_ollama_status():
            if progress_callback:
                progress_callback("Ollama not running. Starting Ollama service...")
            
            if not self.start_ollama():
                return False
            
            if progress_callback:
                progress_callback("Ollama service started")
        
        # Check if Qwen model is available
        if not self.check_model_availability(self.ollama_model):
            if progress_callback:
                progress_callback(f"{self.ollama_model} model not found. Downloading...")
            
            if not self.pull_model(self.ollama_model, progress_callback):
                return False
            
            if progress_callback:
                progress_callback(f"{self.ollama_model} model ready")
        
        return True

    def setup_model(self):
        """Setup the appropriate model based on model type"""
        if self.model.startswith('gemini'):
            # Setup Gemini model
            self.setup_gemini_model()
        else:
            # Setup local Ollama model
            pass  # Already initialized in constructor

    def setup_gemini_model(self):
        """Setup Gemini model with fallback options"""
        api_key = os.getenv('GEMINI_API_KEY', '').strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Try models in order of preference
        model_names = [
            'gemini-2.5-flash',
            'gemini-flash-latest',
            'gemini-2.5-pro',
            'gemini-2.0-flash',
            'gemini-pro-latest'
        ]
        
        for model_name in model_names:
            try:
                test_model = genai.GenerativeModel(model_name)
                test_response = test_model.generate_content("test")
                self.genai_model = test_model
                self.working_gemini_model = model_name
                print(f"Successfully connected to Gemini model: {model_name}")
                return
            except Exception as e:
                print(f"Failed to connect to {model_name}: {e}")
                continue
        
        raise ValueError("No working Gemini model found")

    def validate_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def fetch_webpage_content(self, url: str) -> str:
        if self.stop_requested:
            return "Request stopped by user"
        
        if not self.validate_url(url):
            return f"Error: Invalid URL format: {url}"
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            return f"Error fetching content: {str(e)}"

    def build_summary_prompt(self, topic: str, text: str, length_choice: str) -> str:
        if length_choice == 'preview':
            return (
                f"Write a concise single-paragraph summary about '{topic}' (5-6 sentences).\n\n"
                f"Content:\n{text[:2000]}"
            )
        else:
            num_pages = int(length_choice)
            length_instruction = f"{num_pages * 2 + 1} to {num_pages * 3} paragraphs"
            
            return (
                f"Summarize '{topic}' in {length_instruction} with intro, body, and conclusion.\n\n"
                f"Content:\n{text[:3500]}"
            )

    def build_training_prompt(self, topic: str, length_choice: str) -> str:
        if length_choice == 'preview':
            return (
                f"Write a concise, single-paragraph summary about '{topic}' based on your knowledge. "
                f"Keep it brief and to the point – just one paragraph, no more than 5-6 sentences."
            )
        else:
            num_pages = int(length_choice)
            length_instruction = f"{num_pages * 2 + 1} to {num_pages * 3} paragraphs"
            detail_level = "comprehensive" if num_pages >= 3 else "detailed"
            
            return (
                f"Write a {detail_level} summary about '{topic}' based on your knowledge in {length_instruction}.\n\n"
                f"Begin with an introduction that sets up the topic, provide 2-4 body paragraphs with key information and details, "
                f"and end with a conclusion that summarizes the main points. Use clear paragraph breaks between sections. "
                f"Make the content informative and well-organized. Do not include section headers or labels."
            )

    def summarize_with_ollama(self, topic: str, text: str, length_choice: str, use_training: bool = False, stream_callback=None, progress_callback=None) -> str:
        if self.stop_requested:
            return "Request stopped by user"
            
        if use_training:
            prompt = self.build_training_prompt(topic, length_choice)
        else:
            prompt = self.build_summary_prompt(topic, text, length_choice)
            
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": True
        }
        
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=120, stream=True)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if self.stop_requested:
                    break
                if line:
                    data = __import__('json').loads(line)
                    chunk = data.get('response', '')
                    full_response += chunk
                    if stream_callback:
                        stream_callback(chunk)
            return full_response
        except Exception as e:
            return f"Error summarizing with {self.ollama_model}: {str(e)}"

    def summarize_with_gemini(self, topic: str, text: str, length_choice: str, use_training: bool = False, stream_callback=None) -> str:
        """Summarize content using Gemini model"""
        if self.stop_requested:
            return "Request stopped by user"
            
        if use_training:
            prompt = self.build_training_prompt(topic, length_choice)
        else:
            prompt = self.build_summary_prompt(topic, text, length_choice)
            
        try:
            response = self.genai_model.generate_content(prompt, stream=True)
            full_response = ""
            for chunk in response:
                if self.stop_requested:
                    break
                if chunk.text:
                    full_response += chunk.text
                    if stream_callback:
                        stream_callback(chunk.text)
            return full_response
        except Exception as e:
            return f"Error summarizing with Gemini: {str(e)}"

    def stop_request(self):
        self.stop_requested = True

    def reset_stop_flag(self):
        self.stop_requested = False

    def research_and_summarize(self, urls: List[str], topic: str, length_choice: str, progress_callback=None, stream_callback=None) -> str:
        self.reset_stop_flag()
        
        if progress_callback:
            progress_callback("🔍 Currently searching...")

        all_content = f"Research topic: {topic}\n\n"
        successful_fetches = 0
        
        # Fetch URLs in parallel for faster execution
        with ThreadPoolExecutor(max_workers=min(5, len(urls))) as executor:
            future_to_url = {executor.submit(self.fetch_webpage_content, url): url for url in urls}
            for index, future in enumerate(as_completed(future_to_url), start=1):
                if self.stop_requested:
                    break
                url = future_to_url[future]
                if progress_callback:
                    progress_callback(f"🔎 Fetching content {index}/{len(urls)}...")
                try:
                    content = future.result()
                    if not content.startswith("Error") and not content.startswith("Request stopped"):
                        successful_fetches += 1
                    all_content += f"\n\nContent from {url}:\n{content}"
                except Exception as e:
                    all_content += f"\n\nContent from {url}:\nError fetching content: {str(e)}"

        if self.stop_requested:
            return "Request stopped by user"

        # Check if we got any valid content
        use_training_data = successful_fetches == 0

        if progress_callback:
            progress_callback("📄 Processing retrieved content...")
            progress_callback("🧠 Preparing the summary prompt...")

        if use_training_data and progress_callback:
            progress_callback("⚠️ No relevant content found in URLs.")
            progress_callback("💭 Using model knowledge to generate response...")

        # Choose the right summarization method based on model type
        if self.model.startswith('gemini'):
            if progress_callback:
                progress_callback(f"✍️ Generating answer with {self.working_gemini_model}...")
                progress_callback("⏳ Processing tokens...")
            summary = self.summarize_with_gemini(topic, all_content, length_choice, use_training=use_training_data, stream_callback=stream_callback)
        else:
            if progress_callback:
                progress_callback(f"✍️ Generating answer with {self.ollama_model}...")
                progress_callback("⏳ Processing tokens...")
            summary = self.summarize_with_ollama(topic, all_content, length_choice, use_training=use_training_data, stream_callback=stream_callback, progress_callback=progress_callback)

        if self.stop_requested:
            return "Request stopped by user"

        if progress_callback:
            progress_callback("✏️ Finalizing output...")

        # Format the output as plain text
        output = f"{summary}\n\nSources:\n"
        if use_training_data:
            output += "- No relevant content found on provided URLs\n"
        else:
            for url in urls:
                output += f"- {url}\n"

        return output

    def llm_only_response(self, topic: str, length_choice: str, progress_callback=None, stream_callback=None) -> str:
        self.reset_stop_flag()
        
        if progress_callback:
            progress_callback("🧠 Using LLM training data only...")
            progress_callback("📝 Preparing summary prompt...")

        # Choose the right summarization method based on model type
        if self.model.startswith('gemini'):
            if progress_callback:
                progress_callback(f"✍️ Generating answer with {self.working_gemini_model}...")
                progress_callback("⏳ Processing tokens...")
            summary = self.summarize_with_gemini(topic, "", length_choice, use_training=True, stream_callback=stream_callback)
        else:
            if progress_callback:
                progress_callback(f"✍️ Generating answer with {self.ollama_model}...")
                progress_callback("⏳ Processing tokens...")
            summary = self.summarize_with_ollama(topic, "", length_choice, use_training=True, stream_callback=stream_callback, progress_callback=progress_callback)

        if self.stop_requested:
            return "Request stopped by user"

        if progress_callback:
            progress_callback("✏️ Finalizing output...")

        # Format the output as plain text
        output = f"{summary}\n\nSources:\n- LLM training data only\n"

        return output

    @staticmethod
    def get_default_urls(topic: str) -> List[str]:
        article_title = ResearchAI.format_wikipedia_topic(topic)
        wiki_url = f"https://en.wikipedia.org/wiki/{article_title}"
        openalex_url = f"https://api.openalex.org/search?q={urllib.parse.quote(topic)}"
        return [wiki_url, openalex_url]

    @staticmethod
    def format_wikipedia_topic(topic: str) -> str:
        article_title = topic.strip().rstrip('.?').replace(' ', '_')
        return urllib.parse.quote(article_title)

class ResearchGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Research AI")
        self.root.geometry("1000x600")
        self.researcher = None
        
        # Variables
        self.topic_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="Qwen (Local)")
        self.length_var = tk.StringVar(value="preview")
        self.wiki_var = tk.BooleanVar(value=True)
        self.llm_only_var = tk.BooleanVar(value=False)
        self.custom_urls_var = tk.BooleanVar(value=False)
        
        # Create GUI components
        self.setup_ui()
        self.setup_callbacks()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root, padx=12, pady=12)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        self.create_input_section(main_frame)
        
        # Output section
        self.create_output_section(main_frame)
        
        # Buttons
        self.create_button_section(main_frame)
        
    def create_input_section(self, parent):
        tk.Label(parent, text="Research Topic:").grid(row=0, column=0, sticky="w")
        self.topic_entry = tk.Entry(parent, textvariable=self.topic_var, width=50)
        self.topic_entry.grid(row=0, column=1, columnspan=3, sticky="we", pady=4)

        tk.Label(parent, text="Model:").grid(row=1, column=0, sticky="w")
        self.mode_menu = tk.OptionMenu(parent, self.mode_var, "Qwen (Local)", "Gemini (Online)")
        self.mode_menu.grid(row=1, column=1, sticky="w")

        tk.Label(parent, text="Summary Length:").grid(row=1, column=2, sticky="w")
        self.length_menu = tk.OptionMenu(parent, self.length_var, "preview", "1 page", "2 pages", "3 pages", "4 pages", "5 pages")
        self.length_menu.grid(row=1, column=3, sticky="w")

        # URL options row - side by side
        self.wiki_check = tk.Checkbutton(parent, text="Use default URLs (Wikipedia + OpenAlex)", variable=self.wiki_var, command=self.on_wiki_click)
        self.wiki_check.grid(row=2, column=0, sticky="w", pady=4)
        
        self.custom_urls_check = tk.Checkbutton(parent, text="Use custom URLs", variable=self.custom_urls_var, command=self.on_custom_urls_click)
        self.custom_urls_check.grid(row=2, column=1, sticky="w", pady=4, padx=(10, 0))
        
        self.llm_only_check = tk.Checkbutton(parent, text="LLM Only (skip web search)", variable=self.llm_only_var, command=self.on_checkbox_change)
        self.llm_only_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=4)

        tk.Label(parent, text="Custom URLs (comma separated):").grid(row=4, column=0, sticky="nw")
        self.urls_text = tk.Text(parent, width=60, height=3, wrap=tk.WORD)
        self.urls_text.grid(row=4, column=1, columnspan=3, pady=4, sticky="we")
        
    def create_output_section(self, parent):
        # Progress box on the left, Output box on the right
        progress_label = tk.Label(parent, text="Status:", font=("Arial", 9, "bold"))
        progress_label.grid(row=5, column=0, sticky="nw", pady=(10, 0))
        
        self.progress_text = scrolledtext.ScrolledText(parent, width=20, height=18, wrap=tk.WORD, 
                                                      bg="#f0f0f0", font=("Courier", 8))
        self.progress_text.grid(row=5, column=0, sticky="nsew", pady=(30, 0), padx=(0, 5))
        self.progress_text.config(state=tk.DISABLED)

        tk.Label(parent, text="Output:").grid(row=5, column=1, sticky="nw", pady=(10, 0))
        self.output_text = scrolledtext.ScrolledText(parent, width=80, height=18, wrap=tk.WORD)
        self.output_text.grid(row=5, column=1, columnspan=3, pady=(30, 0), sticky="nsew")

        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=0)
        parent.grid_columnconfigure(3, weight=0)
        parent.grid_rowconfigure(5, weight=1)

    def create_button_section(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.grid(row=6, column=0, columnspan=4, pady=12)
        
        self.generate_button = tk.Button(button_frame, text="Generate Summary")
        self.generate_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = tk.Button(button_frame, text="Stop", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.copy_button = tk.Button(button_frame, text="Copy Output")
        self.copy_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(button_frame, text="Clear Output")
        self.clear_button.pack(side=tk.LEFT, padx=5)

    def set_ui_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.topic_entry.config(state=state)
        self.mode_menu.config(state=state)
        self.length_menu.config(state=state)
        self.wiki_check.config(state=state)
        self.custom_urls_check.config(state=state)
        self.llm_only_check.config(state=state)
        self.urls_text.config(state=state)
        self.generate_button.config(state=state)
        self.stop_button.config(state=tk.NORMAL if not enabled else tk.DISABLED)
        self.copy_button.config(state=state)
        self.clear_button.config(state=state)
        
    def setup_callbacks(self):
        self.generate_button.config(command=self.on_generate)
        self.stop_button.config(command=self.on_stop)
        self.copy_button.config(command=self.on_copy)
        self.clear_button.config(command=self.on_clear)
        self.topic_entry.bind("<Return>", lambda event: self.on_generate())
        
        # Initialize checkbox states
        self.on_checkbox_change()
        
    def on_checkbox_change(self):
        """Handle mutually exclusive checkbox behavior"""
        if self.llm_only_var.get():
            # LLM only checked - unselect URL options but keep them enabled
            self.wiki_var.set(False)
            self.custom_urls_var.set(False)
            self.wiki_check.config(state=tk.NORMAL)
            self.custom_urls_check.config(state=tk.NORMAL)
            self.urls_text.config(state=tk.DISABLED)
        else:
            # LLM only unchecked - enable URL options
            self.wiki_check.config(state=tk.NORMAL)
            self.custom_urls_check.config(state=tk.NORMAL)
            # Enable URLs text box only if custom URLs is checked
            if self.custom_urls_var.get():
                self.urls_text.config(state=tk.NORMAL)
            else:
                self.urls_text.config(state=tk.DISABLED)
        
    def on_wiki_click(self):
        """Handle wiki checkbox click - auto uncheck LLM"""
        if self.wiki_var.get():
            self.llm_only_var.set(False)
            self.urls_text.config(state=tk.DISABLED)

    def on_custom_urls_click(self):
        """Handle custom URLs checkbox click - auto uncheck LLM"""
        if self.custom_urls_var.get():
            self.llm_only_var.set(False)
            self.urls_text.config(state=tk.NORMAL)
        
    def on_generate(self):
        topic = self.topic_var.get().strip()
        if not topic:
            messagebox.showerror("Input Error", "Please enter a research topic.")
            return

        length_choice = self.length_var.get()
        if length_choice == 'preview':
            normalized_length = 'preview'
        else:
            normalized_length = length_choice.split()[0]

        if normalized_length not in ('preview', '1', '2', '3', '4', '5'):
            messagebox.showerror("Input Error", "Please select a valid summary length.")
            return

        # Determine selected model
        mode_selection = self.mode_var.get()
        if mode_selection == "Gemini (Online)":
            selected_model = 'gemini-2.5-flash'  # Will be auto-detected in setup
        else:
            selected_model = 'qwen2.5:3b'  # Local model

        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete("1.0", tk.END)
        self.progress_text.config(state=tk.DISABLED)
        
        self.output_text.delete("1.0", tk.END)
        self.set_ui_state(False)

        def progress_callback(msg):
            def update_progress():
                self.progress_text.config(state=tk.NORMAL)
                self.progress_text.insert(tk.END, msg + "\n")
                self.progress_text.see(tk.END)
                self.progress_text.config(state=tk.DISABLED)
            self.root.after(0, update_progress)

        def stream_callback(chunk):
            def update_output():
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, chunk)
                self.output_text.see(tk.END)
                self.output_text.config(state=tk.DISABLED)
            self.root.after(0, update_output)

        def worker():
            try:
                self.researcher = ResearchAI(model=selected_model)
                
                # For local models, ensure Ollama is running and model is available
                if not selected_model.startswith('gemini'):
                    if not self.researcher.ensure_ollama_ready(progress_callback):
                        output = "Error: Failed to start Ollama or download required model. Please ensure Ollama is installed and accessible."
                        def update_ui_error():
                            self.output_text.config(state=tk.NORMAL)
                            self.output_text.delete("1.0", tk.END)
                            self.output_text.insert(tk.END, output)
                            self.output_text.config(state=tk.DISABLED)
                            self.set_ui_state(True)
                        self.root.after(0, update_ui_error)
                        return
                
                # Check if LLM-only mode is selected
                if self.llm_only_var.get():
                    # LLM-only mode, skip URL fetching
                    output = self.researcher.llm_only_response(topic, normalized_length, progress_callback, stream_callback)
                else:
                    # Normal mode with URLs
                    # Determine URLs to use
                    urls = []
                    
                    if self.custom_urls_var.get():
                        # Use custom URLs if checkbox is checked
                        raw_urls = self.urls_text.get("1.0", tk.END).strip()
                        custom_urls = [url.strip() for url in raw_urls.split(',') if url.strip()]
                        if custom_urls:
                            urls.extend(custom_urls)
                        else:
                            messagebox.showerror("Input Error", "Please enter custom URLs or uncheck custom URLs option.")
                            return
                    
                    if self.wiki_var.get():
                        # Use default URLs if wiki checkbox is checked
                        urls.extend(ResearchAI.get_default_urls(topic))
                    
                    if not urls:
                        messagebox.showerror("Input Error", "Please select either default URLs or custom URLs.")
                        return
                    
                    output = self.researcher.research_and_summarize(urls, topic, normalized_length, progress_callback, stream_callback)
                    
            except Exception as exc:
                output = f"Error: {exc}"

            def update_ui():
                self.progress_text.config(state=tk.NORMAL)
                self.progress_text.insert(tk.END, "\n✓ Complete")
                self.progress_text.see(tk.END)
                self.progress_text.config(state=tk.DISABLED)
                
                if not output.startswith("Error:"):
                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.insert(tk.END, f"\n\nSources:\n")
                    if "LLM training data only" in output:
                        self.output_text.insert(tk.END, "- LLM training data only\n")
                    elif "No relevant content found" in output:
                        self.output_text.insert(tk.END, "- No relevant content found on provided URLs\n")
                    else:
                        # Show URLs used in normal mode
                        if not self.llm_only_var.get():
                            if self.custom_urls_var.get():
                                raw_urls = self.urls_text.get("1.0", tk.END).strip()
                                custom_urls = [url.strip() for url in raw_urls.split(',') if url.strip()]
                                for url in custom_urls:
                                    self.output_text.insert(tk.END, f"- {url}\n")
                            if self.wiki_var.get():
                                default_urls = ResearchAI.get_default_urls(topic)
                                for url in default_urls:
                                    self.output_text.insert(tk.END, f"- {url}\n")
                    self.output_text.see(tk.END)
                    self.output_text.config(state=tk.DISABLED)
                else:
                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.delete("1.0", tk.END)
                    self.output_text.insert(tk.END, output)
                    self.output_text.config(state=tk.DISABLED)
                self.set_ui_state(True)

            self.root.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

    def on_stop(self):
        if self.researcher is not None:
            self.researcher.stop_request()
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.insert(tk.END, "\n⏹️ Request stopped by user")
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)
        self.set_ui_state(True)
    
    def on_clear(self):
        """Clear both progress and output text boxes"""
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete("1.0", tk.END)
        self.progress_text.config(state=tk.DISABLED)
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def on_copy(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Output copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No content to copy!")
    
    def run(self):
        self.root.mainloop()

def run_research_ui():
    app = ResearchGUI()
    app.run()

if __name__ == "__main__":
    run_research_ui()
