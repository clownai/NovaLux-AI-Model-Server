"""
Procedural Content Generation Core Module

This module provides the core framework for procedural content generation in NovaLux,
enabling dynamic creation of game content based on player preferences and behavior patterns.

The system supports:
- Template-based content generation
- Player preference-driven content adaptation
- Multi-layered content composition
- Constraint-based generation
- Content evaluation and selection
"""

from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
import json
import random
import uuid
import time
import math
import copy


class ContentType(Enum):
    """Types of content that can be procedurally generated."""
    QUEST = "quest"
    CHARACTER = "character"
    LOCATION = "location"
    ITEM = "item"
    EVENT = "event"
    DIALOGUE = "dialogue"
    NARRATIVE = "narrative"
    CHALLENGE = "challenge"
    REWARD = "reward"
    ENVIRONMENT = "environment"


class ContentComplexity(Enum):
    """Complexity levels for generated content."""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    VERY_COMPLEX = 4
    EPIC = 5


class ContentTheme(Enum):
    """Thematic elements for content generation."""
    CYBERPUNK = "cyberpunk"
    NOIR = "noir"
    CORPORATE = "corporate"
    UNDERGROUND = "underground"
    DYSTOPIAN = "dystopian"
    TECHNOLOGICAL = "technological"
    REBELLIOUS = "rebellious"
    LUXURIOUS = "luxurious"
    GRITTY = "gritty"
    FUTURISTIC = "futuristic"


class ContentTone(Enum):
    """Emotional tone for generated content."""
    DARK = "dark"
    LIGHT = "light"
    HUMOROUS = "humorous"
    SERIOUS = "serious"
    MYSTERIOUS = "mysterious"
    TENSE = "tense"
    HOPEFUL = "hopeful"
    MELANCHOLIC = "melancholic"
    THRILLING = "thrilling"
    PHILOSOPHICAL = "philosophical"


class ContentFaction(Enum):
    """Factions in the NovaLux universe."""
    CORPORATE = "corporate"
    UNDERGROUND = "underground"
    NEUTRAL = "neutral"
    ROGUE_AI = "rogue_ai"
    ENFORCERS = "enforcers"
    HACKERS = "hackers"
    ELITES = "elites"
    OUTCASTS = "outcasts"


class GenerationStrategy(Enum):
    """Strategies for content generation."""
    TEMPLATE_BASED = "template_based"
    GRAMMAR_BASED = "grammar_based"
    EVOLUTIONARY = "evolutionary"
    CONSTRAINT_BASED = "constraint_based"
    NEURAL = "neural"
    HYBRID = "hybrid"


class ContentConstraint:
    """Base class for constraints on generated content."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize a content constraint.
        
        Args:
            name: Name of the constraint
            description: Description of what the constraint enforces
        """
        self.name = name
        self.description = description
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        Validate if content meets this constraint.
        
        Args:
            content: Content to validate
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate()")
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class RequiredFieldConstraint(ContentConstraint):
    """Constraint that requires specific fields to be present."""
    
    def __init__(self, required_fields: List[str]):
        """
        Initialize a required field constraint.
        
        Args:
            required_fields: List of field names that must be present
        """
        super().__init__(
            name="Required Fields",
            description=f"Content must include these fields: {', '.join(required_fields)}"
        )
        self.required_fields = required_fields
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        Validate if content has all required fields.
        
        Args:
            content: Content to validate
            
        Returns:
            True if all required fields are present, False otherwise
        """
        return all(field in content for field in self.required_fields)


class ValueRangeConstraint(ContentConstraint):
    """Constraint that requires a numeric field to be within a range."""
    
    def __init__(self, field: str, min_value: float, max_value: float):
        """
        Initialize a value range constraint.
        
        Args:
            field: Field name to check
            min_value: Minimum allowed value
            max_value: Maximum allowed value
        """
        super().__init__(
            name=f"{field} Range",
            description=f"{field} must be between {min_value} and {max_value}"
        )
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        Validate if field value is within range.
        
        Args:
            content: Content to validate
            
        Returns:
            True if field value is within range, False otherwise
        """
        if self.field not in content:
            return False
        
        value = content[self.field]
        if not isinstance(value, (int, float)):
            return False
        
        return self.min_value <= value <= self.max_value


class EnumValueConstraint(ContentConstraint):
    """Constraint that requires a field to have one of a set of values."""
    
    def __init__(self, field: str, allowed_values: List[Any]):
        """
        Initialize an enum value constraint.
        
        Args:
            field: Field name to check
            allowed_values: List of allowed values
        """
        super().__init__(
            name=f"{field} Values",
            description=f"{field} must be one of: {', '.join(str(v) for v in allowed_values)}"
        )
        self.field = field
        self.allowed_values = allowed_values
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        Validate if field value is one of allowed values.
        
        Args:
            content: Content to validate
            
        Returns:
            True if field value is allowed, False otherwise
        """
        if self.field not in content:
            return False
        
        return content[self.field] in self.allowed_values


class RelationConstraint(ContentConstraint):
    """Constraint that requires a relationship between two fields."""
    
    def __init__(self, field1: str, field2: str, relation: str, description: str):
        """
        Initialize a relation constraint.
        
        Args:
            field1: First field name
            field2: Second field name
            relation: Type of relation (e.g., "greater_than", "equal", "not_equal")
            description: Description of the relation
        """
        super().__init__(
            name=f"{field1} {relation} {field2}",
            description=description
        )
        self.field1 = field1
        self.field2 = field2
        self.relation = relation
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        Validate if relation between fields is satisfied.
        
        Args:
            content: Content to validate
            
        Returns:
            True if relation is satisfied, False otherwise
        """
        if self.field1 not in content or self.field2 not in content:
            return False
        
        value1 = content[self.field1]
        value2 = content[self.field2]
        
        if self.relation == "greater_than":
            return value1 > value2
        elif self.relation == "greater_than_or_equal":
            return value1 >= value2
        elif self.relation == "less_than":
            return value1 < value2
        elif self.relation == "less_than_or_equal":
            return value1 <= value2
        elif self.relation == "equal":
            return value1 == value2
        elif self.relation == "not_equal":
            return value1 != value2
        else:
            return False


