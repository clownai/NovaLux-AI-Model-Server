"""
Adaptive Difficulty System - Core Module

This module provides the core functionality for the NovaLux adaptive difficulty system,
which dynamically adjusts game challenge levels based on player performance.

The system uses a combination of real-time performance metrics, historical data analysis,
and player preference modeling to create personalized difficulty curves that maintain
an optimal level of challenge and engagement.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
import uuid
import time
import json
import random
import math
import numpy as np
from enum import Enum
from dataclasses import dataclass, field


class DifficultyLevel(Enum):
    """Enumeration of standard difficulty levels."""
    VERY_EASY = 0
    EASY = 1
    MEDIUM = 2
    CHALLENGING = 3
    HARD = 4
    VERY_HARD = 5
    EXTREME = 6


class GameType(Enum):
    """Types of games in the NovaLux ecosystem."""
    ECLIPSE_ROULETTE = "eclipse_roulette"
    NEURAL_HOLDEM = "neural_holdem"
    CHAOS_SLOTS = "chaos_slots"
    QUANTUM_BLACKJACK = "quantum_blackjack"
    CYBERNETIC_CRAPS = "cybernetic_craps"
    NEXUS_BACCARAT = "nexus_baccarat"


class PerformanceMetric(Enum):
    """Key performance metrics tracked for adaptive difficulty."""
    WIN_RATE = "win_rate"
    AVERAGE_BET = "average_bet"
    TIME_PER_DECISION = "time_per_decision"
    RISK_TAKING = "risk_taking"
    STRATEGY_COMPLEXITY = "strategy_complexity"
    VARIANCE_TOLERANCE = "variance_tolerance"
    SESSION_DURATION = "session_duration"
    RETURN_FREQUENCY = "return_frequency"


class AdaptationTrigger(Enum):
    """Events that can trigger difficulty adaptation."""
    SESSION_START = "session_start"
    CONSECUTIVE_WINS = "consecutive_wins"
    CONSECUTIVE_LOSSES = "consecutive_losses"
    BANKROLL_THRESHOLD = "bankroll_threshold"
    PLAYER_FRUSTRATION = "player_frustration"
    PLAYER_BOREDOM = "player_boredom"
    TIME_BASED = "time_based"
    EXPLICIT_REQUEST = "explicit_request"


@dataclass
class PlayerPerformanceProfile:
    """Player performance data used for difficulty adaptation."""
    player_id: str
    game_type: GameType
    metrics: Dict[PerformanceMetric, float] = field(default_factory=dict)
    historical_performance: List[Dict[str, Any]] = field(default_factory=list)
    current_difficulty: float = 3.0  # Scale of 0-6, matching DifficultyLevel
    optimal_difficulty: Optional[float] = None
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: int = field(default_factory=lambda: int(time.time()))
    
    def add_performance_data(self, 
                           session_id: str,
                           metrics: Dict[PerformanceMetric, float],
                           session_outcome: Dict[str, Any]) -> None:
        """
        Add new performance data from a game session.
        
        Args:
            session_id: Unique identifier for the game session
            metrics: Performance metrics from the session
            session_outcome: Outcome data from the session
        """
        # Update current metrics with exponential moving average
        alpha = 0.3  # Weight for new data
        
        for metric, value in metrics.items():
            if metric in self.metrics:
                self.metrics[metric] = (1 - alpha) * self.metrics[metric] + alpha * value
            else:
                self.metrics[metric] = value
        
        # Add to historical performance
        self.historical_performance.append({
            'session_id': session_id,
            'timestamp': int(time.time()),
            'metrics': {m.value: v for m, v in metrics.items()},
            'outcome': session_outcome
        })
        
        # Limit history size
        if len(self.historical_performance) > 100:
            self.historical_performance = self.historical_performance[-100:]
        
        self.last_updated = int(time.time())
    
    def record_adaptation(self, 
                        trigger: AdaptationTrigger,
                        previous_difficulty: float,
                        new_difficulty: float,
                        adaptation_reason: str) -> None:
        """
        Record a difficulty adaptation event.
        
        Args:
            trigger: What triggered the adaptation
            previous_difficulty: Difficulty level before adaptation
            new_difficulty: Difficulty level after adaptation
            adaptation_reason: Reason for the adaptation
        """
        self.adaptation_history.append({
            'timestamp': int(time.time()),
            'trigger': trigger.value,
            'previous_difficulty': previous_difficulty,
            'new_difficulty': new_difficulty,
            'reason': adaptation_reason
        })
        
        # Limit history size
        if len(self.adaptation_history) > 50:
            self.adaptation_history = self.adaptation_history[-50:]
        
        # Update current difficulty
        self.current_difficulty = new_difficulty
        self.last_updated = int(time.time())


@dataclass
class GameDifficultyParameters:
    """Parameters that control difficulty for a specific game type."""
    game_type: GameType
    parameters: Dict[str, float] = field(default_factory=dict)
    difficulty_mapping: Dict[DifficultyLevel, Dict[str, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default parameters if not provided."""
        if not self.parameters and not self.difficulty_mapping:
            self._initialize_default_parameters()
    
    def _initialize_default_parameters(self) -> None:
        """Initialize default parameters based on game type."""
        if self.game_type == GameType.ECLIPSE_ROULETTE:
            # Default parameters for Eclipse Roulette
            self.parameters = {
                'house_edge': 0.05,  # 5% house edge
                'volatility': 0.5,   # Medium volatility
                'special_feature_frequency': 0.1,  # 10% chance of special features
                'bonus_multiplier': 1.5,  # 1.5x bonus multiplier
                'time_pressure': 0.3,  # Low-medium time pressure
                'complexity': 0.4,  # Medium complexity
            }
            
            # Difficulty mappings
            self.difficulty_mapping = {
                DifficultyLevel.VERY_EASY: {
                    'house_edge': 0.02,
                    'volatility': 0.3,
                    'special_feature_frequency': 0.2,
                    'bonus_multiplier': 2.0,
                    'time_pressure': 0.1,
                    'complexity': 0.2,
                },
                DifficultyLevel.EASY: {
                    'house_edge': 0.03,
                    'volatility': 0.4,
                    'special_feature_frequency': 0.15,
                    'bonus_multiplier': 1.8,
                    'time_pressure': 0.2,
                    'complexity': 0.3,
                },
                DifficultyLevel.MEDIUM: {
                    'house_edge': 0.05,
                    'volatility': 0.5,
                    'special_feature_frequency': 0.1,
                    'bonus_multiplier': 1.5,
                    'time_pressure': 0.3,
                    'complexity': 0.4,
                },
                DifficultyLevel.CHALLENGING: {
                    'house_edge': 0.06,
                    'volatility': 0.6,
                    'special_feature_frequency': 0.08,
                    'bonus_multiplier': 1.3,
                    'time_pressure': 0.4,
                    'complexity': 0.5,
                },
                DifficultyLevel.HARD: {
                    'house_edge': 0.07,
                    'volatility': 0.7,
                    'special_feature_frequency': 0.05,
                    'bonus_multiplier': 1.2,
                    'time_pressure': 0.6,
                    'complexity': 0.7,
                },
                DifficultyLevel.VERY_HARD: {
                    'house_edge': 0.08,
                    'volatility': 0.8,
                    'special_feature_frequency': 0.03,
                    'bonus_multiplier': 1.1,
                    'time_pressure': 0.8,
                    'complexity': 0.8,
                },
                DifficultyLevel.EXTREME: {
                    'house_edge': 0.1,
                    'volatility': 0.9,
                    'special_feature_frequency': 0.02,
                    'bonus_multiplier': 1.0,
                    'time_pressure': 0.9,
                    'complexity': 0.9,
                },
            }
            
        elif self.game_type == GameType.NEURAL_HOLDEM:
            # Default parameters for Neural Hold'em
            self.parameters = {
                'ai_skill_level': 0.5,  # Medium AI skill
                'hand_quality_distribution': 0.5,  # Standard distribution
                'bluff_frequency': 0.3,  # Medium bluff frequency
                'tell_visibility': 0.4,  # Medium tell visibility
                'time_per_decision': 20,  # 20 seconds per decision
                'starting_chips_ratio': 1.0,  # Standard starting chips
            }
            
            # Difficulty mappings
            self.difficulty_mapping = {
                DifficultyLevel.VERY_EASY: {
                    'ai_skill_level': 0.1,
                    'hand_quality_distribution': 0.7,
                    'bluff_frequency': 0.1,
                    'tell_visibility': 0.8,
                    'time_per_decision': 30,
                    'starting_chips_ratio': 1.5,
                },
                DifficultyLevel.EASY: {
                    'ai_skill_level': 0.3,
                    'hand_quality_distribution': 0.6,
                    'bluff_frequency': 0.2,
                    'tell_visibility': 0.6,
                    'time_per_decision': 25,
                    'starting_chips_ratio': 1.2,
                },
                DifficultyLevel.MEDIUM: {
                    'ai_skill_level': 0.5,
                    'hand_quality_distribution': 0.5,
                    'bluff_frequency': 0.3,
                    'tell_visibility': 0.4,
                    'time_per_decision': 20,
                    'starting_chips_ratio': 1.0,
                },
                DifficultyLevel.CHALLENGING: {
                    'ai_skill_level': 0.6,
                    'hand_quality_distribution': 0.5,
                    'bluff_frequency': 0.4,
                    'tell_visibility': 0.3,
                    'time_per_decision': 15,
                    'starting_chips_ratio': 0.9,
                },
                DifficultyLevel.HARD: {
                    'ai_skill_level': 0.7,
                    'hand_quality_distribution': 0.5,
                    'bluff_frequency': 0.5,
                    'tell_visibility': 0.2,
                    'time_per_decision': 12,
                    'starting_chips_ratio': 0.8,
                },
                DifficultyLevel.VERY_HARD: {
                    'ai_skill_level': 0.85,
                    'hand_quality_distribution': 0.5,
                    'bluff_frequency': 0.6,
                    'tell_visibility': 0.1,
                    'time_per_decision': 10,
                    'starting_chips_ratio': 0.7,
                },
                DifficultyLevel.EXTREME: {
                    'ai_skill_level': 0.95,
                    'hand_quality_distribution': 0.5,
                    'bluff_frequency': 0.7,
                    'tell_visibility': 0.05,
                    'time_per_decision': 8,
                    'starting_chips_ratio': 0.6,
                },
            }
            
        elif self.game_type == GameType.CHAOS_SLOTS:
            # Default parameters for Chaos Slots
            self.parameters = {
                'rtp': 0.95,  # 95% return to player
                'hit_frequency': 0.3,  # 30% hit frequency
                'volatility': 0.6,  # Medium-high volatility
                'feature_trigger_chance': 0.05,  # 5% feature trigger chance
                'bonus_game_difficulty': 0.5,  # Medium bonus game difficulty
                'symbol_complexity': 0.5,  # Medium symbol complexity
            }
            
            # Difficulty mappings
            self.difficulty_mapping = {
                DifficultyLevel.VERY_EASY: {
                    'rtp': 0.98,
                    'hit_frequency': 0.4,
                    'volatility': 0.3,
                    'feature_trigger_chance': 0.1,
                    'bonus_game_difficulty': 0.2,
                    'symbol_complexity': 0.2,
                },
                DifficultyLevel.EASY: {
                    'rtp': 0.97,
                    'hit_frequency': 0.35,
                    'volatility': 0.4,
                    'feature_trigger_chance': 0.08,
                    'bonus_game_difficulty': 0.3,
                    'symbol_complexity': 0.3,
                },
                DifficultyLevel.MEDIUM: {
                    'rtp': 0.95,
                    'hit_frequency': 0.3,
                    'volatility': 0.6,
                    'feature_trigger_chance': 0.05,
                    'bonus_game_difficulty': 0.5,
                    'symbol_complexity': 0.5,
                },
                DifficultyLevel.CHALLENGING: {
                    'rtp': 0.94,
                    'hit_frequency': 0.25,
                    'volatility': 0.7,
                    'feature_trigger_chance': 0.04,
                    'bonus_game_difficulty': 0.6,
                    'symbol_complexity': 0.6,
                },
                DifficultyLevel.HARD: {
                    'rtp': 0.92,
                    'hit_frequency': 0.2,
                    'volatility': 0.8,
                    'feature_trigger_chance': 0.03,
                    'bonus_game_difficulty': 0.7,
                    'symbol_complexity': 0.7,
                },
                DifficultyLevel.VERY_HARD: {
                    'rtp': 0.9,
                    'hit_frequency': 0.15,
                    'volatility': 0.9,
                    'feature_trigger_chance': 0.02,
                    'bonus_game_difficulty': 0.8,
                    'symbol_complexity': 0.8,
                },
                DifficultyLevel.EXTREME: {
                    'rtp': 0.88,
                    'hit_frequency': 0.1,
                    'volatility': 1.0,
                    'feature_trigger_chance': 0.01,
                    'bonus_game_difficulty': 0.9,
                    'symbol_complexity': 0.9,
                },
            }
        
        else:
            # Generic parameters for other games
            self.parameters = {
                'difficulty_scalar': 0.5,  # Medium difficulty
                'reward_frequency': 0.5,  # Medium reward frequency
                'complexity': 0.5,  # Medium complexity
                'time_pressure': 0.5,  # Medium time pressure
                'punishment_severity': 0.5,  # Medium punishment severity
                'randomness': 0.5,  # Medium randomness
            }
            
            # Generic difficulty mappings
            self.difficulty_mapping = {
                DifficultyLevel.VERY_EASY: {
                    'difficulty_scalar': 0.1,
                    'reward_frequency': 0.8,
                    'complexity': 0.2,
                    'time_pressure': 0.1,
                    'punishment_severity': 0.1,
                    'randomness': 0.3,
                },
                DifficultyLevel.EASY: {
                    'difficulty_scalar': 0.3,
                    'reward_frequency': 0.7,
                    'complexity': 0.3,
                    'time_pressure': 0.2,
                    'punishment_severity': 0.2,
                    'randomness': 0.4,
                },
                DifficultyLevel.MEDIUM: {
                    'difficulty_scalar': 0.5,
                    'reward_frequency': 0.5,
                    'complexity': 0.5,
                    'time_pressure': 0.5,
                    'punishment_severity': 0.5,
                    'randomness': 0.5,
                },
                DifficultyLevel.CHALLENGING: {
                    'difficulty_scalar': 0.6,
                    'reward_frequency': 0.4,
                    'complexity': 0.6,
                    'time_pressure': 0.6,
                    'punishment_severity': 0.6,
                    'randomness': 0.5,
                },
                DifficultyLevel.HARD: {
                    'difficulty_scalar': 0.7,
                    'reward_frequency': 0.3,
                    'complexity': 0.7,
                    'time_pressure': 0.7,
                    'punishment_severity': 0.7,
                    'randomness': 0.6,
                },
                DifficultyLevel.VERY_HARD: {
                    'difficulty_scalar': 0.85,
                    'reward_frequency': 0.2,
                    'complexity': 0.8,
                    'time_pressure': 0.8,
                    'punishment_severity': 0.8,
                    'randomness': 0.7,
                },
                DifficultyLevel.EXTREME: {
                    'difficulty_scalar': 1.0,
                    'reward_frequency': 0.1,
                    'complexity': 0.9,
                    'time_pressure': 0.9,
                    'punishment_severity': 0.9,
                    'randomness': 0.8,
                },
            }
    
    def get_parameters_for_difficulty(self, difficulty_level: Union[DifficultyLevel, float]) -> Dict[str, float]:
        """
        Get game parameters for a specific difficulty level.
        
        Args:
            difficulty_level: Difficulty level (enum or float 0-6)
            
        Returns:
            Dictionary of game parameters
        """
        # Handle float difficulty (interpolate between levels)
        if isinstance(difficulty_level, float):
            return self._interpolate_parameters(difficulty_level)
        
        # Handle enum difficulty (direct mapping)
        if difficulty_level in self.difficulty_mapping:
            return self.difficulty_mapping[difficulty_level]
        
        # Default to medium if not found
        return self.difficulty_mapping.get(DifficultyLevel.MEDIUM, self.parameters)
    
    def _interpolate_parameters(self, difficulty_value: float) -> Dict[str, float]:
        """
        Interpolate parameters between two difficulty levels.
        
        Args:
            difficulty_value: Float difficulty value (0-6)
            
        Returns:
            Interpolated parameters
        """
        # Clamp difficulty value
        difficulty_value = max(0.0, min(6.0, difficulty_value))
        
        # Find the two closest difficulty levels
        lower_level = DifficultyLevel(math.floor(difficulty_value))
        upper_level = DifficultyLevel(min(6, math.ceil(difficulty_value)))
        
        # If same level, return that level's parameters
        if lower_level == upper_level:
            return self.difficulty_mapping[lower_level]
        
        # Get parameters for both levels
        lower_params = self.difficulty_mapping[lower_level]
        upper_params = self.difficulty_mapping[upper_level]
        
        # Calculate interpolation factor
        factor = difficulty_value - math.floor(difficulty_value)
        
        # Interpolate each parameter
        result = {}
        for key in lower_params:
            if key in upper_params:
                result[key] = lower_params[key] * (1 - factor) + upper_params[key] * factor
            else:
                result[key] = lower_params[key]
        
        return result
    
    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Update the current parameters.
        
        Args:
            parameters: New parameter values
        """
        self.parameters.update(parameters)


class AdaptiveDifficultySystem:
    """
    Core system for managing adaptive difficulty across all games.
    
    This class handles player performance tracking, difficulty adjustment,
    and parameter management for all game types.
    """
    
    def __init__(self):
        """Initialize the adaptive difficulty system."""
        # Player performance profiles
        self.player_profiles: Dict[str, Dict[GameType, PlayerPerformanceProfile]] = {}
        
        # Game difficulty parameters
        self.game_parameters: Dict[GameType, GameDifficultyParameters] = {}
        
        # Initialize default game parameters
        self._initialize_default_game_parameters()
        
        # Configuration
        self.config = {
            'adaptation_rate': 0.2,  # How quickly difficulty adapts (0-1)
            'win_rate_target': 0.4,  # Target win rate for balanced difficulty
            'session_weight': 0.3,   # Weight of current session vs. historical data
            'frustration_threshold': 0.7,  # Threshold for detecting frustration
            'boredom_threshold': 0.3,  # Threshold for detecting boredom
            'consecutive_threshold': 5,  # Number of consecutive wins/losses to trigger adaptation
            'min_sessions_for_profile': 3,  # Minimum sessions needed for reliable profile
        }
    
    def _initialize_default_game_parameters(self) -> None:
        """Initialize default parameters for all game types."""
        for game_type in GameType:
            self.game_parameters[game_type] = GameDifficultyParameters(game_type=game_type)
    
    def get_player_profile(self, player_id: str, game_type: GameType) -> PlayerPerformanceProfile:
        """
        Get a player's performance profile for a specific game type.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            
        Returns:
            Player performance profile
        """
        # Create player entry if it doesn't exist
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = {}
        
        # Create game type entry if it doesn't exist
        if game_type not in self.player_profiles[player_id]:
            self.player_profiles[player_id][game_type] = PlayerPerformanceProfile(
                player_id=player_id,
                game_type=game_type
            )
        
        return self.player_profiles[player_id][game_type]
    
    def record_performance(self, player_id: str, game_type: GameType, 
                         session_id: str, metrics: Dict[PerformanceMetric, float],
                         session_outcome: Dict[str, Any]) -> None:
        """
        Record player performance data from a game session.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            session_id: Unique identifier for the game session
            metrics: Performance metrics from the session
            session_outcome: Outcome data from the session
        """
        profile = self.get_player_profile(player_id, game_type)
        profile.add_performance_data(session_id, metrics, session_outcome)
    
    def get_game_parameters(self, player_id: str, game_type: GameType, 
                          session_id: str = None) -> Dict[str, float]:
        """
        Get personalized game parameters for a player.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary of game parameters
        """
        # Get player profile
        profile = self.get_player_profile(player_id, game_type)
        
        # Get base game parameters
        game_params = self.game_parameters[game_type]
        
        # Check if we need to adapt difficulty
        should_adapt, trigger = self._should_adapt_difficulty(profile, session_id)
        
        if should_adapt:
            # Calculate new difficulty
            new_difficulty = self._calculate_optimal_difficulty(profile)
            
            # Record adaptation if difficulty changed
            if abs(new_difficulty - profile.current_difficulty) > 0.1:
                profile.record_adaptation(
                    trigger=trigger,
                    previous_difficulty=profile.current_difficulty,
                    new_difficulty=new_difficulty,
                    adaptation_reason=f"Adapting to player performance. Trigger: {trigger.value}"
                )
        
        # Get parameters for current difficulty
        return game_params.get_parameters_for_difficulty(profile.current_difficulty)
    
    def _should_adapt_difficulty(self, profile: PlayerPerformanceProfile, 
                               session_id: str = None) -> Tuple[bool, AdaptationTrigger]:
        """
        Determine if difficulty should be adapted for a player.
        
        Args:
            profile: Player performance profile
            session_id: Optional session ID
            
        Returns:
            Tuple of (should_adapt, trigger)
        """
        # Always adapt at session start if we have enough data
        if session_id and len(profile.historical_performance) >= self.config['min_sessions_for_profile']:
            return True, AdaptationTrigger.SESSION_START
        
        # Check for consecutive wins/losses
        if len(profile.historical_performance) >= self.config['consecutive_threshold']:
            recent_outcomes = [
                session['outcome'].get('win', False) 
                for session in profile.historical_performance[-self.config['consecutive_threshold']:]
            ]
            
            if all(recent_outcomes):
                return True, AdaptationTrigger.CONSECUTIVE_WINS
            
            if not any(recent_outcomes):
                return True, AdaptationTrigger.CONSECUTIVE_LOSSES
        
        # Check for player frustration
        if PerformanceMetric.WIN_RATE in profile.metrics:
            win_rate = profile.metrics[PerformanceMetric.WIN_RATE]
            target = self.config['win_rate_target']
            
            if win_rate < target - self.config['frustration_threshold']:
                return True, AdaptationTrigger.PLAYER_FRUSTRATION
            
            if win_rate > target + self.config['boredom_threshold']:
                return True, AdaptationTrigger.PLAYER_BOREDOM
        
        # Time-based adaptation (every 5 sessions)
        if len(profile.historical_performance) % 5 == 0 and len(profile.historical_performance) > 0:
            return True, AdaptationTrigger.TIME_BASED
        
        return False, None
    
    def _calculate_optimal_difficulty(self, profile: PlayerPerformanceProfile) -> float:
        """
        Calculate the optimal difficulty level for a player.
        
        Args:
            profile: Player performance profile
            
        Returns:
            Optimal difficulty value (0-6)
        """
        # If we don't have enough data, use current difficulty
        if len(profile.historical_performance) < self.config['min_sessions_for_profile']:
            return profile.current_difficulty
        
        # Start with current difficulty
        current = profile.current_difficulty
        
        # Adjust based on win rate if available
        if PerformanceMetric.WIN_RATE in profile.metrics:
            win_rate = profile.metrics[PerformanceMetric.WIN_RATE]
            target = self.config['win_rate_target']
            
            # Calculate win rate adjustment
            # Higher win rate -> increase difficulty, lower win rate -> decrease difficulty
            win_rate_adjustment = (win_rate - target) * 3.0  # Scale factor
            
            # Apply adjustment with adaptation rate
            difficulty_adjustment = win_rate_adjustment * self.config['adaptation_rate']
            new_difficulty = current + difficulty_adjustment
            
            # Clamp to valid range
            new_difficulty = max(0.0, min(6.0, new_difficulty))
            
            # Store optimal difficulty
            profile.optimal_difficulty = new_difficulty
            
            return new_difficulty
        
        # If no win rate data, adjust based on other metrics if available
        adjustments = []
        
        if PerformanceMetric.RISK_TAKING in profile.metrics:
            risk_taking = profile.metrics[PerformanceMetric.RISK_TAKING]
            # Higher risk taking -> can handle higher difficulty
            risk_adjustment = (risk_taking - 0.5) * 2.0
            adjustments.append(risk_adjustment * 0.5)  # Weight factor
        
        if PerformanceMetric.STRATEGY_COMPLEXITY in profile.metrics:
            strategy = profile.metrics[PerformanceMetric.STRATEGY_COMPLEXITY]
            # More complex strategy -> can handle higher difficulty
            strategy_adjustment = (strategy - 0.5) * 2.0
            adjustments.append(strategy_adjustment * 0.7)  # Weight factor
        
        if PerformanceMetric.VARIANCE_TOLERANCE in profile.metrics:
            variance = profile.metrics[PerformanceMetric.VARIANCE_TOLERANCE]
            # Higher variance tolerance -> can handle higher difficulty
            variance_adjustment = (variance - 0.5) * 2.0
            adjustments.append(variance_adjustment * 0.3)  # Weight factor
        
        # If we have adjustments, apply them
        if adjustments:
            avg_adjustment = sum(adjustments) / len(adjustments)
            new_difficulty = current + avg_adjustment * self.config['adaptation_rate']
            
            # Clamp to valid range
            new_difficulty = max(0.0, min(6.0, new_difficulty))
            
            # Store optimal difficulty
            profile.optimal_difficulty = new_difficulty
            
            return new_difficulty
        
        # If no relevant metrics, return current difficulty
        return current
    
    def set_difficulty_directly(self, player_id: str, game_type: GameType, 
                              difficulty_level: Union[DifficultyLevel, float]) -> Dict[str, float]:
        """
        Set difficulty directly for a player (e.g., from explicit player choice).
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            difficulty_level: Desired difficulty level
            
        Returns:
            Updated game parameters
        """
        # Get player profile
        profile = self.get_player_profile(player_id, game_type)
        
        # Convert enum to float if needed
        if isinstance(difficulty_level, DifficultyLevel):
            difficulty_value = difficulty_level.value
        else:
            difficulty_value = difficulty_level
        
        # Record adaptation
        profile.record_adaptation(
            trigger=AdaptationTrigger.EXPLICIT_REQUEST,
            previous_difficulty=profile.current_difficulty,
            new_difficulty=difficulty_value,
            adaptation_reason="Explicit difficulty selection by player"
        )
        
        # Get game parameters for this difficulty
        game_params = self.game_parameters[game_type]
        return game_params.get_parameters_for_difficulty(difficulty_value)
    
    def analyze_player_difficulty_curve(self, player_id: str, game_type: GameType) -> Dict[str, Any]:
        """
        Analyze a player's difficulty curve over time.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            
        Returns:
            Analysis results
        """
        profile = self.get_player_profile(player_id, game_type)
        
        # Not enough data
        if len(profile.adaptation_history) < 3:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough adaptation history to analyze difficulty curve',
                'current_difficulty': profile.current_difficulty
            }
        
        # Extract difficulty values over time
        timestamps = []
        difficulties = []
        
        for adaptation in profile.adaptation_history:
            timestamps.append(adaptation['timestamp'])
            difficulties.append(adaptation['new_difficulty'])
        
        # Calculate statistics
        avg_difficulty = sum(difficulties) / len(difficulties)
        min_difficulty = min(difficulties)
        max_difficulty = max(difficulties)
        
        # Calculate trend (simple linear regression)
        if len(difficulties) >= 5:
            x = np.array(range(len(difficulties)))
            y = np.array(difficulties)
            
            # Calculate slope
            n = len(x)
            slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x * x) - np.sum(x) ** 2)
            
            # Determine trend
            if slope > 0.1:
                trend = "increasing"
            elif slope < -0.1:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Calculate volatility (standard deviation)
        volatility = np.std(difficulties) if len(difficulties) > 1 else 0
        
        return {
            'status': 'success',
            'current_difficulty': profile.current_difficulty,
            'optimal_difficulty': profile.optimal_difficulty,
            'average_difficulty': avg_difficulty,
            'min_difficulty': min_difficulty,
            'max_difficulty': max_difficulty,
            'difficulty_range': max_difficulty - min_difficulty,
            'difficulty_trend': trend,
            'difficulty_volatility': volatility,
            'adaptation_count': len(profile.adaptation_history),
            'first_adaptation_time': timestamps[0],
            'last_adaptation_time': timestamps[-1],
            'time_span_seconds': timestamps[-1] - timestamps[0]
        }
    
    def get_difficulty_distribution(self) -> Dict[str, Any]:
        """
        Get distribution of difficulty levels across all players.
        
        Returns:
            Difficulty distribution statistics
        """
        all_difficulties = []
        game_type_difficulties = {game_type.value: [] for game_type in GameType}
        
        # Collect all current difficulties
        for player_id, game_profiles in self.player_profiles.items():
            for game_type, profile in game_profiles.items():
                all_difficulties.append(profile.current_difficulty)
                game_type_difficulties[game_type.value].append(profile.current_difficulty)
        
        # If no data, return empty stats
        if not all_difficulties:
            return {
                'status': 'no_data',
                'message': 'No difficulty data available'
            }
        
        # Calculate overall statistics
        overall_stats = {
            'count': len(all_difficulties),
            'average': sum(all_difficulties) / len(all_difficulties),
            'median': sorted(all_difficulties)[len(all_difficulties) // 2],
            'min': min(all_difficulties),
            'max': max(all_difficulties),
            'std_dev': np.std(all_difficulties) if len(all_difficulties) > 1 else 0
        }
        
        # Calculate histogram data
        hist, bins = np.histogram(all_difficulties, bins=7, range=(0, 6))
        histogram = [{'bin': f"{bins[i]:.1f}-{bins[i+1]:.1f}", 'count': int(hist[i])} for i in range(len(hist))]
        
        # Calculate per-game statistics
        game_stats = {}
        for game_type, difficulties in game_type_difficulties.items():
            if difficulties:
                game_stats[game_type] = {
                    'count': len(difficulties),
                    'average': sum(difficulties) / len(difficulties),
                    'median': sorted(difficulties)[len(difficulties) // 2],
                    'min': min(difficulties),
                    'max': max(difficulties),
                    'std_dev': np.std(difficulties) if len(difficulties) > 1 else 0
                }
        
        return {
            'status': 'success',
            'overall': overall_stats,
            'histogram': histogram,
            'by_game': game_stats
        }
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the adaptive difficulty system to a file.
        
        Args:
            filepath: Path to save the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to serializable format
            state = {
                'player_profiles': {},
                'game_parameters': {},
                'config': self.config
            }
            
            # Serialize player profiles
            for player_id, game_profiles in self.player_profiles.items():
                state['player_profiles'][player_id] = {}
                
                for game_type, profile in game_profiles.items():
                    state['player_profiles'][player_id][game_type.value] = {
                        'player_id': profile.player_id,
                        'game_type': profile.game_type.value,
                        'metrics': {metric.value: value for metric, value in profile.metrics.items()},
                        'historical_performance': profile.historical_performance,
                        'current_difficulty': profile.current_difficulty,
                        'optimal_difficulty': profile.optimal_difficulty,
                        'adaptation_history': profile.adaptation_history,
                        'last_updated': profile.last_updated
                    }
            
            # Serialize game parameters
            for game_type, params in self.game_parameters.items():
                state['game_parameters'][game_type.value] = {
                    'game_type': params.game_type.value,
                    'parameters': params.parameters,
                    'difficulty_mapping': {level.value: mapping for level, mapping in params.difficulty_mapping.items()}
                }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving adaptive difficulty state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the state of the adaptive difficulty system from a file.
        
        Args:
            filepath: Path to load the state from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Load configuration
            if 'config' in state:
                self.config = state['config']
            
            # Load game parameters
            self.game_parameters = {}
            for game_type_str, params_data in state.get('game_parameters', {}).items():
                game_type = GameType(game_type_str)
                
                params = GameDifficultyParameters(game_type=game_type)
                params.parameters = params_data['parameters']
                
                # Convert difficulty mapping keys from strings to enums
                params.difficulty_mapping = {
                    DifficultyLevel(int(level)): mapping 
                    for level, mapping in params_data['difficulty_mapping'].items()
                }
                
                self.game_parameters[game_type] = params
            
            # Load player profiles
            self.player_profiles = {}
            for player_id, game_profiles_data in state.get('player_profiles', {}).items():
                self.player_profiles[player_id] = {}
                
                for game_type_str, profile_data in game_profiles_data.items():
                    game_type = GameType(game_type_str)
                    
                    profile = PlayerPerformanceProfile(
                        player_id=profile_data['player_id'],
                        game_type=game_type
                    )
                    
                    # Convert metrics keys from strings to enums
                    profile.metrics = {
                        PerformanceMetric(metric): value 
                        for metric, value in profile_data['metrics'].items()
                    }
                    
                    profile.historical_performance = profile_data['historical_performance']
                    profile.current_difficulty = profile_data['current_difficulty']
                    profile.optimal_difficulty = profile_data['optimal_difficulty']
                    profile.adaptation_history = profile_data['adaptation_history']
                    profile.last_updated = profile_data['last_updated']
                    
                    self.player_profiles[player_id][game_type] = profile
            
            return True
        
        except Exception as e:
            print(f"Error loading adaptive difficulty state: {e}")
            return False
