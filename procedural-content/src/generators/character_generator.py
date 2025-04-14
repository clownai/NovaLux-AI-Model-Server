"""
Character Generator Module

This module provides specialized functionality for generating procedural characters
in the NovaLux ecosystem, creating dynamic NPCs and entities that adapt to player
preferences and behavior patterns.

The module supports:
- Procedural NPC generation
- Dynamic character personalities
- Faction-aligned character traits
- Adaptive character relationships
- Character evolution based on world events
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


class CharacterRole(Enum):
    """Roles that characters can play in the game world."""
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    FACTION_LEADER = "faction_leader"
    ENFORCER = "enforcer"
    INFORMANT = "informant"
    RIVAL = "rival"
    ALLY = "ally"
    MENTOR = "mentor"
    GAMBLER = "gambler"
    HACKER = "hacker"
    FIXER = "fixer"
    ENTERTAINER = "entertainer"
    CORPORATE = "corporate"
    OUTCAST = "outcast"


class CharacterTrait(Enum):
    """Personality traits for characters."""
    AMBITIOUS = "ambitious"
    CAUTIOUS = "cautious"
    CHARISMATIC = "charismatic"
    CUNNING = "cunning"
    LOYAL = "loyal"
    GREEDY = "greedy"
    HONORABLE = "honorable"
    RUTHLESS = "ruthless"
    PARANOID = "paranoid"
    RECKLESS = "reckless"
    MYSTERIOUS = "mysterious"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    DISCIPLINED = "disciplined"
    REBELLIOUS = "rebellious"


class RelationshipType(Enum):
    """Types of relationships between characters."""
    ALLY = "ally"
    RIVAL = "rival"
    ENEMY = "enemy"
    FRIEND = "friend"
    MENTOR = "mentor"
    SUBORDINATE = "subordinate"
    SUPERIOR = "superior"
    FAMILY = "family"
    BUSINESS = "business"
    ROMANTIC = "romantic"
    NEUTRAL = "neutral"


class CharacterGenerator:
    """
    Specialized generator for procedural characters.
    
    This class extends the core procedural content generation system with
    character-specific functionality, creating dynamic NPCs that adapt to
    player preferences and behavior patterns.
    """
    
    def __init__(self, content_generator: ProceduralContentGenerator):
        """
        Initialize the character generator.
        
        Args:
            content_generator: Core procedural content generator
        """
        self.content_generator = content_generator
        self.character_templates: Dict[str, ContentTemplate] = {}
        self.character_relationships: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.character_evolution: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_character_template(self, template: ContentTemplate) -> bool:
        """
        Register a character template.
        
        Args:
            template: Character template to register
            
        Returns:
            True if registration successful, False otherwise
        """
        # Verify this is a character template
        if template.content_type != ContentType.CHARACTER:
            print(f"Template {template.id} is not a character template")
            return False
        
        # Register with core generator
        success = self.content_generator.register_template(template)
        if success:
            self.character_templates[template.id] = template
        
        return success
    
    def generate_character(self, player_id: Optional[str] = None,
                         role: Optional[CharacterRole] = None,
                         faction: Optional[ContentFaction] = None,
                         template_id: Optional[str] = None,
                         params: Optional[Dict[str, Any]] = None) -> GeneratedContent:
        """
        Generate a character based on player preferences.
        
        Args:
            player_id: Player ID for personalization (optional)
            role: Character role (optional)
            faction: Character faction (optional)
            template_id: Specific template ID to use (optional)
            params: Additional generation parameters (optional)
            
        Returns:
            Generated character content
        """
        # Initialize parameters
        if params is None:
            params = {}
        
        # Add role to parameters if specified
        if role is not None:
            if "variables" not in params:
                params["variables"] = {}
            params["variables"]["role"] = role.value
        
        # Add faction to parameters if specified
        if faction is not None:
            if "variables" not in params:
                params["variables"] = {}
            params["variables"]["faction"] = faction.value
        
        # Generate character content
        character = self.content_generator.generate_content(
            content_type=ContentType.CHARACTER,
            player_id=player_id,
            template_id=template_id,
            params=params,
            strategy=GenerationStrategy.TEMPLATE_BASED
        )
        
        # Post-process character
        self._post_process_character(character, player_id)
        
        return character
    
    def create_relationship(self, character_id1: str, character_id2: str,
                          relationship_type: RelationshipType,
                          strength: float = 0.5,
                          details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create or update a relationship between two characters.
        
        Args:
            character_id1: First character ID
            character_id2: Second character ID
            relationship_type: Type of relationship
            strength: Relationship strength (0-1)
            details: Additional relationship details (optional)
            
        Returns:
            True if successful, False otherwise
        """
        # Initialize relationship data
        if character_id1 not in self.character_relationships:
            self.character_relationships[character_id1] = {}
        
        if character_id2 not in self.character_relationships:
            self.character_relationships[character_id2] = {}
        
        # Create relationship data
        relationship_data = {
            "type": relationship_type.value,
            "strength": max(0.0, min(1.0, strength)),
            "established_at": time.time(),
            "updated_at": time.time()
        }
        
        # Add details if provided
        if details is not None:
            relationship_data.update(details)
        
        # Set relationships (bidirectional)
        self.character_relationships[character_id1][character_id2] = relationship_data
        
        # Create inverse relationship
        inverse_relationship = self._get_inverse_relationship(relationship_type)
        inverse_data = copy.deepcopy(relationship_data)
        inverse_data["type"] = inverse_relationship.value
        
        self.character_relationships[character_id2][character_id1] = inverse_data
        
        return True
    
    def get_character_relationships(self, character_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all relationships for a character.
        
        Args:
            character_id: Character ID
            
        Returns:
            Dictionary mapping related character IDs to relationship data
        """
        return self.character_relationships.get(character_id, {})
    
    def evolve_character(self, character_id: str, evolution_data: Dict[str, Any]) -> bool:
        """
        Record character evolution based on game events.
        
        Args:
            character_id: Character ID
            evolution_data: Evolution data (must include 'reason')
            
        Returns:
            True if successful, False otherwise
        """
        # Initialize evolution history
        if character_id not in self.character_evolution:
            self.character_evolution[character_id] = []
        
        # Add timestamp
        evolution_data["timestamp"] = time.time()
        
        # Add to evolution history
        self.character_evolution[character_id].append(evolution_data)
        
        return True
    
    def get_character_evolution(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Get evolution history for a character.
        
        Args:
            character_id: Character ID
            
        Returns:
            List of evolution events in chronological order
        """
        return self.character_evolution.get(character_id, [])
    
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
        # Initialize parameters
        if params is None:
            params = {}
        
        # Generate characters
        characters = []
        
        for i in range(group_size):
            # Determine role
            role = None
            if roles is not None and i < len(roles):
                role = roles[i]
            
            # Create character-specific parameters
            char_params = copy.deepcopy(params)
            if "variables" not in char_params:
                char_params["variables"] = {}
            
            char_params["variables"]["group_index"] = i
            char_params["variables"]["group_size"] = group_size
            
            # Generate character
            character = self.generate_character(
                player_id=player_id,
                role=role,
                faction=faction,
                params=char_params
            )
            
            characters.append(character)
        
        # Create relationships between characters
        for i, char1 in enumerate(characters):
            for j, char2 in enumerate(characters):
                if i != j:
                    # Determine relationship type based on roles
                    relationship_type = self._determine_group_relationship(
                        char1.content_data.get("role"),
                        char2.content_data.get("role")
                    )
                    
                    # Create relationship
                    self.create_relationship(
                        character_id1=char1.id,
                        character_id2=char2.id,
                        relationship_type=relationship_type,
                        strength=random.uniform(0.6, 0.9)  # Group members have strong relationships
                    )
        
        return characters
    
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
                "character_relationships": self.character_relationships,
                "character_evolution": self.character_evolution
            }
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving character generator state: {e}")
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
            
            # Load character relationships
            self.character_relationships = data.get("character_relationships", {})
            
            # Load character evolution
            self.character_evolution = data.get("character_evolution", {})
            
            return True
        
        except Exception as e:
            print(f"Error loading character generator state: {e}")
            return False
    
    def _post_process_character(self, character: GeneratedContent, player_id: Optional[str]) -> None:
        """
        Post-process a generated character.
        
        Args:
            character: Generated character content
            player_id: Player ID (optional)
        """
        # Add unique character ID to content data
        if "character_id" not in character.content_data:
            character.content_data["character_id"] = character.id
        
        # Add timestamp
        if "generated_at" not in character.content_data:
            character.content_data["generated_at"] = character.timestamp
        
        # Add player ID if available
        if player_id is not None and "player_id" not in character.content_data:
            character.content_data["player_id"] = player_id
        
        # Ensure traits are properly structured
        if "traits" in character.content_data and isinstance(character.content_data["traits"], list):
            traits = []
            for trait in character.content_data["traits"]:
                if isinstance(trait, str):
                    try:
                        # Try to convert to enum
                        trait_enum = CharacterTrait(trait)
                        traits.append(trait_enum.value)
                    except ValueError:
                        # Keep as is if not a valid enum
                        traits.append(trait)
            character.content_data["traits"] = traits
        
        # Ensure role is properly structured
        if "role" in character.content_data and isinstance(character.content_data["role"], str):
            try:
                # Try to convert to enum
                role_enum = CharacterRole(character.content_data["role"])
                character.content_data["role"] = role_enum.value
            except ValueError:
                # Keep as is if not a valid enum
                pass
    
    def _get_inverse_relationship(self, relationship_type: RelationshipType) -> RelationshipType:
        """
        Get the inverse of a relationship type.
        
        Args:
            relationship_type: Relationship type
            
        Returns:
            Inverse relationship type
        """
        # Define inverse relationships
        inverse_map = {
            RelationshipType.ALLY: RelationshipType.ALLY,
            RelationshipType.RIVAL: RelationshipType.RIVAL,
            RelationshipType.ENEMY: RelationshipType.ENEMY,
            RelationshipType.FRIEND: RelationshipType.FRIEND,
            RelationshipType.MENTOR: RelationshipType.SUBORDINATE,
            RelationshipType.SUBORDINATE: RelationshipType.SUPERIOR,
            RelationshipType.SUPERIOR: RelationshipType.SUBORDINATE,
            RelationshipType.FAMILY: RelationshipType.FAMILY,
            RelationshipType.BUSINESS: RelationshipType.BUSINESS,
            RelationshipType.ROMANTIC: RelationshipType.ROMANTIC,
            RelationshipType.NEUTRAL: RelationshipType.NEUTRAL
        }
        
        return inverse_map.get(relationship_type, RelationshipType.NEUTRAL)
    
    def _determine_group_relationship(self, role1: Optional[str], role2: Optional[str]) -> RelationshipType:
        """
        Determine relationship type between two characters in a group.
        
        Args:
            role1: Role of first character
            role2: Role of second character
            
        Returns:
            Appropriate relationship type
        """
        # Convert string roles to enums if possible
        role1_enum = None
        role2_enum = None
        
        if role1 is not None:
            try:
                role1_enum = CharacterRole(role1)
            except ValueError:
                pass
        
        if role2 is not None:
            try:
                role2_enum = CharacterRole(role2)
            except ValueError:
                pass
        
        # Leader relationships
        if role1_enum == CharacterRole.FACTION_LEADER:
            if role2_enum in [CharacterRole.ENFORCER, CharacterRole.FIXER, CharacterRole.HACKER]:
                return RelationshipType.SUPERIOR
            return RelationshipType.ALLY
        
        if role2_enum == CharacterRole.FACTION_LEADER:
            if role1_enum in [CharacterRole.ENFORCER, CharacterRole.FIXER, CharacterRole.HACKER]:
                return RelationshipType.SUBORDINATE
            return RelationshipType.ALLY
        
        # Mentor relationships
        if role1_enum == CharacterRole.MENTOR:
            return RelationshipType.MENTOR
        
        if role2_enum == CharacterRole.MENTOR:
            return RelationshipType.SUBORDINATE
        
        # Business relationships
        if role1_enum in [CharacterRole.MERCHANT, CharacterRole.FIXER] and role2_enum in [CharacterRole.MERCHANT, CharacterRole.FIXER]:
            return RelationshipType.BUSINESS
        
        # Default to ally
        return RelationshipType.ALLY