class CustomConstraint(ContentConstraint):
    """Constraint with custom validation logic."""
    
    def __init__(self, name: str, description: str, validation_func: Callable[[Dict[str, Any]], bool]):
        """
        Initialize a custom constraint.
        
        Args:
            name: Name of the constraint
            description: Description of what the constraint enforces
            validation_func: Function that takes content and returns True if valid
        """
        super().__init__(name=name, description=description)
        self.validation_func = validation_func
    
    def validate(self, content: Dict[str, Any]) -> bool:
        """
        Validate using custom validation function.
        
        Args:
            content: Content to validate
            
        Returns:
            True if validation function returns True, False otherwise
        """
        return self.validation_func(content)


@dataclass
class ContentTemplate:
    """Template for generating procedural content."""
    
    id: str
    name: str
    content_type: ContentType
    description: str
    template_data: Dict[str, Any]
    constraints: List[ContentConstraint] = field(default_factory=list)
    complexity: ContentComplexity = ContentComplexity.MODERATE
    themes: List[ContentTheme] = field(default_factory=list)
    tones: List[ContentTone] = field(default_factory=list)
    factions: List[ContentFaction] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate that the template is well-formed.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        is_valid = True
        errors = []
        
        # Check required fields
        required_fields = ["structure", "variables", "content_blocks"]
        for field in required_fields:
            if field not in self.template_data:
                is_valid = False
                errors.append(f"Missing required field: {field}")
        
        # Check structure
        if "structure" in self.template_data:
            structure = self.template_data["structure"]
            if not isinstance(structure, dict):
                is_valid = False
                errors.append("Structure must be a dictionary")
        
        # Check variables
        if "variables" in self.template_data:
            variables = self.template_data["variables"]
            if not isinstance(variables, dict):
                is_valid = False
                errors.append("Variables must be a dictionary")
        
        # Check content blocks
        if "content_blocks" in self.template_data:
            content_blocks = self.template_data["content_blocks"]
            if not isinstance(content_blocks, dict):
                is_valid = False
                errors.append("Content blocks must be a dictionary")
        
        return is_valid, errors


@dataclass
class PlayerPreferenceProfile:
    """Profile of player preferences for content generation."""
    
    player_id: str
    preferred_themes: Dict[ContentTheme, float] = field(default_factory=dict)
    preferred_tones: Dict[ContentTone, float] = field(default_factory=dict)
    preferred_factions: Dict[ContentFaction, float] = field(default_factory=dict)
    preferred_complexity: Dict[ContentType, ContentComplexity] = field(default_factory=dict)
    content_engagement: Dict[ContentType, float] = field(default_factory=dict)
    custom_preferences: Dict[str, Any] = field(default_factory=dict)
    
    def get_theme_preference(self, theme: ContentTheme) -> float:
        """
        Get preference score for a theme.
        
        Args:
            theme: Theme to get preference for
            
        Returns:
            Preference score (0-1)
        """
        return self.preferred_themes.get(theme, 0.5)
    
    def get_tone_preference(self, tone: ContentTone) -> float:
        """
        Get preference score for a tone.
        
        Args:
            tone: Tone to get preference for
            
        Returns:
            Preference score (0-1)
        """
        return self.preferred_tones.get(tone, 0.5)
    
    def get_faction_preference(self, faction: ContentFaction) -> float:
        """
        Get preference score for a faction.
        
        Args:
            faction: Faction to get preference for
            
        Returns:
            Preference score (0-1)
        """
        return self.preferred_factions.get(faction, 0.5)
    
    def get_complexity_preference(self, content_type: ContentType) -> ContentComplexity:
        """
        Get preferred complexity for a content type.
        
        Args:
            content_type: Content type to get complexity for
            
        Returns:
            Preferred complexity level
        """
        return self.preferred_complexity.get(content_type, ContentComplexity.MODERATE)
    
    def get_engagement_score(self, content_type: ContentType) -> float:
        """
        Get engagement score for a content type.
        
        Args:
            content_type: Content type to get engagement for
            
        Returns:
            Engagement score (0-1)
        """
        return self.content_engagement.get(content_type, 0.5)
    
    def update_preference(self, preference_type: str, key: Any, value: float):
        """
        Update a preference value.
        
        Args:
            preference_type: Type of preference ("theme", "tone", "faction", "complexity", "engagement")
            key: Preference key (theme, tone, faction, content type)
            value: New preference value
        """
        if preference_type == "theme" and isinstance(key, ContentTheme):
            self.preferred_themes[key] = max(0.0, min(1.0, value))
        elif preference_type == "tone" and isinstance(key, ContentTone):
            self.preferred_tones[key] = max(0.0, min(1.0, value))
        elif preference_type == "faction" and isinstance(key, ContentFaction):
            self.preferred_factions[key] = max(0.0, min(1.0, value))
        elif preference_type == "complexity" and isinstance(key, ContentType):
            if isinstance(value, ContentComplexity):
                self.preferred_complexity[key] = value
            elif isinstance(value, int) and 1 <= value <= 5:
                self.preferred_complexity[key] = ContentComplexity(value)
        elif preference_type == "engagement" and isinstance(key, ContentType):
            self.content_engagement[key] = max(0.0, min(1.0, value))
        elif preference_type == "custom":
            self.custom_preferences[key] = value


@dataclass
class GeneratedContent:
    """Content generated by the procedural content system."""
    
    id: str
    content_type: ContentType
    name: str
    description: str
    content_data: Dict[str, Any]
    template_id: str
    generation_params: Dict[str, Any]
    player_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    version: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the content
        """
        return {
            "id": self.id,
            "content_type": self.content_type.value,
            "name": self.name,
            "description": self.description,
            "content_data": self.content_data,
            "template_id": self.template_id,
            "generation_params": self.generation_params,
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "version": self.version,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedContent':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            GeneratedContent instance
        """
        content_type_str = data.get("content_type")
        content_type = ContentType(content_type_str) if content_type_str else ContentType.QUEST
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content_type=content_type,
            name=data.get("name", ""),
            description=data.get("description", ""),
            content_data=data.get("content_data", {}),
            template_id=data.get("template_id", ""),
            generation_params=data.get("generation_params", {}),
            player_id=data.get("player_id"),
            timestamp=data.get("timestamp", time.time()),
            version=data.get("version", 1),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


