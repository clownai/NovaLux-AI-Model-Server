"""
Game Parameter Configurator for Adaptive Difficulty System

This module provides tools for configuring game parameters based on difficulty levels,
allowing for fine-grained control over how difficulty affects gameplay across different
game types in the NovaLux ecosystem.

The configurator handles:
- Parameter mapping between difficulty levels and game settings
- Game-specific parameter adjustments
- Parameter interpolation for smooth difficulty transitions
- Parameter validation and constraints
"""

from typing import Dict, List, Tuple, Any, Optional, Union
import json
import math
from enum import Enum
from dataclasses import dataclass, field

from core.adaptive_difficulty import (
    DifficultyLevel, GameType, GameDifficultyParameters
)


class ParameterType(Enum):
    """Types of game parameters with different scaling behaviors."""
    LINEAR = "linear"  # Linear scaling between min and max
    EXPONENTIAL = "exponential"  # Exponential scaling (steeper at higher difficulties)
    LOGARITHMIC = "logarithmic"  # Logarithmic scaling (steeper at lower difficulties)
    INVERSE = "inverse"  # Inverse scaling (higher difficulty = lower value)
    STEPPED = "stepped"  # Discrete steps rather than continuous
    BOOLEAN = "boolean"  # On/off at specific threshold


@dataclass
class ParameterConfig:
    """Configuration for a single game parameter."""
    name: str
    parameter_type: ParameterType
    min_value: float
    max_value: float
    default_value: float
    description: str = ""
    unit: str = ""
    step_size: Optional[float] = None
    threshold: Optional[float] = None  # For boolean parameters
    invert_difficulty: bool = False  # If True, higher difficulty = lower value
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    
    def validate_value(self, value: float) -> bool:
        """
        Validate that a parameter value meets all constraints.
        
        Args:
            value: Parameter value to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check min/max bounds
        if value < self.min_value or value > self.max_value:
            return False
        
        # Check step size for stepped parameters
        if self.parameter_type == ParameterType.STEPPED and self.step_size:
            # Check if value is a multiple of step size from min_value
            steps = round((value - self.min_value) / self.step_size)
            expected_value = self.min_value + (steps * self.step_size)
            if abs(value - expected_value) > 1e-6:  # Allow for floating point imprecision
                return False
        
        # Check additional constraints
        for constraint in self.constraints:
            constraint_type = constraint.get('type')
            
            if constraint_type == 'range' and 'min' in constraint and 'max' in constraint:
                if value < constraint['min'] or value > constraint['max']:
                    return False
            
            elif constraint_type == 'enum' and 'values' in constraint:
                if value not in constraint['values']:
                    return False
            
            elif constraint_type == 'dependency' and 'parameter' in constraint and 'condition' in constraint:
                # Dependencies are checked separately with access to all parameters
                pass
        
        return True
    
    def calculate_value_for_difficulty(self, difficulty_level: Union[DifficultyLevel, float]) -> float:
        """
        Calculate parameter value for a specific difficulty level.
        
        Args:
            difficulty_level: Difficulty level (enum or float 0-6)
            
        Returns:
            Calculated parameter value
        """
        # Convert enum to float if needed
        if isinstance(difficulty_level, DifficultyLevel):
            difficulty = float(difficulty_level.value)
        else:
            difficulty = float(difficulty_level)
        
        # Clamp difficulty to valid range
        difficulty = max(0.0, min(6.0, difficulty))
        
        # Normalize difficulty to 0-1 range
        normalized_difficulty = difficulty / 6.0
        
        # Invert if needed
        if self.invert_difficulty:
            normalized_difficulty = 1.0 - normalized_difficulty
        
        # Calculate value based on parameter type
        if self.parameter_type == ParameterType.LINEAR:
            # Linear interpolation
            value = self.min_value + normalized_difficulty * (self.max_value - self.min_value)
        
        elif self.parameter_type == ParameterType.EXPONENTIAL:
            # Exponential scaling (steeper at higher difficulties)
            # y = a + (b-a) * x^2
            value = self.min_value + (self.max_value - self.min_value) * (normalized_difficulty ** 2)
        
        elif self.parameter_type == ParameterType.LOGARITHMIC:
            # Logarithmic scaling (steeper at lower difficulties)
            # Avoid log(0) by using small epsilon
            epsilon = 1e-6
            # y = a + (b-a) * log(1 + 9x) / log(10)
            value = self.min_value + (self.max_value - self.min_value) * (
                math.log(1 + 9 * normalized_difficulty + epsilon) / math.log(10)
            )
        
        elif self.parameter_type == ParameterType.INVERSE:
            # Inverse scaling
            # y = a + (b-a) * (1 - x)
            value = self.min_value + (self.max_value - self.min_value) * (1.0 - normalized_difficulty)
        
        elif self.parameter_type == ParameterType.STEPPED:
            # Stepped scaling
            if self.step_size:
                # Calculate number of steps
                total_steps = math.floor((self.max_value - self.min_value) / self.step_size)
                current_step = round(normalized_difficulty * total_steps)
                value = self.min_value + current_step * self.step_size
            else:
                # Fallback to linear if step size not specified
                value = self.min_value + normalized_difficulty * (self.max_value - self.min_value)
        
        elif self.parameter_type == ParameterType.BOOLEAN:
            # Boolean (threshold-based)
            if self.threshold is not None:
                value = self.max_value if normalized_difficulty >= self.threshold else self.min_value
            else:
                # Default threshold of 0.5
                value = self.max_value if normalized_difficulty >= 0.5 else self.min_value
        
        else:
            # Default to linear
            value = self.min_value + normalized_difficulty * (self.max_value - self.min_value)
        
        # Clamp to min/max
        value = max(self.min_value, min(self.max_value, value))
        
        # Round to step size if stepped
        if self.parameter_type == ParameterType.STEPPED and self.step_size:
            steps = round((value - self.min_value) / self.step_size)
            value = self.min_value + (steps * self.step_size)
        
        return value


class GameParameterConfigurator:
    """
    Configures and manages game parameters based on difficulty levels.
    
    This class provides tools for defining parameter configurations,
    calculating parameter values for different difficulty levels,
    and validating parameter combinations.
    """
    
    def __init__(self):
        """Initialize the game parameter configurator."""
        # Parameter configurations by game type
        self.parameter_configs: Dict[GameType, Dict[str, ParameterConfig]] = {}
        
        # Parameter dependencies
        self.parameter_dependencies: Dict[GameType, List[Dict[str, Any]]] = {}
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self) -> None:
        """Initialize default parameter configurations for all game types."""
        # Eclipse Roulette parameters
        self._init_eclipse_roulette_params()
        
        # Neural Hold'em parameters
        self._init_neural_holdem_params()
        
        # Chaos Slots parameters
        self._init_chaos_slots_params()
        
        # Generic parameters for other games
        self._init_generic_game_params()
    
    def _init_eclipse_roulette_params(self) -> None:
        """Initialize parameter configurations for Eclipse Roulette."""
        game_type = GameType.ECLIPSE_ROULETTE
        self.parameter_configs[game_type] = {}
        
        # House edge parameter
        self.parameter_configs[game_type]['house_edge'] = ParameterConfig(
            name="house_edge",
            parameter_type=ParameterType.LINEAR,
            min_value=0.02,
            max_value=0.1,
            default_value=0.05,
            description="House edge percentage affecting overall return to player",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = higher house edge
        )
        
        # Volatility parameter
        self.parameter_configs[game_type]['volatility'] = ParameterConfig(
            name="volatility",
            parameter_type=ParameterType.EXPONENTIAL,
            min_value=0.3,
            max_value=0.9,
            default_value=0.5,
            description="Volatility of outcomes affecting variance in results",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = higher volatility
        )
        
        # Special feature frequency parameter
        self.parameter_configs[game_type]['special_feature_frequency'] = ParameterConfig(
            name="special_feature_frequency",
            parameter_type=ParameterType.INVERSE,
            min_value=0.02,
            max_value=0.2,
            default_value=0.1,
            description="Frequency of special features and bonuses",
            unit="ratio",
            invert_difficulty=True  # Higher difficulty = lower frequency
        )
        
        # Bonus multiplier parameter
        self.parameter_configs[game_type]['bonus_multiplier'] = ParameterConfig(
            name="bonus_multiplier",
            parameter_type=ParameterType.INVERSE,
            min_value=1.0,
            max_value=2.0,
            default_value=1.5,
            description="Multiplier applied to bonus wins",
            unit="multiplier",
            invert_difficulty=True  # Higher difficulty = lower multiplier
        )
        
        # Time pressure parameter
        self.parameter_configs[game_type]['time_pressure'] = ParameterConfig(
            name="time_pressure",
            parameter_type=ParameterType.LINEAR,
            min_value=0.1,
            max_value=0.9,
            default_value=0.3,
            description="Time pressure for making decisions",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = higher time pressure
        )
        
        # Complexity parameter
        self.parameter_configs[game_type]['complexity'] = ParameterConfig(
            name="complexity",
            parameter_type=ParameterType.LINEAR,
            min_value=0.2,
            max_value=0.9,
            default_value=0.4,
            description="Complexity of game rules and mechanics",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = higher complexity
        )
        
        # Define dependencies
        self.parameter_dependencies[game_type] = [
            {
                'type': 'inverse_correlation',
                'parameters': ['house_edge', 'special_feature_frequency'],
                'strength': 0.7,
                'description': 'Higher house edge should correlate with lower special feature frequency'
            },
            {
                'type': 'inverse_correlation',
                'parameters': ['volatility', 'bonus_multiplier'],
                'strength': 0.6,
                'description': 'Higher volatility should correlate with lower bonus multipliers'
            }
        ]
    
    def _init_neural_holdem_params(self) -> None:
        """Initialize parameter configurations for Neural Hold'em."""
        game_type = GameType.NEURAL_HOLDEM
        self.parameter_configs[game_type] = {}
        
        # AI skill level parameter
        self.parameter_configs[game_type]['ai_skill_level'] = ParameterConfig(
            name="ai_skill_level",
            parameter_type=ParameterType.EXPONENTIAL,
            min_value=0.1,
            max_value=0.95,
            default_value=0.5,
            description="Skill level of AI opponents",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = higher AI skill
        )
        
        # Hand quality distribution parameter
        self.parameter_configs[game_type]['hand_quality_distribution'] = ParameterConfig(
            name="hand_quality_distribution",
            parameter_type=ParameterType.INVERSE,
            min_value=0.3,
            max_value=0.7,
            default_value=0.5,
            description="Distribution of hand quality (higher = better hands for player)",
            unit="ratio",
            invert_difficulty=True  # Higher difficulty = worse hands for player
        )
        
        # Bluff frequency parameter
        self.parameter_configs[game_type]['bluff_frequency'] = ParameterConfig(
            name="bluff_frequency",
            parameter_type=ParameterType.LINEAR,
            min_value=0.1,
            max_value=0.7,
            default_value=0.3,
            description="Frequency of AI opponent bluffing",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = more bluffing
        )
        
        # Tell visibility parameter
        self.parameter_configs[game_type]['tell_visibility'] = ParameterConfig(
            name="tell_visibility",
            parameter_type=ParameterType.INVERSE,
            min_value=0.05,
            max_value=0.8,
            default_value=0.4,
            description="Visibility of opponent tells and cues",
            unit="ratio",
            invert_difficulty=True  # Higher difficulty = less visible tells
        )
        
        # Time per decision parameter
        self.parameter_configs[game_type]['time_per_decision'] = ParameterConfig(
            name="time_per_decision",
            parameter_type=ParameterType.INVERSE,
            min_value=8,
            max_value=30,
            default_value=20,
            description="Time allowed for each decision",
            unit="seconds",
            invert_difficulty=True  # Higher difficulty = less time
        )
        
        # Starting chips ratio parameter
        self.parameter_configs[game_type]['starting_chips_ratio'] = ParameterConfig(
            name="starting_chips_ratio",
            parameter_type=ParameterType.INVERSE,
            min_value=0.6,
            max_value=1.5,
            default_value=1.0,
            description="Ratio of player's starting chips to standard amount",
            unit="ratio",
            invert_difficulty=True  # Higher difficulty = fewer starting chips
        )
        
        # Define dependencies
        self.parameter_dependencies[game_type] = [
            {
                'type': 'correlation',
                'parameters': ['ai_skill_level', 'bluff_frequency'],
                'strength': 0.5,
                'description': 'Higher AI skill correlates with more sophisticated bluffing'
            },
            {
                'type': 'inverse_correlation',
                'parameters': ['ai_skill_level', 'tell_visibility'],
                'strength': 0.8,
                'description': 'Higher AI skill correlates with fewer visible tells'
            }
        ]
    
    def _init_chaos_slots_params(self) -> None:
        """Initialize parameter configurations for Chaos Slots."""
        game_type = GameType.CHAOS_SLOTS
        self.parameter_configs[game_type] = {}
        
        # Return to player parameter
        self.parameter_configs[game_type]['rtp'] = ParameterConfig(
            name="rtp",
            parameter_type=ParameterType.INVERSE,
            min_value=0.88,
            max_value=0.98,
            default_value=0.95,
            description="Return to player percentage",
            unit="ratio",
            invert_difficulty=True  # Higher difficulty = lower RTP
        )
        
        # Hit frequency parameter
        self.parameter_configs[game_type]['hit_frequency'] = ParameterConfig(
            name="hit_frequency",
            parameter_type=ParameterType.INVERSE,
            min_value=0.1,
            max_value=0.4,
            default_value=0.3,
            description="Frequency of winning spins",
            unit="ratio",
            invert_difficulty=True  # Higher difficulty = lower hit frequency
        )
        
        # Volatility parameter
        self.parameter_configs[game_type]['volatility'] = ParameterConfig(
            name="volatility",
            parameter_type=ParameterType.LINEAR,
            min_value=0.3,
            max_value=1.0,
            default_value=0.6,
            description="Volatility of outcomes",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = higher volatility
        )
        
        # Feature trigger chance parameter
        self.parameter_configs[game_type]['feature_trigger_chance'] = ParameterConfig(
            name="feature_trigger_chance",
            parameter_type=ParameterType.INVERSE,
            min_value=0.01,
            max_value=0.1,
            default_value=0.05,
            description="Chance to trigger bonus features",
            unit="ratio",
            invert_difficulty=True  # Higher difficulty = lower chance
        )
        
        # Bonus game difficulty parameter
        self.parameter_configs[game_type]['bonus_game_difficulty'] = ParameterConfig(
            name="bonus_game_difficulty",
            parameter_type=ParameterType.LINEAR,
            min_value=0.2,
            max_value=0.9,
            default_value=0.5,
            description="Difficulty level of bonus games",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = harder bonus games
        )
        
        # Symbol complexity parameter
        self.parameter_configs[game_type]['symbol_complexity'] = ParameterConfig(
            name="symbol_complexity",
            parameter_type=ParameterType.LINEAR,
            min_value=0.2,
            max_value=0.9,
            default_value=0.5,
            description="Complexity of symbol combinations and paytable",
            unit="ratio",
            invert_difficulty=False  # Higher difficulty = more complex symbols
        )
        
        # Define dependencies
        self.parameter_dependencies[game_type] = [
            {
                'type': 'inverse_correlation',
                'parameters': ['rtp', 'volatility'],
                'strength': 0.7,
                'description': 'Higher RTP should correlate with lower volatility'
            },
            {
                'type': 'correlation',
                'parameters': ['volatility', 'feature_trigger_chance'],
                'strength': 0.5,
                'description': 'Higher volatility should have some correlation with feature triggers'
            }
        ]
    
    def _init_generic_game_params(self) -> None:
        """Initialize generic parameter configurations for other game types."""
        for game_type in GameType:
            # Skip games we've already configured
            if game_type in [GameType.ECLIPSE_ROULETTE, GameType.NEURAL_HOLDEM, GameType.CHAOS_SLOTS]:
                continue
            
            self.parameter_configs[game_type] = {}
            
            # Difficulty scalar parameter
            self.parameter_configs[game_type]['difficulty_scalar'] = ParameterConfig(
                name="difficulty_scalar",
                parameter_type=ParameterType.LINEAR,
                min_value=0.1,
                max_value=1.0,
                default_value=0.5,
                description="Overall difficulty scaling factor",
                unit="ratio",
                invert_difficulty=False  # Higher difficulty = higher scalar
            )
            
            # Reward frequency parameter
            self.parameter_configs[game_type]['reward_frequency'] = ParameterConfig(
                name="reward_frequency",
                parameter_type=ParameterType.INVERSE,
                min_value=0.1,
                max_value=0.8,
                default_value=0.5,
                description="Frequency of rewards and wins",
                unit="ratio",
                invert_difficulty=True  # Higher difficulty = lower frequency
            )
            
            # Complexity parameter
            self.parameter_configs[game_type]['complexity'] = ParameterConfig(
                name="complexity",
                parameter_type=ParameterType.LINEAR,
                min_value=0.2,
                max_value=0.9,
                default_value=0.5,
                description="Complexity of game rules and mechanics",
                unit="ratio",
                invert_difficulty=False  # Higher difficulty = higher complexity
            )
            
            # Time pressure parameter
            self.parameter_configs[game_type]['time_pressure'] = ParameterConfig(
                name="time_pressure",
                parameter_type=ParameterType.LINEAR,
                min_value=0.1,
                max_value=0.9,
                default_value=0.5,
                description="Time pressure for making decisions",
                unit="ratio",
                invert_difficulty=False  # Higher difficulty = higher time pressure
            )
            
            # Punishment severity parameter
            self.parameter_configs[game_type]['punishment_severity'] = ParameterConfig(
                name="punishment_severity",
                parameter_type=ParameterType.LINEAR,
                min_value=0.1,
                max_value=0.9,
                default_value=0.5,
                description="Severity of punishments for mistakes",
                unit="ratio",
                invert_difficulty=False  # Higher difficulty = higher severity
            )
            
            # Randomness parameter
            self.parameter_configs[game_type]['randomness'] = ParameterConfig(
                name="randomness",
                parameter_type=ParameterType.LINEAR,
                min_value=0.3,
                max_value=0.8,
                default_value=0.5,
                description="Randomness in game outcomes",
                unit="ratio",
                invert_difficulty=False  # Higher difficulty = higher randomness
            )
            
            # Define dependencies
            self.parameter_dependencies[game_type] = [
                {
                    'type': 'correlation',
                    'parameters': ['difficulty_scalar', 'punishment_severity'],
                    'strength': 0.8,
                    'description': 'Higher difficulty correlates with higher punishment severity'
                },
                {
                    'type': 'inverse_correlation',
                    'parameters': ['difficulty_scalar', 'reward_frequency'],
                    'strength': 0.7,
                    'description': 'Higher difficulty correlates with lower reward frequency'
                }
            ]
    
    def get_parameter_config(self, game_type: GameType, parameter_name: str) -> Optional[ParameterConfig]:
        """
        Get configuration for a specific parameter.
        
        Args:
            game_type: Type of game
            parameter_name: Name of the parameter
            
        Returns:
            Parameter configuration or None if not found
        """
        if game_type in self.parameter_configs and parameter_name in self.parameter_configs[game_type]:
            return self.parameter_configs[game_type][parameter_name]
        return None
    
    def get_all_parameter_configs(self, game_type: GameType) -> Dict[str, ParameterConfig]:
        """
        Get all parameter configurations for a game type.
        
        Args:
            game_type: Type of game
            
        Returns:
            Dictionary of parameter configurations
        """
        return self.parameter_configs.get(game_type, {})
    
    def calculate_parameters_for_difficulty(self, game_type: GameType, 
                                          difficulty_level: Union[DifficultyLevel, float]) -> Dict[str, float]:
        """
        Calculate all parameters for a specific difficulty level.
        
        Args:
            game_type: Type of game
            difficulty_level: Difficulty level (enum or float 0-6)
            
        Returns:
            Dictionary of parameter values
        """
        parameters = {}
        
        # Get all parameter configs for this game type
        configs = self.get_all_parameter_configs(game_type)
        
        # Calculate each parameter value
        for param_name, config in configs.items():
            parameters[param_name] = config.calculate_value_for_difficulty(difficulty_level)
        
        # Apply parameter dependencies
        self._apply_parameter_dependencies(game_type, parameters)
        
        return parameters
    
    def _apply_parameter_dependencies(self, game_type: GameType, parameters: Dict[str, float]) -> None:
        """
        Apply parameter dependencies to ensure consistent parameter combinations.
        
        Args:
            game_type: Type of game
            parameters: Dictionary of parameter values to adjust
        """
        if game_type not in self.parameter_dependencies:
            return
        
        # Apply each dependency
        for dependency in self.parameter_dependencies[game_type]:
            dep_type = dependency.get('type')
            dep_params = dependency.get('parameters', [])
            strength = dependency.get('strength', 0.5)
            
            # Skip if missing parameters
            if len(dep_params) < 2 or not all(p in parameters for p in dep_params):
                continue
            
            if dep_type == 'correlation' or dep_type == 'inverse_correlation':
                # Get parameter configs
                configs = [self.get_parameter_config(game_type, p) for p in dep_params]
                if not all(configs):
                    continue
                
                # Get normalized values (0-1 scale)
                normalized_values = []
                for i, param in enumerate(dep_params):
                    config = configs[i]
                    value = parameters[param]
                    norm_value = (value - config.min_value) / (config.max_value - config.min_value)
                    normalized_values.append(norm_value)
                
                # Calculate target value based on correlation
                source_value = normalized_values[0]
                target_value = normalized_values[1]
                
                if dep_type == 'correlation':
                    # Positive correlation: values should be similar
                    target_norm = source_value
                else:
                    # Inverse correlation: values should be opposite
                    target_norm = 1.0 - source_value
                
                # Blend current and target values based on strength
                new_norm = target_value * (1 - strength) + target_norm * strength
                
                # Convert back to parameter scale
                config = configs[1]
                new_value = config.min_value + new_norm * (config.max_value - config.min_value)
                
                # Update parameter
                parameters[dep_params[1]] = new_value
    
    def validate_parameters(self, game_type: GameType, parameters: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate a set of parameters against their configurations.
        
        Args:
            game_type: Type of game
            parameters: Dictionary of parameter values
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        is_valid = True
        errors = []
        
        # Get all parameter configs for this game type
        configs = self.get_all_parameter_configs(game_type)
        
        # Validate each parameter
        for param_name, value in parameters.items():
            if param_name not in configs:
                errors.append(f"Unknown parameter: {param_name}")
                is_valid = False
                continue
            
            config = configs[param_name]
            if not config.validate_value(value):
                errors.append(f"Invalid value for {param_name}: {value}")
                is_valid = False
        
        # Check for missing required parameters
        for param_name, config in configs.items():
            if param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
                is_valid = False
        
        return is_valid, errors
    
    def create_difficulty_mapping(self, game_type: GameType) -> Dict[DifficultyLevel, Dict[str, float]]:
        """
        Create a complete difficulty mapping for a game type.
        
        Args:
            game_type: Type of game
            
        Returns:
            Dictionary mapping difficulty levels to parameter sets
        """
        mapping = {}
        
        # Calculate parameters for each standard difficulty level
        for level in DifficultyLevel:
            mapping[level] = self.calculate_parameters_for_difficulty(game_type, level)
        
        return mapping
    
    def create_game_parameters(self, game_type: GameType) -> GameDifficultyParameters:
        """
        Create a GameDifficultyParameters object with complete mappings.
        
        Args:
            game_type: Type of game
            
        Returns:
            GameDifficultyParameters object
        """
        # Get default parameters (medium difficulty)
        default_params = self.calculate_parameters_for_difficulty(game_type, DifficultyLevel.MEDIUM)
        
        # Create difficulty mapping
        difficulty_mapping = self.create_difficulty_mapping(game_type)
        
        # Create and return parameters object
        return GameDifficultyParameters(
            game_type=game_type,
            parameters=default_params,
            difficulty_mapping=difficulty_mapping
        )
    
    def save_configurations(self, filepath: str) -> bool:
        """
        Save parameter configurations to a file.
        
        Args:
            filepath: Path to save configurations
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to serializable format
            data = {
                'parameter_configs': {},
                'parameter_dependencies': {}
            }
            
            # Serialize parameter configs
            for game_type, configs in self.parameter_configs.items():
                data['parameter_configs'][game_type.value] = {}
                
                for param_name, config in configs.items():
                    data['parameter_configs'][game_type.value][param_name] = {
                        'name': config.name,
                        'parameter_type': config.parameter_type.value,
                        'min_value': config.min_value,
                        'max_value': config.max_value,
                        'default_value': config.default_value,
                        'description': config.description,
                        'unit': config.unit,
                        'step_size': config.step_size,
                        'threshold': config.threshold,
                        'invert_difficulty': config.invert_difficulty,
                        'constraints': config.constraints
                    }
            
            # Serialize parameter dependencies
            for game_type, dependencies in self.parameter_dependencies.items():
                data['parameter_dependencies'][game_type.value] = dependencies
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving parameter configurations: {e}")
            return False
    
    def load_configurations(self, filepath: str) -> bool:
        """
        Load parameter configurations from a file.
        
        Args:
            filepath: Path to load configurations from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Clear existing configurations
            self.parameter_configs = {}
            self.parameter_dependencies = {}
            
            # Load parameter configs
            for game_type_str, configs in data.get('parameter_configs', {}).items():
                game_type = GameType(game_type_str)
                self.parameter_configs[game_type] = {}
                
                for param_name, config_data in configs.items():
                    self.parameter_configs[game_type][param_name] = ParameterConfig(
                        name=config_data['name'],
                        parameter_type=ParameterType(config_data['parameter_type']),
                        min_value=config_data['min_value'],
                        max_value=config_data['max_value'],
                        default_value=config_data['default_value'],
                        description=config_data.get('description', ''),
                        unit=config_data.get('unit', ''),
                        step_size=config_data.get('step_size'),
                        threshold=config_data.get('threshold'),
                        invert_difficulty=config_data.get('invert_difficulty', False),
                        constraints=config_data.get('constraints', [])
                    )
            
            # Load parameter dependencies
            for game_type_str, dependencies in data.get('parameter_dependencies', {}).items():
                game_type = GameType(game_type_str)
                self.parameter_dependencies[game_type] = dependencies
            
            return True
        
        except Exception as e:
            print(f"Error loading parameter configurations: {e}")
            return False
