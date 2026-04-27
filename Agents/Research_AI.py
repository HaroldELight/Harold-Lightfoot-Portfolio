import os
from dotenv import load_dotenv, find_dotenv
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import urllib.parse
import google.generativeai as genai
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class ResearchAI:
    def __init__(self, model: str = 'gemini'):
        load_dotenv(find_dotenv())
        self.model = model.lower()
        self.setup_model()

    def ask_for_gemini_key(self) -> str:
        api_key = os.getenv('GEMINI_API_KEY', '').strip()
        if api_key:
            return api_key

        api_key = input("No Gemini API key found in .env. Enter your Gemini API key: ").strip()
        if not api_key:
            raise ValueError("Gemini API key is required for online mode.")

        return api_key

    def setup_model(self):
        if self.model == 'gemini':
            api_key = self.ask_for_gemini_key()
            genai.configure(api_key=api_key)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
            self.ollama_model = self.model

    def fetch_webpage_content(self, url: str) -> str:
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

    def summarize_with_gemini(self, topic: str, text: str, length_choice: str, use_training: bool = False) -> str:
        if use_training:
            prompt = self.build_training_prompt(topic, length_choice)
        else:
            prompt = self.build_summary_prompt(topic, text, length_choice)
        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error summarizing with Gemini: {str(e)}"

    def summarize_with_ollama(self, topic: str, text: str, length_choice: str, use_training: bool = False, progress_callback=None) -> str:
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
            token_count = 0
            for line in response.iter_lines():
                if line:
                    data = __import__('json').loads(line)
                    chunk = data.get('response', '')
                    full_response += chunk
                    token_count += 1
                    if progress_callback and token_count % 10 == 0:
                        progress_callback(f"📝 Generated {token_count * 4} characters...")
            return full_response
        except Exception as e:
            return f"Error summarizing with {self.ollama_model}: {str(e)}"

    def extract_key_points(self, summary: str) -> List[str]:
        prompt = f"Extract 3-5 key points from the following summary:\n\n{summary}"
        if self.model == 'gemini':
            try:
                response = self.genai_model.generate_content(prompt)
                points_text = response.text
            except:
                points_text = summary
        else:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
            try:
                response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
                result = response.json()
                points_text = result.get('response', summary)
            except:
                points_text = summary

        # Parse the points
        lines = points_text.split('\n')
        points = [line.strip('- •').strip() for line in lines if line.strip() and not line.lower().startswith(('key points', 'points'))]
        return points[:5]  # Limit to 5 points

    @staticmethod
    def get_user_topic() -> str:
        topic = input("Enter the research topic: ").strip()
        while not topic:
            topic = input("Please enter a valid research topic: ").strip()
        return topic

    @staticmethod
    def choose_api_mode() -> str:
        choice = input("Use local or online API? [local/online]: ").strip().lower()
        while choice not in ('local', 'online', 'l', 'o'):
            choice = input("Please enter 'local' or 'online': ").strip().lower()
        return 'qwen2.5:3b' if choice in ('local', 'l') else 'gemini'

    @staticmethod
    def format_wikipedia_topic(topic: str) -> str:
        article_title = topic.strip().rstrip('.?').replace(' ', '_')
        return urllib.parse.quote(article_title)

    @staticmethod
    def get_summary_length_choice() -> str:
        choice = input("Enter summary length in pages (1-5) or 'preview' for one paragraph: ").strip().lower()
        if choice == 'preview':
            return 'preview'
        while not (choice.isdigit() and 1 <= int(choice) <= 5):
            choice = input("Please enter 1-5 or 'preview': ").strip().lower()
            if choice == 'preview':
                return 'preview'
        return choice

    @staticmethod
    def get_default_urls(topic: str) -> List[str]:
        article_title = ResearchAI.format_wikipedia_topic(topic)
        wiki_url = f"https://en.wikipedia.org/wiki/{article_title}"
        openalex_url = f"https://api.openalex.org/search?q={urllib.parse.quote(topic)}"
        return [wiki_url, openalex_url]

    @staticmethod
    def get_urls_from_user(topic: str) -> List[str]:
        choice = input("Use default Wikipedia URLs for this topic? [y/n]: ").strip().lower()
        if choice in ('y', 'yes'):
            urls = ResearchAI.get_default_urls(topic)
            print("Using URLs:")
            for url in urls:
                print(f" - {url}")
            return urls

        raw = input("Enter one or more URLs separated by commas: ").strip()
        urls = [url.strip() for url in raw.split(',') if url.strip()]
        while not urls:
            raw = input("You must enter at least one URL: ").strip()
            urls = [url.strip() for url in raw.split(',') if url.strip()]
        return urls

    def research_and_summarize(self, urls: List[str], topic: str, length_choice: str, progress_callback=None) -> str:
        if progress_callback:
            progress_callback("🔍 Currently searching...")

        all_content = f"Research topic: {topic}\n\n"
        successful_fetches = 0
        
        # Fetch URLs in parallel for faster execution
        with ThreadPoolExecutor(max_workers=min(5, len(urls))) as executor:
            future_to_url = {executor.submit(self.fetch_webpage_content, url): url for url in urls}
            for index, future in enumerate(as_completed(future_to_url), start=1):
                url = future_to_url[future]
                if progress_callback:
                    progress_callback(f"🔎 Fetching content {index}/{len(urls)}...")
                try:
                    content = future.result()
                    if not content.startswith("Error"):
                        successful_fetches += 1
                    all_content += f"\n\nContent from {url}:\n{content}"
                except Exception as e:
                    all_content += f"\n\nContent from {url}:\nError fetching content: {str(e)}"

        # Check if we got any valid content
        use_training_data = successful_fetches == 0

        if progress_callback:
            progress_callback("📄 Processing retrieved content...")
            progress_callback("🧠 Preparing the summary prompt...")

        if use_training_data and progress_callback:
            progress_callback("⚠️ No relevant content found in URLs.")
            progress_callback("💭 Using model knowledge to generate response...")

        if self.model == 'gemini':
            if progress_callback:
                progress_callback("✍️ Generating answer with Gemini...")
            summary = self.summarize_with_gemini(topic, all_content, length_choice, use_training=use_training_data)
        else:
            if progress_callback:
                progress_callback(f"✍️ Generating answer with {self.ollama_model}...")
                progress_callback("⏳ Processing tokens...")
            summary = self.summarize_with_ollama(topic, all_content, length_choice, use_training=use_training_data, progress_callback=progress_callback)

        if progress_callback:
            progress_callback("✏️ Finalizing output...")

        # Format the output as plain text
        output = f"{summary}\n\nSources:\n"
        if use_training_data:
            output += "- Model training data (no internet access)\n"
        else:
            for url in urls:
                output += f"- {url}\n"

        return output

