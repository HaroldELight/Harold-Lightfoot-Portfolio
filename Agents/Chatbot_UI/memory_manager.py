import json
import os
import uuid
from datetime import datetime
import re
from typing import List, Dict, Any

class MemoryManager:
    """Advanced memory system for continuous learning Personal Assistant"""
    
    def __init__(self, memory_dir="memory"):
        self.memory_dir = memory_dir
        self.global_memory_file = os.path.join(memory_dir, "global_memory.json")
        self.personal_facts_file = os.path.join(memory_dir, "personal_facts.json")
        self.topics_file = os.path.join(memory_dir, "topics.json")
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing memories
        self.load_memories()
    
    def load_memories(self):
        """Load all memory systems"""
        self.global_memory = self.load_json(self.global_memory_file, {
            "conversations": [],
            "total_messages": 0,
            "last_updated": None
        })
        
        self.personal_facts = self.load_json(self.personal_facts_file, {
            "name": None,
            "preferences": {},
            "patterns": {},
            "facts_learned": {}
        })
        
        self.topics = self.load_json(self.topics_file, {
            "topics": {},
            "last_updated": None
        })
    
    def load_json(self, filepath, default):
        """Load JSON file with fallback to default"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        return default
    
    def save_memories(self):
        """Save all memory systems"""
        self.save_json(self.global_memory_file, self.global_memory)
        self.save_json(self.personal_facts_file, self.personal_facts)
        self.save_json(self.topics_file, self.topics)
    
    def save_json(self, filepath, data):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def add_conversation(self, conversation_id: str, messages: List[Dict]):
        """Add conversation to global memory and extract insights"""
        # Add to global memory
        conversation_entry = {
            "id": conversation_id,
            "messages": messages,
            "created_at": datetime.now().isoformat(),
            "message_count": len(messages)
        }
        
        self.global_memory["conversations"].append(conversation_entry)
        self.global_memory["total_messages"] += len(messages)
        self.global_memory["last_updated"] = datetime.now().isoformat()
        
        # Extract personal facts and patterns
        self.extract_personal_facts(messages)
        
        # Extract topic information
        self.extract_topics(messages)
        
        # Save updated memories
        self.save_memories()
    
    def extract_personal_facts(self, messages: List[Dict]):
        """Extract personal facts from conversation"""
        for message in messages:
            if message["role"] == "user":
                content = message["content"].lower()
                
                # Extract name
                if "my name is" in content:
                    name_match = re.search(r"my name is (\w+)", content)
                    if name_match:
                        self.personal_facts["name"] = name_match.group(1).title()
                
                # Extract preferences
                if "i like" in content:
                    likes = re.findall(r"i like ([^.!?]+)", content)
                    for like in likes:
                        self.personal_facts["preferences"]["likes"] = self.personal_facts["preferences"].get("likes", [])
                        if like.strip() not in self.personal_facts["preferences"]["likes"]:
                            self.personal_facts["preferences"]["likes"].append(like.strip())
                
                if "i don't like" in content or "i hate" in content:
                    dislikes = re.findall(r"(?:i don't like|i hate) ([^.!?]+)", content)
                    for dislike in dislikes:
                        self.personal_facts["preferences"]["dislikes"] = self.personal_facts["preferences"].get("dislikes", [])
                        if dislike.strip() not in self.personal_facts["preferences"]["dislikes"]:
                            self.personal_facts["preferences"]["dislikes"].append(dislike.strip())
                
                # Extract facts about user
                if "i am" in content:
                    facts = re.findall(r"i am ([^.!?]+)", content)
                    for fact in facts:
                        fact_key = f"personal_fact_{len(self.personal_facts['facts_learned'])}"
                        self.personal_facts["facts_learned"][fact_key] = {
                            "fact": fact.strip(),
                            "timestamp": datetime.now().isoformat(),
                            "context": message["content"]
                        }
    
    def extract_topics(self, messages: List[Dict]):
        """Extract topic information from conversation"""
        # Simple topic extraction based on keywords
        topic_keywords = {
            "technology": ["computer", "software", "programming", "code", "ai", "machine learning"],
            "science": ["physics", "chemistry", "biology", "research", "experiment"],
            "business": ["work", "job", "career", "company", "business", "project"],
            "personal": ["family", "friend", "relationship", "personal", "life"],
            "entertainment": ["movie", "music", "game", "book", "show"],
            "health": ["health", "exercise", "diet", "medical", "doctor"]
        }
        
        for message in messages:
            content = message["content"].lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in content for keyword in keywords):
                    if topic not in self.topics["topics"]:
                        self.topics["topics"][topic] = {
                            "message_count": 0,
                            "last_discussed": None,
                            "key_points": []
                        }
                    
                    self.topics["topics"][topic]["message_count"] += 1
                    self.topics["topics"][topic]["last_discussed"] = datetime.now().isoformat()
                    
                    # Add key points (simplified)
                    if len(message["content"]) > 50:  # Only substantial messages
                        self.topics["topics"][topic]["key_points"].append({
                            "content": message["content"][:200],  # Truncate for storage
                            "timestamp": message["timestamp"],
                            "role": message["role"]
                        })
        
        self.topics["last_updated"] = datetime.now().isoformat()
    
    def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Search global memory for relevant conversations"""
        query_lower = query.lower()
        results = []
        
        for conversation in self.global_memory["conversations"]:
            relevance_score = 0
            matching_messages = []
            
            for message in conversation["messages"]:
                message_content = message["content"].lower()
                
                # Calculate relevance based on keyword matches
                if query_lower in message_content:
                    relevance_score += 10
                    matching_messages.append(message)
                else:
                    # Check for partial word matches
                    query_words = query_lower.split()
                    for word in query_words:
                        if word in message_content:
                            relevance_score += 2
                            matching_messages.append(message)
                            break
            
            if relevance_score > 0:
                results.append({
                    "conversation_id": conversation["id"],
                    "relevance_score": relevance_score,
                    "matching_messages": matching_messages[:3],  # Limit matches
                    "created_at": conversation["created_at"]
                })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
    
    def get_personal_context(self) -> str:
        """Get personal context for conversation"""
        context_parts = []
        
        if self.personal_facts["name"]:
            context_parts.append(f"The user's name is {self.personal_facts['name']}")
        
        if self.personal_facts["preferences"].get("likes"):
            likes = ", ".join(self.personal_facts["preferences"]["likes"][:5])
            context_parts.append(f"The user likes: {likes}")
        
        if self.personal_facts["preferences"].get("dislikes"):
            dislikes = ", ".join(self.personal_facts["preferences"]["dislikes"][:5])
            context_parts.append(f"The user dislikes: {dislikes}")
        
        if self.personal_facts["facts_learned"]:
            recent_facts = list(self.personal_facts["facts_learned"].values())[-3:]
            fact_texts = [f"User mentioned: {fact['fact']}" for fact in recent_facts]
            context_parts.extend(fact_texts)
        
        return "\n".join(context_parts)
    
    def get_topic_context(self, query: str) -> str:
        """Get topic context based on query"""
        query_lower = query.lower()
        relevant_topics = []
        
        for topic, data in self.topics["topics"].items():
            # Check if query relates to this topic
            topic_keywords = {
                "technology": ["computer", "software", "programming", "code", "ai"],
                "science": ["physics", "chemistry", "biology", "research"],
                "business": ["work", "job", "career", "company"],
                "personal": ["family", "friend", "relationship"],
                "entertainment": ["movie", "music", "game", "book"],
                "health": ["health", "exercise", "diet", "medical"]
            }
            
            if topic in topic_keywords:
                keywords = topic_keywords[topic]
                if any(keyword in query_lower for keyword in keywords):
                    relevant_topics.append((topic, data))
        
        if relevant_topics:
            context_parts = []
            for topic, data in relevant_topics:
                context_parts.append(f"Previously discussed {topic}: {data['message_count']} times")
                
                # Add recent key points
                recent_points = data["key_points"][-2:]
                for point in recent_points:
                    context_parts.append(f"About {topic}: {point['content'][:100]}...")
            
            return "\n".join(context_parts)
        
        return ""
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about the memory system"""
        return {
            "total_conversations": len(self.global_memory["conversations"]),
            "total_messages": self.global_memory["total_messages"],
            "personal_facts_count": len(self.personal_facts["facts_learned"]),
            "topics_count": len(self.topics["topics"]),
            "last_updated": self.global_memory["last_updated"],
            "user_name": self.personal_facts["name"]
        }
    
    def get_relevant_context(self, query: str) -> str:
        """Get all relevant context for a query"""
        context_parts = []
        
        # Add personal context
        personal_context = self.get_personal_context()
        if personal_context:
            context_parts.append("=== PERSONAL CONTEXT ===")
            context_parts.append(personal_context)
        
        # Add topic context
        topic_context = self.get_topic_context(query)
        if topic_context:
            context_parts.append("\n=== TOPIC CONTEXT ===")
            context_parts.append(topic_context)
        
        # Add relevant past conversations
        search_results = self.search_memory(query, limit=2)
        if search_results:
            context_parts.append("\n=== RELEVANT PAST CONVERSATIONS ===")
            for result in search_results:
                context_parts.append(f"From {result['created_at'][:10]}:")
                for msg in result['matching_messages']:
                    context_parts.append(f"{msg['role'].title()}: {msg['content'][:100]}...")
        
        return "\n".join(context_parts)
