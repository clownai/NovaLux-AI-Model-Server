"""
Integration Module for Procedural Content Generation

This module provides integration functionality for the procedural content generation system,
connecting the various generators and providing a unified API for game systems to interact with.

The module supports:
- Centralized access to all content generators
- Coordinated content generation across multiple domains
- Consistent player preference management
- State persistence and loading
- Event-driven content updates
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import random
import uuid
import time
import json
import os
from pathlib import Path

from core.procedural_content import (
    ContentType, ContentComplexity, ContentTheme, ContentTone, ContentFaction,
    GenerationStrategy, ContentTemplate, PlayerPreferenceProfile, GeneratedContent,
    ProceduralContentGenerator
)

from generators.quest_generator import (
    QuestGenerator, QuestType, QuestObjectiveType, QuestRewardType
)

from generators.environment_generator import (
    EnvironmentGenerator, EnvironmentType, EnvironmentState, EnvironmentFeature
)

from generators.character_generator import (
    CharacterGenerator, CharacterRole, CharacterTrait, RelationshipType
)


class ContentGenerationManager:
    """
    Central manager for procedural content generation.
    
    This class integrates all content generators and provides a unified API
    for game systems to interact with the procedural content generation system.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the content generation manager.
        
        Args:
            data_dir: Directory for storing data files (optional)
        """
        # Set data directory
        self.data_dir = data_dir or os.path.join(os.getcwd(), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize core generator
        self.core_generator = ProceduralContentGenerator()
        
        # Initialize specialized generators
        self.quest_generator = QuestGenerator(self.core_generator)
        self.environment_generator = EnvironmentGenerator(self.core_generator)
        self.character_generator = CharacterGenerator(self.core_generator)
        
        # Event listeners
        self.event_listeners = {}
        
        # Load templates
        self._load_default_templates()
    
    def register_player(self, player_id: str, initial_preferences: Optional[Dict[str, Any]] = None) -> PlayerPreferenceProfile:
        """
        Register a new player with the system.
        
        Args:
            player_id: Unique player identifier
            initial_preferences: Initial preference data (optional)
            
        Returns:
            Created player preference profile
        """
        # Create default preferences
        if initial_preferences is None:
            initial_preferences = {}
        
        # Initialize preference collections
        preferred_themes = {}
        preferred_tones = {}
        preferred_factions = {}
        preferred_complexity = {}
        content_engagement = {}
        custom_preferences = {}
        
        # Process initial preferences
        if "themes" in initial_preferences:
            for theme_str, value in initial_preferences["themes"].items():
                try:
                    theme = ContentTheme(theme_str)
                    preferred_themes[theme] = max(0.0, min(1.0, value))
                except ValueError:
                    pass
        
        if "tones" in initial_preferences:
            for tone_str, value in initial_preferences["tones"].items():
                try:
                    tone = ContentTone(tone_str)
                    preferred_tones[tone] = max(0.0, min(1.0, value))
                except ValueError:
                    pass
        
        if "factions" in initial_preferences:
            for faction_str, value in initial_preferences["factions"].items():
                try:
                    faction = ContentFaction(faction_str)
                    preferred_factions[faction] = max(0.0, min(1.0, value))
                except ValueError:
                    pass
        
        if "complexity" in initial_preferences:
            for type_str, value in initial_preferences["complexity"].items():
                try:
                    content_type = ContentType(type_str)
                    complexity = ContentComplexity(value) if isinstance(value, int) else ContentComplexity.MODERATE
                    preferred_complexity[content_type] = complexity
                except ValueError:
                    pass
        
        if "engagement" in initial_preferences:
            for type_str, value in initial_preferences["engagement"].items():
                try:
                    content_type = ContentType(type_str)
                    content_engagement[content_type] = max(0.0, min(1.0, value))
                except ValueError:
                    pass
        
        if "custom" in initial_preferences:
            custom_preferences = initial_preferences["custom"]
        
        # Create profile
        profile = PlayerPreferenceProfile(
            player_id=player_id,
            preferred_themes=preferred_themes,
            preferred_tones=preferred_tones,
            preferred_factions=preferred_factions,
            preferred_complexity=preferred_complexity,
            content_engagement=content_engagement,
            custom_preferences=custom_preferences
        )
        
        # Register with core generator
        self.core_generator.register_player_profile(profile)
        
        return profile
    
    def update_player_preference(self, player_id: str, preference_type: str, 
                               key: Any, value: float) -> bool:
        """
        Update a player preference.
        
        Args:
            player_id: Player ID
            preference_type: Type of preference
            key: Preference key
            value: New preference value
            
        Returns:
            True if update successful, False otherwise
        """
        return self.core_generator.update_player_preference(player_id, preference_type, key, value)
    
    def get_player_profile(self, player_id: str) -> Optional[PlayerPreferenceProfile]:
        """
        Get a player's preference profile.
        
        Args:
            player_id: Player ID
            
        Returns:
            Player preference profile or None if not found
        """
        return self.core_generator.get_player_profile(player_id)
    
    def register_template(self, template_data: Dict[str, Any]) -> bool:
        """
        Register a content template from dictionary data.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Extract required fields
            template_id = template_data["id"]
            name = template_data["name"]
            content_type_str = template_data["content_type"]
            description = template_data["description"]
            template_content = template_data["template_data"]
            
            # Convert content type
            try:
                content_type = ContentType(content_type_str)
            except ValueError:
                print(f"Invalid content type: {content_type_str}")
                return False
            
            # Extract optional fields
            complexity_value = template_data.get("complexity", 2)
            try:
                complexity = ContentComplexity(complexity_value)
            except ValueError:
                complexity = ContentComplexity.MODERATE
            
            # Process themes
            themes = []
            for theme_str in template_data.get("themes", []):
                try:
                    theme = ContentTheme(theme_str)
                    themes.append(theme)
                except ValueError:
                    pass
            
            # Process tones
            tones = []
            for tone_str in template_data.get("tones", []):
                try:
                    tone = ContentTone(tone_str)
                    tones.append(tone)
                except ValueError:
                    pass
            
            # Process factions
            factions = []
            for faction_str in template_data.get("factions", []):
                try:
                    faction = ContentFaction(faction_str)
                    factions.append(faction)
                except ValueError:
                    pass
            
            # Create template
            template = ContentTemplate(
                id=template_id,
                name=name,
                content_type=content_type,
                description=description,
                template_data=template_content,
                complexity=complexity,
                themes=themes,
                tones=tones,
                factions=factions,
                tags=template_data.get("tags", [])
            )
            
            # Register with appropriate generator
            if content_type == ContentType.QUEST:
                return self.quest_generator.register_quest_template(template)
            elif content_type == ContentType.ENVIRONMENT:
                return self.environment_generator.register_environment_template(template)
            elif content_type == ContentType.CHARACTER:
                return self.character_generator.register_character_template(template)
            else:
                return self.core_generator.register_template(template)
            
        except KeyError as e:
            print(f"Missing required field in template data: {e}")
            return False
    
    def generate_content(self, content_type: ContentType, player_id: Optional[str] = None,
                       params: Optional[Dict[str, Any]] = None) -> GeneratedContent:
        """
        Generate content of a specific type.
        
        Args:
            content_type: Type of content to generate
            player_id: Player ID for personalization (optional)
            params: Additional generation parameters (optional)
            
        Returns:
            Generated content
        """
        # Initialize parameters
        if params is None:
            params = {}
        
        # Generate content based on type
        if content_type == ContentType.QUEST:
            quest_type = None
            if "quest_type" in params:
                try:
                    quest_type = QuestType(params["quest_type"])
                except ValueError:
                    pass
            
            template_id = params.get("template_id")
            
            return self.quest_generator.generate_quest(
                player_id=player_id,
                quest_type=quest_type,
                template_id=template_id,
                params=params
            )
        
        elif content_type == ContentType.ENVIRONMENT:
            environment_type = None
            if "environment_type" in params:
                try:
                    environment_type = EnvironmentType(params["environment_type"])
                except ValueError:
                    pass
            
            template_id = params.get("template_id")
            
            return self.environment_generator.generate_environment(
                player_id=player_id,
                environment_type=environment_type,
                template_id=template_id,
                params=params
            )
        
        elif content_type == ContentType.CHARACTER:
            role = None
            if "role" in params:
                try:
                    role = CharacterRole(params["role"])
                except ValueError:
                    pass
            
            faction = None
            if "faction" in params:
                try:
                    faction = ContentFaction(params["faction"])
                except ValueError:
                    pass
            
            template_id = params.get("template_id")
            
            return self.character_generator.generate_character(
                player_id=player_id,
                role=role,
                faction=faction,
                template_id=template_id,
                params=params
            )
        
        else:
            # Use core generator for other content types
            template_id = params.get("template_id")
            strategy = GenerationStrategy.TEMPLATE_BASED
            
            if "strategy" in params:
                try:
                    strategy = GenerationStrategy(params["strategy"])
                except ValueError:
                    pass
            
            return self.core_generator.generate_content(
                content_type=content_type,
                player_id=player_id,
                template_id=template_id,
                params=params,
                strategy=strategy
            )
    
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
        return self.quest_generator.generate_quest_chain(chain_id, player_id, params)
    
    def generate_character_group(self, group_size: int, faction: ContentFaction,
                               roles: Optional[List[CharacterRole]] = None,
                               player_id: Optional[str] = None,
                               params: Optional[Dict[str, Any]] = None) -> List[GeneratedContent]:
        """
        Generate a group of related characters.
        
        Args:
            group_size: Number of characters to generate
            faction: Faction for the character group
            roles: Specific roles for characters (optional)
            player_id: Player ID for personalization (optional)
            params: Additional generation parameters (optional)
            
        Returns:
            List of generated characters
        """
        return self.character_generator.generate_character_group(
            group_size=group_size,
            faction=faction,
            roles=roles,
            player_id=player_id,
            params=params
        )
    
    def generate_related_content(self, base_content: GeneratedContent,
                               related_type: ContentType,
                               count: int = 1,
                               player_id: Optional[str] = None,
                               params: Optional[Dict[str, Any]] = None) -> List[GeneratedContent]:
        """
        Generate content related to existing content.
        
        Args:
            base_content: Base content to generate related content for
            related_type: Type of related content to generate
            count: Number of related content items to generate
            player_id: Player ID for personalization (optional)
            params: Additional generation parameters (optional)
            
        Returns:
            List of generated related content
        """
        # Initialize parameters
        if params is None:
            params = {}
        
        # Add base content to parameters
        if "variables" not in params:
            params["variables"] = {}
        
        params["variables"]["related_to"] = {
            "id": base_content.id,
            "type": base_content.content_type.value,
            "name": base_content.name,
            "content_data": base_content.content_data
        }
        
        # Generate related content
        related_content = []
        
        for _ in range(count):
            content = self.generate_content(
                content_type=related_type,
                player_id=player_id,
                params=params
            )
            
            related_content.append(content)
        
        return related_content
    
    def evaluate_content(self, content: GeneratedContent, 
                       player_id: Optional[str] = None,
                       metrics: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Evaluate content quality and player fit.
        
        Args:
            content: Content to evaluate
            player_id: Player ID for personalization metrics (optional)
            metrics: Specific metrics to evaluate (optional)
            
        Returns:
            Dictionary of evaluation scores
        """
        return self.core_generator.evaluate_content(content, player_id, metrics)
    
    def add_event_listener(self, event_type: str, listener_func: callable) -> str:
        """
        Add a listener for content generation events.
        
        Args:
            event_type: Type of event to listen for
            listener_func: Function to call when event occurs
            
        Returns:
            Listener ID
        """
        listener_id = str(uuid.uuid4())
        
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = {}
        
        self.event_listeners[event_type][listener_id] = listener_func
        
        return listener_id
    
    def remove_event_listener(self, event_type: str, listener_id: str) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event
            listener_id: Listener ID
            
        Returns:
            True if listener was removed, False otherwise
        """
        if event_type in self.event_listeners and listener_id in self.event_listeners[event_type]:
            del self.event_listeners[event_type][listener_id]
            return True
        
        return False
    
    def trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Trigger an event for listeners.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if event_type in self.event_listeners:
            for listener_func in self.event_listeners[event_type].values():
                try:
                    listener_func(event_data)
                except Exception as e:
                    print(f"Error in event listener: {e}")
    
    def save_state(self) -> bool:
        """
        Save the current state of all generators.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create state directory
            state_dir = os.path.join(self.data_dir, "state")
            os.makedirs(state_dir, exist_ok=True)
            
            # Save core generator state
            core_path = os.path.join(state_dir, "core_generator.json")
            self.core_generator.save_state(core_path)
            
            # Save quest generator state
            quest_path = os.path.join(state_dir, "quest_generator.json")
            self.quest_generator.save_state(quest_path)
            
            # Save environment generator state
            env_path = os.path.join(state_dir, "environment_generator.json")
            self.environment_generator.save_state(env_path)
            
            # Save character generator state
            char_path = os.path.join(state_dir, "character_generator.json")
            self.character_generator.save_state(char_path)
            
            return True
        
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self) -> bool:
        """
        Load the state of all generators.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check state directory
            state_dir = os.path.join(self.data_dir, "state")
            if not os.path.exists(state_dir):
                return False
            
            # Load core generator state
            core_path = os.path.join(state_dir, "core_generator.json")
            if os.path.exists(core_path):
                self.core_generator.load_state(core_path)
            
            # Load quest generator state
            quest_path = os.path.join(state_dir, "quest_generator.json")
            if os.path.exists(quest_path):
                self.quest_generator.load_state(quest_path)
            
            # Load environment generator state
            env_path = os.path.join(state_dir, "environment_generator.json")
            if os.path.exists(env_path):
                self.environment_generator.load_state(env_path)
            
            # Load character generator state
            char_path = os.path.join(state_dir, "character_generator.json")
            if os.path.exists(char_path):
                self.character_generator.load_state(char_path)
            
            return True
        
        except Exception as e:
            print(f"Error loading state: {e}")
            return False
    
    def _load_default_templates(self) -> None:
        """Load default templates from the templates directory."""
        templates_dir = os.path.join(self.data_dir, "templates")
        
        # Skip if directory doesn't exist
        if not os.path.exists(templates_dir):
            return
        
        # Load templates from JSON files
        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(templates_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        template_data = json.load(f)
                    
                    # Register template
                    if isinstance(template_data, dict):
                        self.register_template(template_data)
                    elif isinstance(template_data, list):
                        for template in template_data:
                            self.register_template(template)
                
                except Exception as e:
                    print(f"Error loading template from {filename}: {e}")


class ContentGenerationAPI:
    """
    API wrapper for the content generation system.
    
    This class provides a simplified API for game systems to interact with
    the procedural content generation system.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the content generation API.
        
        Args:
            data_dir: Directory for storing data files (optional)
        """
        self.manager = ContentGenerationManager(data_dir)
    
    def register_player(self, player_id: str, preferences: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a player with the system.
        
        Args:
            player_id: Player ID
            preferences: Initial preferences (optional)
            
        Returns:
            True if registration successful, False otherwise
        """
        profile = self.manager.register_player(player_id, preferences)
        return profile is not None
    
    def generate_quest(self, player_id: str, quest_type: str = None,
                     params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a quest for a player.
        
        Args:
            player_id: Player ID
            quest_type: Type of quest (optional)
            params: Additional parameters (optional)
            
        Returns:
            Generated quest data
        """
        # Prepare parameters
        if params is None:
            params = {}
        
        if quest_type is not None:
            params["quest_type"] = quest_type
        
        # Generate quest
        quest = self.manager.generate_content(
            content_type=ContentType.QUEST,
            player_id=player_id,
            params=params
        )
        
        # Convert to dictionary
        return quest.to_dict()
    
    def generate_environment(self, player_id: str, environment_type: str = None,
                           params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an environment for a player.
        
        Args:
            player_id: Player ID
            environment_type: Type of environment (optional)
            params: Additional parameters (optional)
            
        Returns:
            Generated environment data
        """
        # Prepare parameters
        if params is None:
            params = {}
        
        if environment_type is not None:
            params["environment_type"] = environment_type
        
        # Generate environment
        environment = self.manager.generate_content(
            content_type=ContentType.ENVIRONMENT,
            player_id=player_id,
            params=params
        )
        
        # Convert to dictionary
        return environment.to_dict()
    
    def generate_character(self, player_id: str, role: str = None,
                         faction: str = None,
                         params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a character for a player.
        
        Args:
            player_id: Player ID
            role: Character role (optional)
            faction: Character faction (optional)
            params: Additional parameters (optional)
            
        Returns:
            Generated character data
        """
        # Prepare parameters
        if params is None:
            params = {}
        
        if role is not None:
            params["role"] = role
        
        if faction is not None:
            params["faction"] = faction
        
        # Generate character
        character = self.manager.generate_content(
            content_type=ContentType.CHARACTER,
            player_id=player_id,
            params=params
        )
        
        # Convert to dictionary
        return character.to_dict()
    
    def update_player_preference(self, player_id: str, preference_type: str,
                               key: str, value: float) -> bool:
        """
        Update a player preference.
        
        Args:
            player_id: Player ID
            preference_type: Type of preference
            key: Preference key
            value: New preference value
            
        Returns:
            True if update successful, False otherwise
        """
        return self.manager.update_player_preference(player_id, preference_type, key, value)
    
    def save_state(self) -> bool:
        """
        Save the current state of the system.
        
        Returns:
            True if successful, False otherwise
        """
        return self.manager.save_state()
    
    def load_state(self) -> bool:
        """
        Load the state of the system.
        
        Returns:
            True if successful, False otherwise
        """
        return self.manager.load_state()