def run_research_ui():
    root = tk.Tk()
    root.title("Research AI")
    root.geometry("1000x600")

    main_frame = tk.Frame(root, padx=12, pady=12)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(main_frame, text="Research Topic:").grid(row=0, column=0, sticky="w")
    topic_var = tk.StringVar()
    topic_entry = tk.Entry(main_frame, textvariable=topic_var, width=50)
    topic_entry.grid(row=0, column=1, columnspan=3, sticky="we", pady=4)

    tk.Label(main_frame, text="Model:").grid(row=1, column=0, sticky="w")
    mode_var = tk.StringVar(value="Qwen (Local)")
    mode_menu = tk.OptionMenu(main_frame, mode_var, "Gemini (online)", "Qwen (Local)")
    mode_menu.grid(row=1, column=1, sticky="w")

    tk.Label(main_frame, text="Summary Length:").grid(row=1, column=2, sticky="w")
    length_var = tk.StringVar(value="preview")
    length_menu = tk.OptionMenu(main_frame, length_var, "preview", "1 page", "2 pages", "3 pages", "4 pages", "5 pages")
    length_menu.grid(row=1, column=3, sticky="w")

    wiki_var = tk.BooleanVar(value=True)
    wiki_check = tk.Checkbutton(main_frame, text="Use default URLs (Wikipedia + OpenAlex)", variable=wiki_var)
    wiki_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=4)

    tk.Label(main_frame, text="Custom URLs (comma separated):").grid(row=3, column=0, sticky="nw")
    urls_text = tk.Text(main_frame, width=60, height=3, wrap=tk.WORD)
    urls_text.grid(row=3, column=1, columnspan=3, pady=4, sticky="we")

    # Progress box on the left, Output box on the right
    progress_label = tk.Label(main_frame, text="Status:", font=("Arial", 9, "bold"))
    progress_label.grid(row=4, column=0, sticky="nw", pady=(10, 0))
    
    progress_text = scrolledtext.ScrolledText(main_frame, width=20, height=18, wrap=tk.WORD, 
                                              bg="#f0f0f0", font=("Courier", 8))
    progress_text.grid(row=4, column=0, sticky="nsew", pady=(30, 0), padx=(0, 5))
    progress_text.config(state=tk.DISABLED)

    tk.Label(main_frame, text="Output:").grid(row=4, column=1, sticky="nw", pady=(10, 0))
    output_text = scrolledtext.ScrolledText(main_frame, width=80, height=18, wrap=tk.WORD)
    output_text.grid(row=4, column=1, columnspan=3, pady=(30, 0), sticky="nsew")

    main_frame.grid_columnconfigure(0, weight=0)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_columnconfigure(2, weight=0)
    main_frame.grid_columnconfigure(3, weight=0)
    main_frame.grid_rowconfigure(4, weight=1)

    generate_button = tk.Button(main_frame, text="Generate Summary")
    generate_button.grid(row=5, column=0, columnspan=4, pady=12)

    def set_ui_state(enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        topic_entry.config(state=state)
        mode_menu.config(state=state)
        length_menu.config(state=state)
        wiki_check.config(state=state)
        urls_text.config(state=state)
        generate_button.config(state=state)

    def on_generate():
        topic = topic_var.get().strip()
        if not topic:
            messagebox.showerror("Input Error", "Please enter a research topic.")
            return

        length_choice = length_var.get()
        if length_choice == 'preview':
            normalized_length = 'preview'
        else:
            normalized_length = length_choice.split()[0]

        if normalized_length not in ('preview', '1', '2', '3', '4', '5'):
            messagebox.showerror("Input Error", "Please select a valid summary length.")
            return

        if wiki_var.get():
            urls = ResearchAI.get_default_urls(topic)
        else:
            raw = urls_text.get("1.0", tk.END).strip()
            urls = [url.strip() for url in raw.split(',') if url.strip()]
            if not urls:
                messagebox.showerror("Input Error", "Please enter at least one URL or enable default URLs.")
                return

        model_mapping = {
            "Gemini (online)": "gemini",
            "Qwen (Local)": "qwen2.5:3b"
        }
        selected_model = model_mapping.get(mode_var.get(), mode_var.get().lower())

        progress_text.config(state=tk.NORMAL)
        progress_text.delete("1.0", tk.END)
        progress_text.config(state=tk.DISABLED)
        
        output_text.delete("1.0", tk.END)
        set_ui_state(False)

        def progress_callback(msg):
            def update_progress():
                progress_text.config(state=tk.NORMAL)
                progress_text.insert(tk.END, msg + "\n")
                progress_text.see(tk.END)
                progress_text.config(state=tk.DISABLED)
            root.after(0, update_progress)

        def worker():
            try:
                researcher = ResearchAI(model=selected_model)
                output = researcher.research_and_summarize(urls, topic, normalized_length, progress_callback)
            except Exception as exc:
                output = f"Error: {exc}"

            def update_ui():
                progress_text.config(state=tk.NORMAL)
                progress_text.insert(tk.END, "\n✓ Complete")
                progress_text.see(tk.END)
                progress_text.config(state=tk.DISABLED)
                
                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, output)
                set_ui_state(True)

            root.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

    generate_button.config(command=on_generate)
    topic_entry.bind("<Return>", lambda event: on_generate())
    root.mainloop()

if __name__ == "__main__":
    run_research_ui()