class ContentEvaluator:
    """Evaluates generated content for quality and player fit."""
    
    def __init__(self):
        """Initialize the content evaluator."""
        self.evaluation_metrics = {
            "coherence": self._evaluate_coherence,
            "novelty": self._evaluate_novelty,
            "player_fit": self._evaluate_player_fit,
            "complexity_match": self._evaluate_complexity_match,
            "theme_match": self._evaluate_theme_match,
            "tone_match": self._evaluate_tone_match,
            "faction_match": self._evaluate_faction_match
        }
    
    def evaluate(self, content: GeneratedContent, 
               player_profile: Optional[PlayerPreferenceProfile] = None,
               metrics: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Evaluate content on multiple metrics.
        
        Args:
            content: Content to evaluate
            player_profile: Player preference profile for personalization metrics
            metrics: List of metrics to evaluate (default: all)
            
        Returns:
            Dictionary of metric scores (0-1)
        """
        results = {}
        
        # Determine which metrics to evaluate
        if metrics is None:
            metrics_to_evaluate = list(self.evaluation_metrics.keys())
        else:
            metrics_to_evaluate = [m for m in metrics if m in self.evaluation_metrics]
        
        # Skip player-specific metrics if no profile provided
        if player_profile is None:
            metrics_to_evaluate = [m for m in metrics_to_evaluate 
                                 if m not in ["player_fit", "complexity_match", 
                                             "theme_match", "tone_match", 
                                             "faction_match"]]
        
        # Evaluate each metric
        for metric in metrics_to_evaluate:
            evaluation_func = self.evaluation_metrics[metric]
            if metric in ["player_fit", "complexity_match", "theme_match", 
                         "tone_match", "faction_match"]:
                results[metric] = evaluation_func(content, player_profile)
            else:
                results[metric] = evaluation_func(content)
        
        # Calculate overall score
        if results:
            results["overall"] = sum(results.values()) / len(results)
        else:
            results["overall"] = 0.0
        
        return results
    
    def _evaluate_coherence(self, content: GeneratedContent) -> float:
        """
        Evaluate content coherence.
        
        Args:
            content: Content to evaluate
            
        Returns:
            Coherence score (0-1)
        """
        # Simple coherence check based on content structure
        coherence_score = 0.5  # Default moderate coherence
        
        # Check if content has required fields based on type
        if content.content_type == ContentType.QUEST:
            required_fields = ["objectives", "steps", "rewards"]
            if all(field in content.content_data for field in required_fields):
                coherence_score += 0.2
            
            # Check if quest steps are sequential
            if "steps" in content.content_data and isinstance(content.content_data["steps"], list):
                steps = content.content_data["steps"]
                if len(steps) > 1 and all("step_number" in step for step in steps):
                    step_numbers = [step["step_number"] for step in steps]
                    if step_numbers == sorted(step_numbers) and len(set(step_numbers)) == len(step_numbers):
                        coherence_score += 0.2
        
        elif content.content_type == ContentType.CHARACTER:
            required_fields = ["name", "description", "traits"]
            if all(field in content.content_data for field in required_fields):
                coherence_score += 0.2
            
            # Check if character traits are consistent with faction
            if "faction" in content.content_data and "traits" in content.content_data:
                faction = content.content_data["faction"]
                traits = content.content_data["traits"]
                
                # Simple faction-trait consistency check
                faction_trait_map = {
                    "corporate": ["ambitious", "disciplined", "wealthy"],
                    "underground": ["rebellious", "resourceful", "secretive"],
                    "hackers": ["technical", "curious", "independent"],
                    "elites": ["privileged", "influential", "sophisticated"]
                }
                
                if faction in faction_trait_map:
                    matching_traits = [t for t in traits if t in faction_trait_map[faction]]
                    if matching_traits:
                        coherence_score += 0.2
        
        # Clamp to valid range
        return max(0.0, min(1.0, coherence_score))
    
    def _evaluate_novelty(self, content: GeneratedContent) -> float:
        """
        Evaluate content novelty.
        
        Args:
            content: Content to evaluate
            
        Returns:
            Novelty score (0-1)
        """
        # Simple novelty check based on content complexity and uniqueness
        novelty_score = 0.5  # Default moderate novelty
        
        # More complex content tends to be more novel
        if hasattr(content, "complexity") and isinstance(content.complexity, ContentComplexity):
            complexity_bonus = (content.complexity.value - 1) / 4  # 0-1 scale
            novelty_score += complexity_bonus * 0.3
        
        # More tags and metadata suggest more unique content
        if content.tags:
            tag_bonus = min(len(content.tags) / 10, 1.0)  # Cap at 10 tags
            novelty_score += tag_bonus * 0.2
        
        # Metadata richness suggests more detailed, unique content
        if content.metadata:
            metadata_bonus = min(len(content.metadata) / 5, 1.0)  # Cap at 5 metadata items
            novelty_score += metadata_bonus * 0.2
        
        # Clamp to valid range
        return max(0.0, min(1.0, novelty_score))
    
    def _evaluate_player_fit(self, content: GeneratedContent, 
                           player_profile: PlayerPreferenceProfile) -> float:
        """
        Evaluate how well content fits player preferences.
        
        Args:
            content: Content to evaluate
            player_profile: Player preference profile
            
        Returns:
            Player fit score (0-1)
        """
        # Combine various preference matches
        theme_match = self._evaluate_theme_match(content, player_profile)
        tone_match = self._evaluate_tone_match(content, player_profile)
        faction_match = self._evaluate_faction_match(content, player_profile)
        complexity_match = self._evaluate_complexity_match(content, player_profile)
        
        # Weight the components
        player_fit = (
            theme_match * 0.3 +
            tone_match * 0.2 +
            faction_match * 0.2 +
            complexity_match * 0.3
        )
        
        return player_fit
    
    def _evaluate_complexity_match(self, content: GeneratedContent, 
                                 player_profile: PlayerPreferenceProfile) -> float:
        """
        Evaluate how well content complexity matches player preference.
        
        Args:
            content: Content to evaluate
            player_profile: Player preference profile
            
        Returns:
            Complexity match score (0-1)
        """
        # Get preferred complexity for this content type
        preferred_complexity = player_profile.get_complexity_preference(content.content_type)
        
        # Get content complexity
        content_complexity = None
        if hasattr(content, "complexity") and isinstance(content.complexity, ContentComplexity):
            content_complexity = content.complexity
        elif "complexity" in content.metadata:
            complexity_value = content.metadata["complexity"]
            if isinstance(complexity_value, int) and 1 <= complexity_value <= 5:
                content_complexity = ContentComplexity(complexity_value)
            elif isinstance(complexity_value, str):
                try:
                    content_complexity = ContentComplexity[complexity_value.upper()]
                except (KeyError, ValueError):
                    pass
        
        # Default to moderate if not specified
        if content_complexity is None:
            content_complexity = ContentComplexity.MODERATE
        
        # Calculate match score based on difference
        complexity_diff = abs(content_complexity.value - preferred_complexity.value)
        max_diff = 4  # Maximum possible difference (1 to 5)
        
        # Convert to 0-1 scale (1 = perfect match, 0 = maximum difference)
        match_score = 1.0 - (complexity_diff / max_diff)
        
        return match_score
    
    def _evaluate_theme_match(self, content: GeneratedContent, 
                            player_profile: PlayerPreferenceProfile) -> float:
        """
        Evaluate how well content themes match player preferences.
        
        Args:
            content: Content to evaluate
            player_profile: Player preference profile
            
        Returns:
            Theme match score (0-1)
        """
        # Get content themes
        content_themes = []
        
        # Check content.tags for theme values
        for tag in content.tags:
            try:
                theme = ContentTheme(tag)
                content_themes.append(theme)
            except (ValueError, KeyError):
                pass
        
        # Check content.metadata for themes
        if "themes" in content.metadata:
            themes_data = content.metadata["themes"]
            if isinstance(themes_data, list):
                for theme_data in themes_data:
                    if isinstance(theme_data, str):
                        try:
                            theme = ContentTheme(theme_data)
                            content_themes.append(theme)
                        except (ValueError, KeyError):
                            pass
        
        # If no themes found, return neutral score
        if not content_themes:
            return 0.5
        
        # Calculate average preference score for content themes
        theme_scores = [player_profile.get_theme_preference(theme) for theme in content_themes]
        average_score = sum(theme_scores) / len(theme_scores)
        
        return average_score
    
    def _evaluate_tone_match(self, content: GeneratedContent, 
                           player_profile: PlayerPreferenceProfile) -> float:
        """
        Evaluate how well content tones match player preferences.
        
        Args:
            content: Content to evaluate
            player_profile: Player preference profile
            
        Returns:
            Tone match score (0-1)
        """
        # Get content tones
        content_tones = []
        
        # Check content.tags for tone values
        for tag in content.tags:
            try:
                tone = ContentTone(tag)
                content_tones.append(tone)
            except (ValueError, KeyError):
                pass
        
        # Check content.metadata for tones
        if "tones" in content.metadata:
            tones_data = content.metadata["tones"]
            if isinstance(tones_data, list):
                for tone_data in tones_data:
                    if isinstance(tone_data, str):
                        try:
                            tone = ContentTone(tone_data)
                            content_tones.append(tone)
                        except (ValueError, KeyError):
                            pass
        
        # If no tones found, return neutral score
        if not content_tones:
            return 0.5
        
        # Calculate average preference score for content tones
        tone_scores = [player_profile.get_tone_preference(tone) for tone in content_tones]
        average_score = sum(tone_scores) / len(tone_scores)
        
        return average_score
    
    def _evaluate_faction_match(self, content: GeneratedContent, 
                              player_profile: PlayerPreferenceProfile) -> float:
        """
        Evaluate how well content factions match player preferences.
        
        Args:
            content: Content to evaluate
            player_profile: Player preference profile
            
        Returns:
            Faction match score (0-1)
        """
        # Get content factions
        content_factions = []
        
        # Check content.content_data for faction
        if "faction" in content.content_data:
            faction_data = content.content_data["faction"]
            if isinstance(faction_data, str):
                try:
                    faction = ContentFaction(faction_data)
                    content_factions.append(faction)
                except (ValueError, KeyError):
                    pass
        
        # Check content.tags for faction values
        for tag in content.tags:
            try:
                faction = ContentFaction(tag)
                content_factions.append(faction)
            except (ValueError, KeyError):
                pass
        
        # Check content.metadata for factions
        if "factions" in content.metadata:
            factions_data = content.metadata["factions"]
            if isinstance(factions_data, list):
                for faction_data in factions_data:
                    if isinstance(faction_data, str):
                        try:
                            faction = ContentFaction(faction_data)
                            content_factions.append(faction)
                        except (ValueError, KeyError):
                            pass
        
        # If no factions found, return neutral score
        if not content_factions:
            return 0.5
        
        # Calculate average preference score for content factions
        faction_scores = [player_profile.get_faction_preference(faction) for faction in content_factions]
        average_score = sum(faction_scores) / len(faction_scores)
        
        return average_score


class ProceduralContentGenerator:
    """
    Core system for procedural content generation.
    
    This class manages templates, player preferences, and content generation
    to create dynamic game content that adapts to player behavior patterns.
    """
    
    def __init__(self):
        """Initialize the procedural content generator."""
        # Templates by ID
        self.templates: Dict[str, ContentTemplate] = {}
        
        # Templates by content type
        self.templates_by_type: Dict[ContentType, List[str]] = {
            content_type: [] for content_type in ContentType
        }
        
        # Player preference profiles
        self.player_profiles: Dict[str, PlayerPreferenceProfile] = {}
        
        # Generated content history
        self.content_history: Dict[str, List[GeneratedContent]] = {}
        
        # Content evaluator
        self.evaluator = ContentEvaluator()
        
        # Generation strategies
        self.generation_strategies: Dict[GenerationStrategy, Callable] = {
            GenerationStrategy.TEMPLATE_BASED: self._generate_template_based,
            GenerationStrategy.GRAMMAR_BASED: self._generate_grammar_based,
            GenerationStrategy.EVOLUTIONARY: self._generate_evolutionary,
            GenerationStrategy.CONSTRAINT_BASED: self._generate_constraint_based,
            GenerationStrategy.NEURAL: self._generate_neural,
            GenerationStrategy.HYBRID: self._generate_hybrid
        }
    
    def register_template(self, template: ContentTemplate) -> bool:
        """
        Register a content template.
        
        Args:
            template: Template to register
            
        Returns:
            True if registration successful, False otherwise
        """
        # Validate template
        is_valid, errors = template.validate()
        if not is_valid:
            print(f"Template validation failed: {', '.join(errors)}")
            return False
        
        # Register template
        self.templates[template.id] = template
        self.templates_by_type[template.content_type].append(template.id)
        
        return True
    
    def get_template(self, template_id: str) -> Optional[ContentTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template or None if not found
        """
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, content_type: ContentType) -> List[ContentTemplate]:
        """
        Get all templates for a content type.
        
        Args:
            content_type: Content type
            
        Returns:
            List of templates
        """
        template_ids = self.templates_by_type.get(content_type, [])
        return [self.templates[tid] for tid in template_ids if tid in self.templates]
    
    def register_player_profile(self, profile: PlayerPreferenceProfile) -> bool:
        """
        Register a player preference profile.
        
        Args:
            profile: Player profile to register
            
        Returns:
            True if registration successful, False otherwise
        """
        self.player_profiles[profile.player_id] = profile
        return True
    
    def get_player_profile(self, player_id: str) -> Optional[PlayerPreferenceProfile]:
        """
        Get a player profile by ID.
        
        Args:
            player_id: Player ID
            
        Returns:
            Player profile or None if not found
        """
        return self.player_profiles.get(player_id)
    
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
        profile = self.get_player_profile(player_id)
        if profile is None:
            return False
        
        profile.update_preference(preference_type, key, value)
        return True
    
    def generate_content(self, content_type: ContentType, player_id: Optional[str] = None,
                       template_id: Optional[str] = None, params: Optional[Dict[str, Any]] = None,
                       strategy: GenerationStrategy = GenerationStrategy.TEMPLATE_BASED) -> GeneratedContent:
        """
        Generate content based on type and player preferences.
        
        Args:
            content_type: Type of content to generate
            player_id: Player ID for personalization (optional)
            template_id: Specific template ID to use (optional)
            params: Additional generation parameters (optional)
            strategy: Generation strategy to use
            
        Returns:
            Generated content
        """
        # Initialize parameters
        if params is None:
            params = {}
        
        # Get player profile if available
        player_profile = None
        if player_id is not None:
            player_profile = self.get_player_profile(player_id)
        
        # Select template
        selected_template = None
        if template_id is not None:
            selected_template = self.get_template(template_id)
        elif player_profile is not None:
            # Select template based on player preferences
            selected_template = self._select_template_for_player(content_type, player_profile)
        else:
            # Select random template of the right type
            templates = self.get_templates_by_type(content_type)
            if templates:
                selected_template = random.choice(templates)
        
        # If no template found, return error content
        if selected_template is None:
            return self._create_error_content(
                content_type, 
                "No suitable template found",
                player_id
            )
        
        # Generate content using selected strategy
        generation_func = self.generation_strategies.get(strategy)
        if generation_func is None:
            return self._create_error_content(
                content_type,
                f"Unsupported generation strategy: {strategy}",
                player_id
            )
        
        # Generate content
        try:
            content = generation_func(selected_template, player_profile, params)
            
            # Record in history
            if player_id is not None:
                if player_id not in self.content_history:
                    self.content_history[player_id] = []
                self.content_history[player_id].append(content)
            
            return content
        
        except Exception as e:
            return self._create_error_content(
                content_type,
                f"Error generating content: {str(e)}",
                player_id
            )
    
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
        player_profile = None
        if player_id is not None:
            player_profile = self.get_player_profile(player_id)
        
        return self.evaluator.evaluate(content, player_profile, metrics)
    
    def get_player_content_history(self, player_id: str) -> List[GeneratedContent]:
        """
        Get content history for a player.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of generated content
        """
        return self.content_history.get(player_id, [])
    
    def save_state(self, filepath: str) -> bool:
        """
        Save generator state to file.
        
        Args:
            filepath: Path to save state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for serialization
            data = {
                "templates": {},
                "player_profiles": {},
                "content_history": {}
            }
            
            # Serialize templates
            for template_id, template in self.templates.items():
                template_dict = {
                    "id": template.id,
                    "name": template.name,
                    "content_type": template.content_type.value,
                    "description": template.description,
                    "template_data": template.template_data,
                    "complexity": template.complexity.value,
                    "themes": [theme.value for theme in template.themes],
                    "tones": [tone.value for tone in template.tones],
                    "factions": [faction.value for faction in template.factions],
                    "tags": template.tags
                }
                data["templates"][template_id] = template_dict
            
            # Serialize player profiles
            for player_id, profile in self.player_profiles.items():
                profile_dict = {
                    "player_id": profile.player_id,
                    "preferred_themes": {theme.value: score for theme, score in profile.preferred_themes.items()},
                    "preferred_tones": {tone.value: score for tone, score in profile.preferred_tones.items()},
                    "preferred_factions": {faction.value: score for faction, score in profile.preferred_factions.items()},
                    "preferred_complexity": {ct.value: complexity.value for ct, complexity in profile.preferred_complexity.items()},
                    "content_engagement": {ct.value: score for ct, score in profile.content_engagement.items()},
                    "custom_preferences": profile.custom_preferences
                }
                data["player_profiles"][player_id] = profile_dict
            
            # Serialize content history
            for player_id, content_list in self.content_history.items():
                data["content_history"][player_id] = [content.to_dict() for content in content_list]
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving state: {e}")
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
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Clear current state
            self.templates = {}
            self.templates_by_type = {content_type: [] for content_type in ContentType}
            self.player_profiles = {}
            self.content_history = {}
            
            # Load templates
            for template_id, template_dict in data.get("templates", {}).items():
                content_type = ContentType(template_dict["content_type"])
                complexity = ContentComplexity(template_dict["complexity"])
                
                themes = []
                for theme_value in template_dict.get("themes", []):
                    try:
                        themes.append(ContentTheme(theme_value))
                    except (ValueError, KeyError):
                        pass
                
                tones = []
                for tone_value in template_dict.get("tones", []):
                    try:
                        tones.append(ContentTone(tone_value))
                    except (ValueError, KeyError):
                        pass
                
                factions = []
                for faction_value in template_dict.get("factions", []):
                    try:
                        factions.append(ContentFaction(faction_value))
                    except (ValueError, KeyError):
                        pass
                
                template = ContentTemplate(
                    id=template_dict["id"],
                    name=template_dict["name"],
                    content_type=content_type,
                    description=template_dict["description"],
                    template_data=template_dict["template_data"],
                    complexity=complexity,
                    themes=themes,
                    tones=tones,
                    factions=factions,
                    tags=template_dict.get("tags", [])
                )
                
                self.templates[template_id] = template
                self.templates_by_type[content_type].append(template_id)
            
            # Load player profiles
            for player_id, profile_dict in data.get("player_profiles", {}).items():
                preferred_themes = {}
                for theme_value, score in profile_dict.get("preferred_themes", {}).items():
                    try:
                        preferred_themes[ContentTheme(theme_value)] = score
                    except (ValueError, KeyError):
                        pass
                
                preferred_tones = {}
                for tone_value, score in profile_dict.get("preferred_tones", {}).items():
                    try:
                        preferred_tones[ContentTone(tone_value)] = score
                    except (ValueError, KeyError):
                        pass
                
                preferred_factions = {}
                for faction_value, score in profile_dict.get("preferred_factions", {}).items():
                    try:
                        preferred_factions[ContentFaction(faction_value)] = score
                    except (ValueError, KeyError):
                        pass
                
                preferred_complexity = {}
                for ct_value, complexity_value in profile_dict.get("preferred_complexity", {}).items():
                    try:
                        preferred_complexity[ContentType(ct_value)] = ContentComplexity(complexity_value)
                    except (ValueError, KeyError):
                        pass
                
                content_engagement = {}
                for ct_value, score in profile_dict.get("content_engagement", {}).items():
                    try:
                        content_engagement[ContentType(ct_value)] = score
                    except (ValueError, KeyError):
                        pass
                
                profile = PlayerPreferenceProfile(
                    player_id=profile_dict["player_id"],
                    preferred_themes=preferred_themes,
                    preferred_tones=preferred_tones,
                    preferred_factions=preferred_factions,
                    preferred_complexity=preferred_complexity,
                    content_engagement=content_engagement,
                    custom_preferences=profile_dict.get("custom_preferences", {})
                )
                
                self.player_profiles[player_id] = profile
            
            # Load content history
            for player_id, content_list in data.get("content_history", {}).items():
                self.content_history[player_id] = [
                    GeneratedContent.from_dict(content_dict) for content_dict in content_list
                ]
            
            return True
        
        except Exception as e:
            print(f"Error loading state: {e}")
            return False
    
    def _select_template_for_player(self, content_type: ContentType, 
                                  player_profile: PlayerPreferenceProfile) -> Optional[ContentTemplate]:
        """
        Select the best template for a player based on preferences.
        
        Args:
            content_type: Type of content to generate
            player_profile: Player preference profile
            
        Returns:
            Selected template or None if no suitable template found
        """
        templates = self.get_templates_by_type(content_type)
        if not templates:
            return None
        
        # Calculate scores for each template
        template_scores = []
        for template in templates:
            score = 0.0
            
            # Match complexity
            preferred_complexity = player_profile.get_complexity_preference(content_type)
            complexity_diff = abs(template.complexity.value - preferred_complexity.value)
            max_diff = 4  # Maximum possible difference (1 to 5)
            complexity_score = 1.0 - (complexity_diff / max_diff)
            score += complexity_score * 0.3
            
            # Match themes
            theme_scores = []
            for theme in template.themes:
                theme_scores.append(player_profile.get_theme_preference(theme))
            
            if theme_scores:
                theme_score = sum(theme_scores) / len(theme_scores)
                score += theme_score * 0.3
            
            # Match tones
            tone_scores = []
            for tone in template.tones:
                tone_scores.append(player_profile.get_tone_preference(tone))
            
            if tone_scores:
                tone_score = sum(tone_scores) / len(tone_scores)
                score += tone_score * 0.2
            
            # Match factions
            faction_scores = []
            for faction in template.factions:
                faction_scores.append(player_profile.get_faction_preference(faction))
            
            if faction_scores:
                faction_score = sum(faction_scores) / len(faction_scores)
                score += faction_score * 0.2
            
            template_scores.append((template, score))
        
        # Sort by score (descending)
        template_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Add some randomness to prevent always selecting the same template
        # 80% chance to select from top 3 templates (if available)
        if random.random() < 0.8 and len(template_scores) >= 3:
            return random.choice([t for t, _ in template_scores[:3]])
        else:
            # Otherwise, weighted random selection based on scores
            total_score = sum(score for _, score in template_scores)
            if total_score <= 0:
                return random.choice(templates)
            
            r = random.uniform(0, total_score)
            cumulative = 0
            for template, score in template_scores:
                cumulative += score
                if r <= cumulative:
                    return template
            
            # Fallback
            return template_scores[0][0] if template_scores else None
    
    def _create_error_content(self, content_type: ContentType, error_message: str,
                            player_id: Optional[str] = None) -> GeneratedContent:
        """
        Create error content when generation fails.
        
        Args:
            content_type: Type of content that failed to generate
            error_message: Error message
            player_id: Player ID (optional)
            
        Returns:
            Error content
        """
        return GeneratedContent(
            id=str(uuid.uuid4()),
            content_type=content_type,
            name="Error Content",
            description=f"Error generating {content_type.value} content",
            content_data={"error": error_message},
            template_id="error",
            generation_params={"error": error_message},
            player_id=player_id,
            timestamp=time.time(),
            version=1,
            tags=["error"],
            metadata={"error": True, "error_message": error_message}
        )
    
    def _generate_template_based(self, template: ContentTemplate,
                               player_profile: Optional[PlayerPreferenceProfile] = None,
                               params: Dict[str, Any] = None) -> GeneratedContent:
        """
        Generate content using template-based approach.
        
        Args:
            template: Template to use
            player_profile: Player preference profile (optional)
            params: Additional generation parameters
            
        Returns:
            Generated content
        """
        if params is None:
            params = {}
        
        # Get template data
        template_data = template.template_data
        structure = template_data.get("structure", {})
        variables = template_data.get("variables", {})
        content_blocks = template_data.get("content_blocks", {})
        
        # Apply player preferences if available
        if player_profile is not None:
            variables = self._apply_player_preferences(variables, player_profile, template, params)
        
        # Apply additional parameters
        variables.update(params.get("variables", {}))
        
        # Generate content data
        content_data = self._process_structure(structure, variables, content_blocks)
        
        # Generate name and description
        name = content_data.get("name", template.name)
        description = content_data.get("description", template.description)
        
        # Create content object
        content = GeneratedContent(
            id=str(uuid.uuid4()),
            content_type=template.content_type,
            name=name,
            description=description,
            content_data=content_data,
            template_id=template.id,
            generation_params=params,
            player_id=player_profile.player_id if player_profile else None,
            timestamp=time.time(),
            version=1,
            tags=template.tags.copy(),
            metadata={
                "complexity": template.complexity.value,
                "themes": [theme.value for theme in template.themes],
                "tones": [tone.value for tone in template.tones],
                "factions": [faction.value for faction in template.factions]
            }
        )
        
        return content
    
    def _apply_player_preferences(self, variables: Dict[str, Any],
                                player_profile: PlayerPreferenceProfile,
                                template: ContentTemplate,
                                params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply player preferences to template variables.
        
        Args:
            variables: Template variables
            player_profile: Player preference profile
            template: Content template
            params: Additional generation parameters
            
        Returns:
            Updated variables
        """
        # Create a copy to avoid modifying the original
        variables = copy.deepcopy(variables)
        
        # Apply theme preferences
        if "themes" in variables and isinstance(variables["themes"], list):
            # Get player's preferred themes
            preferred_themes = sorted(
                player_profile.preferred_themes.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Replace themes with player's preferred ones
            if preferred_themes:
                top_themes = [theme for theme, _ in preferred_themes[:2]]
                if top_themes:
                    variables["themes"] = [theme.value for theme in top_themes]
        
        # Apply tone preferences
        if "tones" in variables and isinstance(variables["tones"], list):
            # Get player's preferred tones
            preferred_tones = sorted(
                player_profile.preferred_tones.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Replace tones with player's preferred ones
            if preferred_tones:
                top_tones = [tone for tone, _ in preferred_tones[:2]]
                if top_tones:
                    variables["tones"] = [tone.value for tone in top_tones]
        
        # Apply faction preferences
        if "faction" in variables:
            # Get player's preferred faction
            preferred_factions = sorted(
                player_profile.preferred_factions.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Replace faction with player's preferred one
            if preferred_factions:
                top_faction = preferred_factions[0][0]
                variables["faction"] = top_faction.value
        
        # Apply complexity preference
        preferred_complexity = player_profile.get_complexity_preference(template.content_type)
        variables["complexity"] = preferred_complexity.value
        
        # Apply custom preferences
        for key, value in player_profile.custom_preferences.items():
            if key in variables:
                variables[key] = value
        
        return variables
    
    def _process_structure(self, structure: Dict[str, Any], variables: Dict[str, Any],
                         content_blocks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process template structure to generate content.
        
        Args:
            structure: Template structure
            variables: Template variables
            content_blocks: Content blocks
            
        Returns:
            Generated content data
        """
        # Create a copy to avoid modifying the original
        result = {}
        
        # Process each field in the structure
        for key, value in structure.items():
            if isinstance(value, dict):
                # Recursively process nested dictionaries
                result[key] = self._process_structure(value, variables, content_blocks)
            elif isinstance(value, list):
                # Process lists
                result[key] = self._process_list(value, variables, content_blocks)
            elif isinstance(value, str):
                # Process string values
                if value.startswith("$var:"):
                    # Variable reference
                    var_name = value[5:]
                    result[key] = variables.get(var_name, value)
                elif value.startswith("$block:"):
                    # Content block reference
                    block_name = value[7:]
                    result[key] = self._process_content_block(block_name, variables, content_blocks)
                elif value.startswith("$random:"):
                    # Random selection
                    options_str = value[8:]
                    options = [opt.strip() for opt in options_str.split(",")]
                    result[key] = random.choice(options)
                elif value.startswith("$range:"):
                    # Random number in range
                    range_str = value[7:]
                    range_parts = range_str.split(",")
                    if len(range_parts) >= 2:
                        min_val = int(range_parts[0])
                        max_val = int(range_parts[1])
                        result[key] = random.randint(min_val, max_val)
                    else:
                        result[key] = value
                else:
                    # Regular string
                    result[key] = value
            else:
                # Other values (numbers, booleans, etc.)
                result[key] = value
        
        return result
    
    def _process_list(self, items: List[Any], variables: Dict[str, Any],
                    content_blocks: Dict[str, Any]) -> List[Any]:
        """
        Process a list in the template structure.
        
        Args:
            items: List items
            variables: Template variables
            content_blocks: Content blocks
            
        Returns:
            Processed list
        """
        result = []
        
        # Check for list generation directives
        if len(items) == 1 and isinstance(items[0], str) and items[0].startswith("$generate:"):
            # List generation directive
            directive = items[0][10:]
            directive_parts = directive.split(":")
            
            if len(directive_parts) >= 2:
                count_str = directive_parts[0]
                block_name = directive_parts[1]
                
                # Determine count
                if count_str.startswith("$var:"):
                    var_name = count_str[5:]
                    count = variables.get(var_name, 1)
                elif count_str.startswith("$range:"):
                    range_str = count_str[7:]
                    range_parts = range_str.split(",")
                    if len(range_parts) >= 2:
                        min_val = int(range_parts[0])
                        max_val = int(range_parts[1])
                        count = random.randint(min_val, max_val)
                    else:
                        count = 1
                else:
                    try:
                        count = int(count_str)
                    except ValueError:
                        count = 1
                
                # Generate items
                for i in range(count):
                    item_vars = copy.deepcopy(variables)
                    item_vars["index"] = i
                    item = self._process_content_block(block_name, item_vars, content_blocks)
                    result.append(item)
            
            return result
        
        # Process each item normally
        for item in items:
            if isinstance(item, dict):
                # Process dictionary
                result.append(self._process_structure(item, variables, content_blocks))
            elif isinstance(item, list):
                # Process nested list
                result.append(self._process_list(item, variables, content_blocks))
            elif isinstance(item, str):
                # Process string
                if item.startswith("$var:"):
                    # Variable reference
                    var_name = item[5:]
                    result.append(variables.get(var_name, item))
                elif item.startswith("$block:"):
                    # Content block reference
                    block_name = item[7:]
                    result.append(self._process_content_block(block_name, variables, content_blocks))
                elif item.startswith("$random:"):
                    # Random selection
                    options_str = item[8:]
                    options = [opt.strip() for opt in options_str.split(",")]
                    result.append(random.choice(options))
                elif item.startswith("$range:"):
                    # Random number in range
                    range_str = item[7:]
                    range_parts = range_str.split(",")
                    if len(range_parts) >= 2:
                        min_val = int(range_parts[0])
                        max_val = int(range_parts[1])
                        result.append(random.randint(min_val, max_val))
                    else:
                        result.append(item)
                else:
                    # Regular string
                    result.append(item)
            else:
                # Other values
                result.append(item)
        
        return result
    
    def _process_content_block(self, block_name: str, variables: Dict[str, Any],
                             content_blocks: Dict[str, Any]) -> Any:
        """
        Process a content block.
        
        Args:
            block_name: Name of the content block
            variables: Template variables
            content_blocks: Content blocks
            
        Returns:
            Processed content block
        """
        if block_name not in content_blocks:
            return f"[Missing block: {block_name}]"
        
        block = content_blocks[block_name]
        
        if isinstance(block, dict):
            # Process dictionary block
            return self._process_structure(block, variables, content_blocks)
        elif isinstance(block, list):
            # Process list block
            return self._process_list(block, variables, content_blocks)
        elif isinstance(block, str):
            # Process string block
            if block.startswith("$var:"):
                # Variable reference
                var_name = block[5:]
                return variables.get(var_name, block)
            elif block.startswith("$random:"):
                # Random selection
                options_str = block[8:]
                options = [opt.strip() for opt in options_str.split(",")]
                return random.choice(options)
            elif block.startswith("$range:"):
                # Random number in range
                range_str = block[7:]
                range_parts = range_str.split(",")
                if len(range_parts) >= 2:
                    min_val = int(range_parts[0])
                    max_val = int(range_parts[1])
                    return random.randint(min_val, max_val)
                else:
                    return block
            else:
                # Regular string
                return block
        else:
            # Other values
            return block
    
    def _generate_grammar_based(self, template: ContentTemplate,
                              player_profile: Optional[PlayerPreferenceProfile] = None,
                              params: Dict[str, Any] = None) -> GeneratedContent:
        """
        Generate content using grammar-based approach.
        
        Args:
            template: Template to use
            player_profile: Player preference profile (optional)
            params: Additional generation parameters
            
        Returns:
            Generated content
        """
        # For now, fall back to template-based generation
        return self._generate_template_based(template, player_profile, params)
    
    def _generate_evolutionary(self, template: ContentTemplate,
                             player_profile: Optional[PlayerPreferenceProfile] = None,
                             params: Dict[str, Any] = None) -> GeneratedContent:
        """
        Generate content using evolutionary approach.
        
        Args:
            template: Template to use
            player_profile: Player preference profile (optional)
            params: Additional generation parameters
            
        Returns:
            Generated content
        """
        # For now, fall back to template-based generation
        return self._generate_template_based(template, player_profile, params)
    
    def _generate_constraint_based(self, template: ContentTemplate,
                                 player_profile: Optional[PlayerPreferenceProfile] = None,
                                 params: Dict[str, Any] = None) -> GeneratedContent:
        """
        Generate content using constraint-based approach.
        
        Args:
            template: Template to use
            player_profile: Player preference profile (optional)
            params: Additional generation parameters
            
        Returns:
            Generated content
        """
        # For now, fall back to template-based generation
        return self._generate_template_based(template, player_profile, params)
    
    def _generate_neural(self, template: ContentTemplate,
                       player_profile: Optional[PlayerPreferenceProfile] = None,
                       params: Dict[str, Any] = None) -> GeneratedContent:
        """
        Generate content using neural approach.
        
        Args:
            template: Template to use
            player_profile: Player preference profile (optional)
            params: Additional generation parameters
            
        Returns:
            Generated content
        """
        # For now, fall back to template-based generation
        return self._generate_template_based(template, player_profile, params)
    
    def _generate_hybrid(self, template: ContentTemplate,
                       player_profile: Optional[PlayerPreferenceProfile] = None,
                       params: Dict[str, Any] = None) -> GeneratedContent:
        """
        Generate content using hybrid approach.
        
        Args:
            template: Template to use
            player_profile: Player preference profile (optional)
            params: Additional generation parameters
            
        Returns:
            Generated content
        """
        # For now, fall back to template-based generation
        return self._generate_template_based(template, player_profile, params)
