"""
Environment Generator Module

This module provides specialized functionality for generating procedural environments
in the NovaLux ecosystem, creating dynamic locations and settings that adapt to player
preferences and behavior patterns.

The module supports:
- Procedural location generation
- Dynamic environment states
- Faction territory control
- Environmental hazards and features
- Adaptive atmosphere based on player history
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


class EnvironmentType(Enum):
    """Types of environments that can be generated."""
    URBAN = "urban"
    CORPORATE = "corporate"
    UNDERGROUND = "underground"
    WILDERNESS = "wilderness"
    VIRTUAL = "virtual"
    SPACE = "space"
    CASINO = "casino"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    ENTERTAINMENT = "entertainment"


class EnvironmentState(Enum):
    """Possible states for environments."""
    PEACEFUL = "peaceful"
    TENSE = "tense"
    CONFLICT = "conflict"
    LOCKDOWN = "lockdown"
    CELEBRATION = "celebration"
    ABANDONED = "abandoned"
    RESTRICTED = "restricted"
    HAZARDOUS = "hazardous"
    UNSTABLE = "unstable"


class EnvironmentFeature(Enum):
    """Special features that can exist in environments."""
    SECURITY_SYSTEMS = "security_systems"
    HIDDEN_AREAS = "hidden_areas"
    CROWD = "crowd"
    SURVEILLANCE = "surveillance"
    RESTRICTED_ACCESS = "restricted_access"
    BLACK_MARKET = "black_market"
    ENVIRONMENTAL_HAZARD = "environmental_hazard"
    FACTION_PRESENCE = "faction_presence"
    SPECIAL_EVENT = "special_event"
    UNIQUE_RESOURCE = "unique_resource"


class EnvironmentGenerator:
    """
    Specialized generator for procedural environments.
    
    This class extends the core procedural content generation system with
    environment-specific functionality, creating dynamic locations that adapt to
    player preferences and behavior patterns.
    """
    
    def __init__(self, content_generator: ProceduralContentGenerator):
        """
        Initialize the environment generator.
        
        Args:
            content_generator: Core procedural content generator
        """
        self.content_generator = content_generator
        self.environment_templates: Dict[str, ContentTemplate] = {}
        self.global_state: Dict[str, Any] = {
            "faction_territories": {},
            "environment_states": {},
            "global_events": [],
            "resource_distribution": {}
        }
    
    def register_environment_template(self, template: ContentTemplate) -> bool:
        """
        Register an environment template.
        
        Args:
            template: Environment template to register
            
        Returns:
            True if registration successful, False otherwise
        """
        # Verify this is an environment template
        if template.content_type != ContentType.ENVIRONMENT:
            print(f"Template {template.id} is not an environment template")
            return False
        
        # Register with core generator
        success = self.content_generator.register_template(template)
        if success:
            self.environment_templates[template.id] = template
        
        return success
    
    def generate_environment(self, player_id: Optional[str] = None,
                           environment_type: Optional[EnvironmentType] = None,
                           template_id: Optional[str] = None,
                           params: Optional[Dict[str, Any]] = None) -> GeneratedContent:
        """
        Generate an environment based on player preferences.
        
        Args:
            player_id: Player ID for personalization (optional)
            environment_type: Type of environment to generate (optional)
            template_id: Specific template ID to use (optional)
            params: Additional generation parameters (optional)
            
        Returns:
            Generated environment content
        """
        # Initialize parameters
        if params is None:
            params = {}
        
        # Add environment type to parameters if specified
        if environment_type is not None:
            if "variables" not in params:
                params["variables"] = {}
            params["variables"]["environment_type"] = environment_type.value
        
        # Add global state information to parameters
        self._add_global_state_to_params(params)
        
        # Generate environment content
        environment = self.content_generator.generate_content(
            content_type=ContentType.ENVIRONMENT,
            player_id=player_id,
            template_id=template_id,
            params=params,
            strategy=GenerationStrategy.TEMPLATE_BASED
        )
        
        # Post-process environment
        self._post_process_environment(environment, player_id)
        
        # Update global state based on generated environment
        self._update_global_state(environment)
        
        return environment
    
    def get_environment_state(self, environment_id: str) -> Optional[EnvironmentState]:
        """
        Get the current state of an environment.
        
        Args:
            environment_id: Environment ID
            
        Returns:
            Current environment state or None if not found
        """
        state_str = self.global_state["environment_states"].get(environment_id)
        if state_str is None:
            return None
        
        try:
            return EnvironmentState(state_str)
        except ValueError:
            return None
    
    def set_environment_state(self, environment_id: str, state: EnvironmentState) -> bool:
        """
        Set the state of an environment.
        
        Args:
            environment_id: Environment ID
            state: New environment state
            
        Returns:
            True if update successful, False otherwise
        """
        self.global_state["environment_states"][environment_id] = state.value
        return True
    
    def get_faction_territories(self) -> Dict[str, List[str]]:
        """
        Get current faction territory control.
        
        Returns:
            Dictionary mapping faction IDs to lists of controlled environment IDs
        """
        return self.global_state["faction_territories"]
    
    def set_faction_territory(self, faction_id: str, environment_id: str) -> bool:
        """
        Set faction control of an environment.
        
        Args:
            faction_id: Faction ID
            environment_id: Environment ID
            
        Returns:
            True if update successful, False otherwise
        """
        # Initialize faction territories if needed
        if faction_id not in self.global_state["faction_territories"]:
            self.global_state["faction_territories"][faction_id] = []
        
        # Remove environment from any other faction's control
        for other_faction, territories in self.global_state["faction_territories"].items():
            if other_faction != faction_id and environment_id in territories:
                territories.remove(environment_id)
        
        # Add to faction's territories if not already there
        if environment_id not in self.global_state["faction_territories"][faction_id]:
            self.global_state["faction_territories"][faction_id].append(environment_id)
        
        return True
    
    def add_global_event(self, event: Dict[str, Any]) -> str:
        """
        Add a global event that affects environments.
        
        Args:
            event: Event data (must include 'name', 'description', 'duration')
            
        Returns:
            Event ID
        """
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Add required fields
        event["id"] = event_id
        event["start_time"] = time.time()
        if "end_time" not in event and "duration" in event:
            event["end_time"] = event["start_time"] + event["duration"]
        
        # Add to global events
        self.global_state["global_events"].append(event)
        
        return event_id
    
    def get_active_global_events(self) -> List[Dict[str, Any]]:
        """
        Get currently active global events.
        
        Returns:
            List of active global events
        """
        current_time = time.time()
        active_events = []
        
        for event in self.global_state["global_events"]:
            if "end_time" not in event or event["end_time"] > current_time:
                active_events.append(event)
        
        return active_events
    
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
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(self.global_state, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving environment generator state: {e}")
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
                self.global_state = json.load(f)
            
            return True
        
        except Exception as e:
            print(f"Error loading environment generator state: {e}")
            return False
    
    def _add_global_state_to_params(self, params: Dict[str, Any]) -> None:
        """
        Add global state information to generation parameters.
        
        Args:
            params: Generation parameters to update
        """
        if "variables" not in params:
            params["variables"] = {}
        
        # Add active global events
        params["variables"]["global_events"] = self.get_active_global_events()
        
        # Add faction territories
        params["variables"]["faction_territories"] = self.global_state["faction_territories"]
        
        # Add resource distribution
        params["variables"]["resource_distribution"] = self.global_state["resource_distribution"]
    
    def _post_process_environment(self, environment: GeneratedContent, player_id: Optional[str]) -> None:
        """
        Post-process a generated environment.
        
        Args:
            environment: Generated environment content
            player_id: Player ID (optional)
        """
        # Add unique environment ID to content data
        if "environment_id" not in environment.content_data:
            environment.content_data["environment_id"] = environment.id
        
        # Add timestamp
        if "generated_at" not in environment.content_data:
            environment.content_data["generated_at"] = environment.timestamp
        
        # Add player ID if available
        if player_id is not None and "player_id" not in environment.content_data:
            environment.content_data["player_id"] = player_id
        
        # Ensure features are properly structured
        if "features" in environment.content_data and isinstance(environment.content_data["features"], list):
            for i, feature in enumerate(environment.content_data["features"]):
                if isinstance(feature, dict) and "id" not in feature:
                    feature["id"] = f"feature_{i+1}"
        
        # Ensure NPCs are properly structured
        if "npcs" in environment.content_data and isinstance(environment.content_data["npcs"], list):
            for i, npc in enumerate(environment.content_data["npcs"]):
                if isinstance(npc, dict) and "id" not in npc:
                    npc["id"] = f"npc_{i+1}"
        
        # Ensure points of interest are properly structured
        if "points_of_interest" in environment.content_data and isinstance(environment.content_data["points_of_interest"], list):
            for i, poi in enumerate(environment.content_data["points_of_interest"]):
                if isinstance(poi, dict) and "id" not in poi:
                    poi["id"] = f"poi_{i+1}"
    
    def _update_global_state(self, environment: GeneratedContent) -> None:
        """
        Update global state based on generated environment.
        
        Args:
            environment: Generated environment content
        """
        # Get environment ID
        environment_id = environment.id
        
        # Update environment state
        if "state" in environment.content_data:
            state_str = environment.content_data["state"]
            try:
                state = EnvironmentState(state_str)
                self.global_state["environment_states"][environment_id] = state.value
            except ValueError:
                pass
        
        # Update faction control
        if "controlling_faction" in environment.content_data:
            faction_id = environment.content_data["controlling_faction"]
            if faction_id:
                self.set_faction_territory(faction_id, environment_id)
        
        # Update resource distribution
        if "resources" in environment.content_data and isinstance(environment.content_data["resources"], dict):
            for resource_id, amount in environment.content_data["resources"].items():
                if resource_id not in self.global_state["resource_distribution"]:
                    self.global_state["resource_distribution"][resource_id] = {}
                self.global_state["resource_distribution"][resource_id][environment_id] = amount
