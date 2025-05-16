"""
Journal Manager Module
Handles creating, saving, and managing journal entries with bullet journal features.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class JournalManager:
    def __init__(self, journal_dir: str = "journals"):
        """Initialize the journal manager"""
        self.journal_dir = journal_dir
        self._ensure_journal_dir()

    def _ensure_journal_dir(self):
        """Ensure the journal directory exists"""
        Path(self.journal_dir).mkdir(parents=True, exist_ok=True)

    def _get_journal_path(self, date: datetime) -> str:
        """Get the path for a journal file based on date"""
        return os.path.join(self.journal_dir, f"{date.strftime('%Y-%m')}", f"{date.strftime('%Y-%m-%d')}.json")

    def create_entry(self, 
                    text: str, 
                    emotion_analysis: Dict,
                    date: Optional[datetime] = None,
                    tasks: List[Dict] = None,
                    goals: List[Dict] = None,
                    tags: List[str] = None,
                    category: str = "daily",
                    chat_history: Optional[List[Dict]] = None,
                    ai_summary: Optional[str] = None) -> Dict:
        """
        Create a new journal entry
        
        Args:
            text: The main journal text
            emotion_analysis: Dict containing emotion analysis {
                "primary_emotion": str,
                "emotion_intensity": int (1-10),
                "emotional_themes": List[str],
                "mood_summary": str,
                "suggested_actions": List[str]
            }
            date: Entry date (defaults to now)
            tasks: List of tasks [{"task": "task text", "status": "pending/done", "priority": "high/medium/low"}]
            goals: List of goals [{"goal": "goal text", "timeframe": "daily/weekly/monthly", "progress": 0-100}]
            tags: List of tags for the entry
            category: Entry category (daily, weekly, monthly, etc.)
            chat_history: Optional list of chat messages with AI [{"role": "user/assistant", "content": "message text", "timestamp": "ISO timestamp"}]
            ai_summary: Optional AI-generated summary of the journal entry
        """
        if date is None:
            date = datetime.now()

        # Create entry structure
        entry = {
            "date": date.strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "content": {
                "text": text,
                "tasks": tasks or [],
                "goals": goals or [],
                "tags": tags or [],
                "chat_history": chat_history or [],
                "ai_summary": ai_summary or []
            },
            "emotion_analysis": emotion_analysis,
            "metadata": {
                "last_modified": datetime.now().isoformat(),
                "word_count": len(text.split()),
                "has_tasks": bool(tasks),
                "has_goals": bool(goals),
                "has_chat_history": bool(chat_history),
                "has_ai_summary": bool(ai_summary)
            }
        }

        # Save the entry
        self._save_entry(entry, date)
        return entry

    def _save_entry(self, entry: Dict, date: datetime):
        """Save a journal entry to file"""
        file_path = self._get_journal_path(date)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the entry
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)

    def get_entry(self, date: datetime) -> Optional[Dict]:
        """Retrieve a journal entry for a specific date"""
        file_path = self._get_journal_path(date)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def update_entry(self, 
                    date: datetime,
                    text: Optional[str] = None,
                    emotion_analysis: Optional[Dict] = None,
                    tasks: Optional[List[Dict]] = None,
                    goals: Optional[List[Dict]] = None,
                    tags: Optional[List[str]] = None,
                    chat_history: Optional[List[Dict]] = None,
                    ai_summary: Optional[str] = None) -> Optional[Dict]:
        """Update an existing journal entry"""
        entry = self.get_entry(date)
        if not entry:
            return None

        if text:
            entry['content']['text'] = text
            entry['metadata']['word_count'] = len(text.split())

        if emotion_analysis:
            entry['emotion_analysis'] = emotion_analysis

        if tasks is not None:
            entry['content']['tasks'] = tasks
            entry['metadata']['has_tasks'] = bool(tasks)

        if goals is not None:
            entry['content']['goals'] = goals
            entry['metadata']['has_goals'] = bool(goals)

        if tags is not None:
            entry['content']['tags'] = tags

        if chat_history is not None:
            entry['content']['chat_history'] = chat_history
            entry['metadata']['has_chat_history'] = bool(chat_history)

        if ai_summary is not None:
            entry['content']['ai_summary'] = ai_summary
            entry['metadata']['has_ai_summary'] = bool(ai_summary)

        entry['metadata']['last_modified'] = datetime.now().isoformat()
        
        self._save_entry(entry, date)
        return entry

    def search_entries(self, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      tags: Optional[List[str]] = None,
                      emotion: Optional[str] = None) -> List[Dict]:
        """Search journal entries based on criteria"""
        entries = []
        
        # If no dates specified, use the current month
        if not start_date:
            start_date = datetime.now().replace(day=1)
        if not end_date:
            end_date = datetime.now()

        # Walk through the journal directory
        for root, _, files in os.walk(self.journal_dir):
            for file in files:
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                        
                    entry_date = datetime.strptime(entry['date'], '%Y-%m-%d')
                    
                    # Check if entry matches criteria
                    if start_date <= entry_date <= end_date:
                        if tags and not any(tag in entry['content']['tags'] for tag in tags):
                            continue
                        if emotion and entry['emotion_analysis']['primary_emotion'].lower() != emotion.lower():
                            continue
                        entries.append(entry)
                except Exception as e:
                    print(f"Error reading entry {file_path}: {str(e)}")

        return sorted(entries, key=lambda x: x['date']) 

    def get_all_entries(self) -> List[Dict]:
        """
        Retrieve all journal entries in chronological order.
        
        Returns:
            List[Dict]: A list of all journal entries sorted by date
        """
        entries = []
        
        # Walk through the journal directory
        for root, _, files in os.walk(self.journal_dir):
            for file in files:
                if not file.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                        entries.append(entry)
                except Exception as e:
                    print(f"Error reading entry {file_path}: {str(e)}")

        # Sort entries by date
        return sorted(entries, key=lambda x: x['date']) 

    def record_entry(self, 
                    text: str, 
                    emotion_analysis: Optional[Dict] = {},
                    date: Optional[datetime] = None,
                    tasks: List[Dict] = [],
                    goals: List[Dict] = [],
                    tags: List[str] = [],
                    category: str = "daily",
                    chat_history: Optional[List[Dict]] = [],
                    ai_summary: Optional[str] = []) -> Dict:
        """
        Create a new entry if there were no entry on that day, and update the entry if there was prior entries created before.
        
        Args:
            text: The main journal text
            emotion_analysis: Dict containing emotion analysis
            date: Entry date (defaults to now)
            tasks: List of tasks
            goals: List of goals
            tags: List of tags for the entry
            category: Entry category (daily, weekly, monthly, etc.)
            chat_history: Optional list of chat messages with AI
            ai_summary: Optional AI-generated summary of the journal entry
        """
        if date is None:
            date = datetime.now()
            
        entry = self.get_entry(date)
        if not entry:
            created_entry = self.create_entry(
                text=text,
                emotion_analysis=emotion_analysis,
                date=date,
                tasks=tasks,
                goals=goals,
                tags=tags,
                category=category,
                chat_history=chat_history,
                ai_summary=ai_summary
            )
            return created_entry
        else:
            # Merge emotion analysis
            updated_emotion_analysis = entry["emotion_analysis"].copy()
            updated_emotion_analysis.update(emotion_analysis)
            
            # Merge chat history if provided
            updated_chat_history = entry['content'].get('chat_history', [])
            if chat_history:
                updated_chat_history += chat_history
            
            # Update AI summary if provided, otherwise keep existing
            updated_ai_summary = ai_summary if ai_summary else entry['content'].get('ai_summary', [])
            
            updated_entry = self.update_entry( 
                date=date,
                text=text.replace("\n","\\n").replace('[', '').replace(']', '') + " \n " + entry['content']['text'],
                emotion_analysis=updated_emotion_analysis,
                tasks=tasks + entry['content']["tasks"],
                goals=goals + entry['content']["goals"],
                tags=tags + entry['content']["tags"],
                chat_history=updated_chat_history,
                ai_summary=updated_ai_summary
            )
            return updated_entry 