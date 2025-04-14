"""
Quest Generator Module

This module provides specialized functionality for generating procedural quests
in the NovaLux ecosystem, creating dynamic mission content that adapts to player
preferences and behavior patterns.

The module supports:
- Multi-stage quest generation
- Objective-based quest structures
- Faction-aligned quest themes
- Difficulty-appropriate challenges
- Personalized reward systems
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import random
import uuid
import time
import copy
from enum import Enum

from core.procedural_content import (
    ContentType, ContentComplexity, ContentTheme, ContentTone, ContentFaction,
    GenerationStrategy, ContentTemplate, PlayerPreferenceProfile, GeneratedContent,
    ProceduralContentGenerator
)


class QuestType(Enum):
    """Types of quests that can be generated."""
    MAIN = "main"
    SIDE = "side"
    FACTION = "faction"
    CHALLENGE = "challenge"
    DAILY = "daily"
    EVENT = "event"
    TUTORIAL = "tutorial"
    HIDDEN = "hidden"


class QuestObjectiveType(Enum):
    """Types of objectives for quests."""
    COLLECT = "collect"
    DEFEAT = "defeat"
    INTERACT = "interact"
    ESCORT = "escort"
    DEFEND = "defend"
    INVESTIGATE = "investigate"
    REACH = "reach"
    HACK = "hack"
    GAMBLE = "gamble"
    TRADE = "trade"
    CRAFT = "craft"
    STEALTH = "stealth"
    RACE = "race"
    PUZZLE = "puzzle"
    SOCIAL = "social"


class QuestRewardType(Enum):
    """Types of rewards for quests."""
    CURRENCY = "currency"
    ITEM = "item"
    EXPERIENCE = "experience"
    REPUTATION = "reputation"
    SKILL = "skill"
    UNLOCK = "unlock"
    COSMETIC = "cosmetic"
    LORE = "lore"
    SPECIAL = "special"


class QuestGenerator:
    """
    Specialized generator for procedural quests.
    
    This class extends the core procedural content generation system with
    quest-specific functionality, creating dynamic missions that adapt to
    player preferences and behavior patterns.
    """
    
    def __init__(self, content_generator: ProceduralContentGenerator):
        """
        Initialize the quest generator.
        
        Args:
            content_generator: Core procedural content generator
        """
        self.content_generator = content_generator
        self.quest_templates: Dict[str, ContentTemplate] = {}
        self.quest_chains: Dict[str, List[str]] = {}  # Chain ID -> List of quest IDs
        self.player_quest_history: Dict[str, Dict[str, Any]] = {}  # Player ID -> Quest history
    
    def register_quest_template(self, template: ContentTemplate) -> bool:
        """
        Register a quest template.
        
        Args:
            template: Quest template to register
            
        Returns:
            True if registration successful, False otherwise
        """
        # Verify this is a quest template
        if template.content_type != ContentType.QUEST:
            print(f"Template {template.id} is not a quest template")
            return False
        
        # Register with core generator
        success = self.content_generator.register_template(template)
        if success:
            self.quest_templates[template.id] = template
        
        return success
    
    def create_quest_chain(self, chain_id: str, quest_template_ids: List[str]) -> bool:
        """
        Create a chain of related quests.
        
        Args:
            chain_id: Unique identifier for the quest chain
            quest_template_ids: List of quest template IDs in sequence
            
        Returns:
            True if creation successful, False otherwise
        """
        # Verify all templates exist and are quest templates
        for template_id in quest_template_ids:
            template = self.content_generator.get_template(template_id)
            if template is None:
                print(f"Template {template_id} not found")
                return False
            if template.content_type != ContentType.QUEST:
                print(f"Template {template_id} is not a quest template")
                return False
        
        # Register quest chain
        self.quest_chains[chain_id] = quest_template_ids
        
        return True
    
    def generate_quest(self, player_id: Optional[str] = None,
                     quest_type: Optional[QuestType] = None,
                     template_id: Optional[str] = None,
                     params: Optional[Dict[str, Any]] = None) -> GeneratedContent:
        """
        Generate a quest based on player preferences.
        
        Args:
            player_id: Player ID for personalization (optional)
            quest_type: Type of quest to generate (optional)
            template_id: Specific template ID to use (optional)
            params: Additional generation parameters (optional)
            
        Returns:
            Generated quest content
        """
        # Initialize parameters
        if params is None:
            params = {}
        
        # Add quest type to parameters if specified
        if quest_type is not None:
            if "variables" not in params:
                params["variables"] = {}
            params["variables"]["quest_type"] = quest_type.value
        
        # Generate quest content
        quest = self.content_generator.generate_content(
            content_type=ContentType.QUEST,
            player_id=player_id,
            template_id=template_id,
            params=params,
            strategy=GenerationStrategy.TEMPLATE_BASED
        )
        
        # Post-process quest
        self._post_process_quest(quest, player_id)
        
        # Record in player quest history
        if player_id is not None:
            self._record_quest_in_history(player_id, quest)
        
        return quest
    
    def generate_quest_chain(self, chain_id: str, player_id: Optional[str] = None,
                           params: Optional[Dict[str, Any]] = None) -> List[GeneratedContent]:
        """
        Generate a chain of related quests.
        
        Args:
            chain_id: Quest chain ID
            player_id: Player ID for personalization (optional)
            params: Additional generation parameters (optional)
            
        Returns:
            List of generated quests in chain order
        """
        # Check if chain exists
        if chain_id not in self.quest_chains:
            return []
        
        # Initialize parameters
        if params is None:
            params = {}
        
        # Get template IDs for chain
        template_ids = self.quest_chains[chain_id]
        
        # Generate quests in sequence
        quests = []
        chain_context = {"chain_id": chain_id, "quests": []}
        
        for i, template_id in enumerate(template_ids):
            # Update parameters with chain context
            chain_params = copy.deepcopy(params)
            if "variables" not in chain_params:
                chain_params["variables"] = {}
            
            chain_params["variables"]["chain_id"] = chain_id
            chain_params["variables"]["chain_position"] = i
            chain_params["variables"]["chain_length"] = len(template_ids)
            chain_params["variables"]["is_first_in_chain"] = (i == 0)
            chain_params["variables"]["is_last_in_chain"] = (i == len(template_ids) - 1)
            
            # Add previous quest data if available
            if quests:
                chain_params["variables"]["previous_quest"] = quests[-1].content_data
            
            # Add chain context
            chain_params["variables"]["chain_context"] = chain_context
            
            # Generate quest
            quest = self.generate_quest(
                player_id=player_id,
                template_id=template_id,
                params=chain_params
            )
            
            quests.append(quest)
            
            # Update chain context
            chain_context["quests"].append({
                "id": quest.id,
                "name": quest.name,
                "position": i,
                "template_id": template_id
            })
        
        return quests
    
    def get_available_quests(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get list of available quests for a player.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of available quest information
        """
        # Get player profile
        player_profile = self.content_generator.get_player_profile(player_id)
        if player_profile is None:
            return []
        
        # Get player quest history
        quest_history = self.player_quest_history.get(player_id, {})
        completed_quests = quest_history.get("completed", [])
        active_quests = quest_history.get("active", [])
        
        # Get all quest templates
        all_templates = [
            template for template in self.content_generator.templates.values()
            if template.content_type == ContentType.QUEST
        ]
        
        # Filter available templates
        available_quests = []
        
        for template in all_templates:
            # Skip templates that are already active
            if any(q["template_id"] == template.id for q in active_quests):
                continue
            
            # Check prerequisites
            prerequisites = template.template_data.get("prerequisites", {})
            
            # Check level prerequisite
            if "min_level" in prerequisites:
                player_level = quest_history.get("player_level", 1)
                if player_level < prerequisites["min_level"]:
                    continue
            
            # Check completed quest prerequisites
            if "completed_quests" in prerequisites:
                required_quests = prerequisites["completed_quests"]
                if not all(q in completed_quests for q in required_quests):
                    continue
            
            # Check faction prerequisites
            if "faction" in prerequisites:
                required_faction = prerequisites["faction"]
                player_faction = quest_history.get("faction")
                if player_faction != required_faction:
                    continue
            
            # Check reputation prerequisites
            if "min_reputation" in prerequisites:
                for faction, min_rep in prerequisites["min_reputation"].items():
                    player_rep = quest_history.get("reputation", {}).get(faction, 0)
                    if player_rep < min_rep:
                        continue
            
            # Quest is available
            available_quests.append({
                "template_id": template.id,
                "name": template.name,
                "description": template.description,
                "quest_type": template.template_data.get("quest_type", "side"),
                "complexity": template.complexity.value,
                "themes": [theme.value for theme in template.themes],
                "factions": [faction.value for faction in template.factions]
            })
        
        return available_quests
    
    def update_player_quest_status(self, player_id: str, quest_id: str, 
                                 status: str, progress: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a player's quest status.
        
        Args:
            player_id: Player ID
            quest_id: Quest ID
            status: New status ("active", "completed", "failed", "abandoned")
            progress: Quest progress data (optional)
            
        Returns:
            True if update successful, False otherwise
        """
        # Initialize player quest history if needed
        if player_id not in self.player_quest_history:
            self.player_quest_history[player_id] = {
                "active": [],
                "completed": [],
                "failed": [],
                "abandoned": []
            }
        
        history = self.player_quest_history[player_id]
        
        # Find quest in current status lists
        current_status = None
        quest_data = None
        
        for status_key in ["active", "completed", "failed", "abandoned"]:
            for i, quest in enumerate(history.get(status_key, [])):
                if quest["quest_id"] == quest_id:
                    current_status = status_key
                    quest_data = quest
                    history[status_key].pop(i)
                    break
            if current_status:
                break
        
        # If quest not found and not activating, return False
        if quest_data is None and status != "active":
            return False
        
        # If activating a new quest, create quest data
        if quest_data is None and status == "active":
            # Find quest in content history
            content_history = self.content_generator.get_player_content_history(player_id)
            quest_content = None
            
            for content in content_history:
                if content.id == quest_id and content.content_type == ContentType.QUEST:
                    quest_content = content
                    break
            
            if quest_content is None:
                return False
            
            # Create quest data
            quest_data = {
                "quest_id": quest_id,
                "template_id": quest_content.template_id,
                "name": quest_content.name,
                "activated_at": time.time(),
                "progress": {}
            }
        
        # Update progress if provided
        if progress is not None:
            quest_data["progress"] = progress
        
        # Update status timestamp
        quest_data[f"{status}_at"] = time.time()
        
        # Add to new status list
        if status not in history:
            history[status] = []
        history[status].append(quest_data)
        
        return True
    
    def get_player_quest_history(self, player_id: str) -> Dict[str, Any]:
        """
        Get a player's quest history.
        
        Args:
            player_id: Player ID
            
        Returns:
            Quest history data
        """
        return self.player_quest_history.get(player_id, {})
    
    def _post_process_quest(self, quest: GeneratedContent, player_id: Optional[str]) -> None:
        """
        Post-process a generated quest.
        
        Args:
            quest: Generated quest content
            player_id: Player ID (optional)
        """
        # Add unique quest ID to content data
        if "quest_id" not in quest.content_data:
            quest.content_data["quest_id"] = quest.id
        
        # Add timestamp
        if "generated_at" not in quest.content_data:
            quest.content_data["generated_at"] = quest.timestamp
        
        # Add player ID if available
        if player_id is not None and "player_id" not in quest.content_data:
            quest.content_data["player_id"] = player_id
        
        # Ensure objectives are properly structured
        if "objectives" in quest.content_data and isinstance(quest.content_data["objectives"], list):
            for i, objective in enumerate(quest.content_data["objectives"]):
                if isinstance(objective, dict):
                    # Add objective ID if missing
                    if "id" not in objective:
                        objective["id"] = f"obj_{i+1}"
                    
                    # Add objective index if missing
                    if "index" not in objective:
                        objective["index"] = i
                    
                    # Add objective status if missing
                    if "status" not in objective:
                        objective["status"] = "pending"
        
        # Ensure steps are properly structured
        if "steps" in quest.content_data and isinstance(quest.content_data["steps"], list):
            for i, step in enumerate(quest.content_data["steps"]):
                if isinstance(step, dict):
                    # Add step ID if missing
                    if "id" not in step:
                        step["id"] = f"step_{i+1}"
                    
                    # Add step number if missing
                    if "step_number" not in step:
                        step["step_number"] = i + 1
                    
                    # Add step status if missing
                    if "status" not in step:
                        step["status"] = "pending"
        
        # Ensure rewards are properly structured
        if "rewards" in quest.content_data and isinstance(quest.content_data["rewards"], list):
            for i, reward in enumerate(quest.content_data["rewards"]):
                if isinstance(reward, dict):
                    # Add reward ID if missing
                    if "id" not in reward:
                        reward["id"] = f"reward_{i+1}"
                    
                    # Add reward status if missing
                    if "status" not in reward:
                        reward["status"] = "pending"
    
    def _record_quest_in_history(self, player_id: str, quest: GeneratedContent) -> None:
        """
        Record a quest in player history.
        
        Args:
            player_id: Player ID
            quest: Generated quest content
        """
        # Initialize player quest history if needed
        if player_id not in self.player_quest_history:
            self.player_quest_history[player_id] = {
                "active": [],
                "completed": [],
                "failed": [],
                "abandoned": []
            }
        
        # Add to history
        self.player_quest_history[player_id]["generated"] = self.player_quest_history[player_id].get("generated", [])
        self.player_quest_history[player_id]["generated"].append({
            "quest_id": quest.id,
            "template_id": quest.template_id,
            "name": quest.name,
            "generated_at": quest.timestamp
        })
    
    def save_state(self, filepath: str) -> bool:
        """
        Save generator state to file.
        
        Args:
            filepath: Path to save state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            # Prepare data for serialization
            data = {
                "quest_chains": self.quest_chains,
                "player_quest_history": self.player_quest_history
            }
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving quest generator state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load generator state from file.
        
        Args:
            filepath: Path to load state from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load quest chains
            self.quest_chains = data.get("quest_chains", {})
            
            # Load player quest history
            self.player_quest_history = data.get("player_quest_history", {})
            
            return True
        
        except Exception as e:
            print(f"Error loading quest generator state: {e}")
            return False
