"""
Player Performance Analysis Module for Adaptive Difficulty System

This module provides analysis tools for player performance data, including:
- Performance metric calculation from raw game data
- Pattern recognition in player behavior
- Skill level assessment
- Learning curve analysis
- Engagement and frustration detection

These analyses inform the adaptive difficulty system to create optimal
challenge levels for each player.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
import math
import time
from enum import Enum
from dataclasses import dataclass, field

from core.adaptive_difficulty import (
    PerformanceMetric, GameType, PlayerPerformanceProfile,
    DifficultyLevel, AdaptationTrigger
)


class EngagementState(Enum):
    """Player engagement states based on performance analysis."""
    FLOW = "flow"  # Optimal engagement
    BORED = "bored"  # Too easy, losing interest
    FRUSTRATED = "frustrated"  # Too difficult, becoming frustrated
    LEARNING = "learning"  # In learning phase, still improving
    MASTERY = "mastery"  # Achieved mastery, needs new challenges
    EXPERIMENTING = "experimenting"  # Trying different strategies
    DECLINING = "declining"  # Performance declining (tired, distracted)
    INCONSISTENT = "inconsistent"  # Highly variable performance


class SkillComponent(Enum):
    """Components that make up a player's skill profile."""
    REACTION_TIME = "reaction_time"
    DECISION_MAKING = "decision_making"
    PATTERN_RECOGNITION = "pattern_recognition"
    RISK_ASSESSMENT = "risk_assessment"
    STRATEGIC_PLANNING = "strategic_planning"
    EMOTIONAL_CONTROL = "emotional_control"
    ADAPTABILITY = "adaptability"
    FOCUS_DURATION = "focus_duration"


@dataclass
class PlayerSkillProfile:
    """Detailed breakdown of a player's skill components."""
    player_id: str
    game_type: GameType
    components: Dict[SkillComponent, float] = field(default_factory=dict)
    overall_skill: float = 0.5  # 0-1 scale
    confidence: float = 0.0  # How confident we are in this assessment (0-1)
    last_updated: int = field(default_factory=lambda: int(time.time()))


class PerformanceAnalyzer:
    """
    Analyzes player performance data to extract meaningful insights.
    
    This class processes raw game data and session outcomes to calculate
    performance metrics, detect patterns, and assess player skill and engagement.
    """
    
    def __init__(self):
        """Initialize the performance analyzer."""
        # Player skill profiles
        self.skill_profiles: Dict[str, Dict[GameType, PlayerSkillProfile]] = {}
        
        # Configuration
        self.config = {
            'min_sessions_for_confidence': 5,  # Minimum sessions for confident assessment
            'engagement_window_size': 10,  # Number of recent sessions to analyze for engagement
            'learning_rate_threshold': 0.05,  # Threshold for detecting learning state
            'mastery_threshold': 0.85,  # Skill threshold for mastery state
            'consistency_threshold': 0.15,  # Standard deviation threshold for consistency
            'boredom_win_rate': 0.75,  # Win rate threshold for boredom detection
            'frustration_win_rate': 0.25,  # Win rate threshold for frustration detection
        }
    
    def get_skill_profile(self, player_id: str, game_type: GameType) -> PlayerSkillProfile:
        """
        Get a player's skill profile for a specific game type.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            
        Returns:
            Player skill profile
        """
        # Create player entry if it doesn't exist
        if player_id not in self.skill_profiles:
            self.skill_profiles[player_id] = {}
        
        # Create game type entry if it doesn't exist
        if game_type not in self.skill_profiles[player_id]:
            self.skill_profiles[player_id][game_type] = PlayerSkillProfile(
                player_id=player_id,
                game_type=game_type
            )
        
        return self.skill_profiles[player_id][game_type]
    
    def analyze_raw_game_data(self, player_id: str, game_type: GameType, 
                            session_id: str, raw_data: Dict[str, Any]) -> Dict[PerformanceMetric, float]:
        """
        Analyze raw game data to calculate performance metrics.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            session_id: Unique identifier for the game session
            raw_data: Raw game data from the session
            
        Returns:
            Dictionary of calculated performance metrics
        """
        metrics = {}
        
        # Process based on game type
        if game_type == GameType.ECLIPSE_ROULETTE:
            metrics = self._analyze_eclipse_roulette_data(raw_data)
        elif game_type == GameType.NEURAL_HOLDEM:
            metrics = self._analyze_neural_holdem_data(raw_data)
        elif game_type == GameType.CHAOS_SLOTS:
            metrics = self._analyze_chaos_slots_data(raw_data)
        else:
            # Generic analysis for other game types
            metrics = self._analyze_generic_game_data(raw_data)
        
        # Update skill profile
        self._update_skill_profile(player_id, game_type, metrics, raw_data)
        
        return metrics
    
    def _analyze_eclipse_roulette_data(self, raw_data: Dict[str, Any]) -> Dict[PerformanceMetric, float]:
        """
        Analyze Eclipse Roulette game data.
        
        Args:
            raw_data: Raw game data
            
        Returns:
            Calculated performance metrics
        """
        metrics = {}
        
        # Extract relevant data
        bets = raw_data.get('bets', [])
        wins = raw_data.get('wins', [])
        bet_amounts = raw_data.get('bet_amounts', [])
        decision_times = raw_data.get('decision_times', [])
        
        # Calculate win rate
        if bets:
            win_rate = len(wins) / len(bets)
            metrics[PerformanceMetric.WIN_RATE] = win_rate
        
        # Calculate average bet
        if bet_amounts:
            avg_bet = sum(bet_amounts) / len(bet_amounts)
            metrics[PerformanceMetric.AVERAGE_BET] = avg_bet
        
        # Calculate time per decision
        if decision_times:
            avg_time = sum(decision_times) / len(decision_times)
            metrics[PerformanceMetric.TIME_PER_DECISION] = avg_time
        
        # Calculate risk taking (based on bet spread and complexity)
        if bet_amounts and len(bet_amounts) > 1:
            # Normalize bet amounts
            max_bet = max(bet_amounts)
            if max_bet > 0:
                normalized_bets = [b / max_bet for b in bet_amounts]
                
                # Calculate variance
                variance = np.var(normalized_bets)
                
                # Calculate bet spread (how many different types of bets)
                bet_types = set(raw_data.get('bet_types', []))
                bet_type_diversity = len(bet_types) / 10.0  # Normalize to 0-1 scale
                
                # Combine into risk taking metric
                risk_taking = (variance * 0.5) + (bet_type_diversity * 0.5)
                metrics[PerformanceMetric.RISK_TAKING] = min(1.0, risk_taking)
        
        # Calculate strategy complexity
        bet_patterns = raw_data.get('bet_patterns', [])
        if bet_patterns:
            # Count unique patterns
            unique_patterns = set(tuple(p) for p in bet_patterns)
            pattern_diversity = len(unique_patterns) / len(bet_patterns)
            
            # Calculate pattern length
            avg_pattern_length = sum(len(p) for p in bet_patterns) / len(bet_patterns)
            normalized_length = min(1.0, avg_pattern_length / 5.0)  # Normalize to 0-1
            
            # Combine into strategy complexity
            strategy_complexity = (pattern_diversity * 0.7) + (normalized_length * 0.3)
            metrics[PerformanceMetric.STRATEGY_COMPLEXITY] = strategy_complexity
        
        # Calculate variance tolerance
        if 'consecutive_losses' in raw_data and 'max_drawdown' in raw_data:
            max_consecutive_losses = raw_data['consecutive_losses']
            max_drawdown = raw_data['max_drawdown']
            
            # Normalize
            normalized_losses = min(1.0, max_consecutive_losses / 10.0)
            normalized_drawdown = min(1.0, max_drawdown / 0.5)  # 50% drawdown = 1.0
            
            # Calculate variance tolerance (higher = more tolerant)
            # Invert because higher consecutive losses means lower tolerance
            variance_tolerance = 1.0 - ((normalized_losses * 0.5) + (normalized_drawdown * 0.5))
            metrics[PerformanceMetric.VARIANCE_TOLERANCE] = variance_tolerance
        
        # Calculate session duration
        if 'session_duration' in raw_data:
            # Normalize to 0-1 scale (cap at 2 hours)
            duration_hours = raw_data['session_duration'] / 3600.0
            normalized_duration = min(1.0, duration_hours / 2.0)
            metrics[PerformanceMetric.SESSION_DURATION] = normalized_duration
        
        return metrics
    
    def _analyze_neural_holdem_data(self, raw_data: Dict[str, Any]) -> Dict[PerformanceMetric, float]:
        """
        Analyze Neural Hold'em game data.
        
        Args:
            raw_data: Raw game data
            
        Returns:
            Calculated performance metrics
        """
        metrics = {}
        
        # Extract relevant data
        hands_played = raw_data.get('hands_played', [])
        hands_won = raw_data.get('hands_won', [])
        bet_amounts = raw_data.get('bet_amounts', [])
        decision_times = raw_data.get('decision_times', [])
        bluffs = raw_data.get('bluffs', [])
        folds = raw_data.get('folds', [])
        
        # Calculate win rate
        if hands_played:
            win_rate = len(hands_won) / len(hands_played)
            metrics[PerformanceMetric.WIN_RATE] = win_rate
        
        # Calculate average bet
        if bet_amounts:
            avg_bet = sum(bet_amounts) / len(bet_amounts)
            metrics[PerformanceMetric.AVERAGE_BET] = avg_bet
        
        # Calculate time per decision
        if decision_times:
            avg_time = sum(decision_times) / len(decision_times)
            metrics[PerformanceMetric.TIME_PER_DECISION] = avg_time
        
        # Calculate risk taking (based on bluff frequency and bet sizing)
        if hands_played and bluffs is not None:
            bluff_frequency = len(bluffs) / len(hands_played)
            
            # Calculate bet sizing aggression
            bet_aggression = 0.5  # Default
            if bet_amounts and 'pot_sizes' in raw_data:
                pot_sizes = raw_data['pot_sizes']
                if len(bet_amounts) == len(pot_sizes) and sum(pot_sizes) > 0:
                    # Calculate average bet as percentage of pot
                    bet_pot_ratios = [bet / pot for bet, pot in zip(bet_amounts, pot_sizes) if pot > 0]
                    if bet_pot_ratios:
                        avg_bet_pot_ratio = sum(bet_pot_ratios) / len(bet_pot_ratios)
                        bet_aggression = min(1.0, avg_bet_pot_ratio / 2.0)  # Normalize to 0-1
            
            # Combine into risk taking metric
            risk_taking = (bluff_frequency * 0.6) + (bet_aggression * 0.4)
            metrics[PerformanceMetric.RISK_TAKING] = risk_taking
        
        # Calculate strategy complexity
        if 'action_sequences' in raw_data:
            action_sequences = raw_data['action_sequences']
            
            # Count unique sequences
            unique_sequences = set(tuple(s) for s in action_sequences)
            sequence_diversity = len(unique_sequences) / max(1, len(action_sequences))
            
            # Calculate position awareness
            position_awareness = 0.5  # Default
            if 'position_actions' in raw_data:
                position_actions = raw_data['position_actions']
                # Higher value means actions vary appropriately by position
                position_awareness = position_actions.get('awareness_score', 0.5)
            
            # Calculate hand range understanding
            hand_range = 0.5  # Default
            if 'hand_strength_actions' in raw_data:
                hand_strength_actions = raw_data['hand_strength_actions']
                # Higher value means actions are appropriate for hand strength
                hand_range = hand_strength_actions.get('appropriateness_score', 0.5)
            
            # Combine into strategy complexity
            strategy_complexity = (sequence_diversity * 0.3) + (position_awareness * 0.35) + (hand_range * 0.35)
            metrics[PerformanceMetric.STRATEGY_COMPLEXITY] = strategy_complexity
        
        # Calculate variance tolerance
        if 'stack_volatility' in raw_data and folds is not None and hands_played:
            stack_volatility = raw_data['stack_volatility']
            fold_frequency = len(folds) / len(hands_played)
            
            # Higher volatility tolerance = higher stack volatility and lower fold frequency
            variance_tolerance = (stack_volatility * 0.6) + ((1.0 - fold_frequency) * 0.4)
            metrics[PerformanceMetric.VARIANCE_TOLERANCE] = variance_tolerance
        
        # Calculate session duration
        if 'session_duration' in raw_data:
            # Normalize to 0-1 scale (cap at 3 hours)
            duration_hours = raw_data['session_duration'] / 3600.0
            normalized_duration = min(1.0, duration_hours / 3.0)
            metrics[PerformanceMetric.SESSION_DURATION] = normalized_duration
        
        return metrics
    
    def _analyze_chaos_slots_data(self, raw_data: Dict[str, Any]) -> Dict[PerformanceMetric, float]:
        """
        Analyze Chaos Slots game data.
        
        Args:
            raw_data: Raw game data
            
        Returns:
            Calculated performance metrics
        """
        metrics = {}
        
        # Extract relevant data
        spins = raw_data.get('spins', [])
        wins = raw_data.get('wins', [])
        bet_amounts = raw_data.get('bet_amounts', [])
        feature_triggers = raw_data.get('feature_triggers', [])
        
        # Calculate win rate
        if spins:
            win_rate = len(wins) / len(spins)
            metrics[PerformanceMetric.WIN_RATE] = win_rate
        
        # Calculate average bet
        if bet_amounts:
            avg_bet = sum(bet_amounts) / len(bet_amounts)
            metrics[PerformanceMetric.AVERAGE_BET] = avg_bet
        
        # Calculate risk taking (based on bet variation)
        if bet_amounts and len(bet_amounts) > 1:
            # Calculate coefficient of variation
            mean_bet = sum(bet_amounts) / len(bet_amounts)
            if mean_bet > 0:
                std_dev = math.sqrt(sum((x - mean_bet) ** 2 for x in bet_amounts) / len(bet_amounts))
                cv = std_dev / mean_bet
                
                # Normalize to 0-1 scale
                risk_taking = min(1.0, cv / 2.0)
                metrics[PerformanceMetric.RISK_TAKING] = risk_taking
        
        # Calculate strategy complexity (limited in slots, but can measure bet adjustment)
        if 'bet_adjustments' in raw_data and bet_amounts:
            bet_adjustments = raw_data['bet_adjustments']
            
            # Calculate frequency of adjustments
            adjustment_frequency = len(bet_adjustments) / len(bet_amounts)
            
            # Calculate responsiveness to outcomes
            responsiveness = 0.5  # Default
            if 'outcome_responses' in raw_data:
                outcome_responses = raw_data['outcome_responses']
                # Higher value means player adjusts bets based on recent outcomes
                responsiveness = outcome_responses.get('score', 0.5)
            
            # Combine into strategy complexity
            strategy_complexity = (adjustment_frequency * 0.4) + (responsiveness * 0.6)
            metrics[PerformanceMetric.STRATEGY_COMPLEXITY] = strategy_complexity
        
        # Calculate variance tolerance
        if 'max_drawdown' in raw_data and 'max_consecutive_losses' in raw_data:
            max_drawdown = raw_data['max_drawdown']
            max_consecutive_losses = raw_data['max_consecutive_losses']
            
            # Normalize
            normalized_drawdown = min(1.0, max_drawdown / 0.7)  # 70% drawdown = 1.0
            normalized_losses = min(1.0, max_consecutive_losses / 20.0)  # 20 losses = 1.0
            
            # Calculate variance tolerance (higher = more tolerant)
            # Invert because higher drawdown means lower tolerance
            variance_tolerance = 1.0 - ((normalized_drawdown * 0.6) + (normalized_losses * 0.4))
            metrics[PerformanceMetric.VARIANCE_TOLERANCE] = variance_tolerance
        
        # Calculate session duration
        if 'session_duration' in raw_data:
            # Normalize to 0-1 scale (cap at 2 hours)
            duration_hours = raw_data['session_duration'] / 3600.0
            normalized_duration = min(1.0, duration_hours / 2.0)
            metrics[PerformanceMetric.SESSION_DURATION] = normalized_duration
        
        # Calculate return frequency (how often player returns to play)
        if 'days_since_last_session' in raw_data:
            days_since_last = raw_data['days_since_last_session']
            # Normalize to 0-1 scale (0 days = 1.0, 30+ days = 0.0)
            return_frequency = max(0.0, 1.0 - (days_since_last / 30.0))
            metrics[PerformanceMetric.RETURN_FREQUENCY] = return_frequency
        
        return metrics
    
    def _analyze_generic_game_data(self, raw_data: Dict[str, Any]) -> Dict[PerformanceMetric, float]:
        """
        Analyze generic game data for any game type.
        
        Args:
            raw_data: Raw game data
            
        Returns:
            Calculated performance metrics
        """
        metrics = {}
        
        # Extract common metrics that apply to most games
        if 'win_rate' in raw_data:
            metrics[PerformanceMetric.WIN_RATE] = raw_data['win_rate']
        
        if 'average_bet' in raw_data:
            metrics[PerformanceMetric.AVERAGE_BET] = raw_data['average_bet']
        
        if 'time_per_decision' in raw_data:
            metrics[PerformanceMetric.TIME_PER_DECISION] = raw_data['time_per_decision']
        
        if 'risk_taking' in raw_data:
            metrics[PerformanceMetric.RISK_TAKING] = raw_data['risk_taking']
        
        if 'strategy_complexity' in raw_data:
            metrics[PerformanceMetric.STRATEGY_COMPLEXITY] = raw_data['strategy_complexity']
        
        if 'variance_tolerance' in raw_data:
            metrics[PerformanceMetric.VARIANCE_TOLERANCE] = raw_data['variance_tolerance']
        
        if 'session_duration' in raw_data:
            # Normalize to 0-1 scale (cap at 2 hours)
            duration_hours = raw_data['session_duration'] / 3600.0
            normalized_duration = min(1.0, duration_hours / 2.0)
            metrics[PerformanceMetric.SESSION_DURATION] = normalized_duration
        
        if 'return_frequency' in raw_data:
            metrics[PerformanceMetric.RETURN_FREQUENCY] = raw_data['return_frequency']
        
        return metrics
    
    def _update_skill_profile(self, player_id: str, game_type: GameType, 
                            metrics: Dict[PerformanceMetric, float], 
                            raw_data: Dict[str, Any]) -> None:
        """
        Update a player's skill profile based on performance metrics.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            metrics: Performance metrics
            raw_data: Raw game data
        """
        # Get skill profile
        profile = self.get_skill_profile(player_id, game_type)
        
        # Extract skill components from metrics and raw data
        components = {}
        
        # Reaction time (from time_per_decision, lower is better)
        if PerformanceMetric.TIME_PER_DECISION in metrics:
            time_per_decision = metrics[PerformanceMetric.TIME_PER_DECISION]
            # Convert to 0-1 scale (0 = slow, 1 = fast)
            # Assuming 0.5s is very fast, 10s is very slow
            reaction_time = max(0.0, min(1.0, 1.0 - ((time_per_decision - 0.5) / 9.5)))
            components[SkillComponent.REACTION_TIME] = reaction_time
        
        # Decision making (from win_rate)
        if PerformanceMetric.WIN_RATE in metrics:
            win_rate = metrics[PerformanceMetric.WIN_RATE]
            # Scale win rate to account for house edge
            # In games with house edge, even 45% win rate might be excellent
            adjusted_win_rate = min(1.0, win_rate * 2.0)
            components[SkillComponent.DECISION_MAKING] = adjusted_win_rate
        
        # Pattern recognition (from strategy_complexity)
        if PerformanceMetric.STRATEGY_COMPLEXITY in metrics:
            components[SkillComponent.PATTERN_RECOGNITION] = metrics[PerformanceMetric.STRATEGY_COMPLEXITY]
        
        # Risk assessment (from risk_taking and variance_tolerance)
        risk_assessment = 0.5  # Default
        if PerformanceMetric.RISK_TAKING in metrics and PerformanceMetric.VARIANCE_TOLERANCE in metrics:
            risk_taking = metrics[PerformanceMetric.RISK_TAKING]
            variance_tolerance = metrics[PerformanceMetric.VARIANCE_TOLERANCE]
            
            # Combine into risk assessment (higher = better assessment, not higher risk)
            # Good risk assessment means risk taking aligns with variance tolerance
            risk_alignment = 1.0 - abs(risk_taking - variance_tolerance)
            risk_assessment = risk_alignment
        components[SkillComponent.RISK_ASSESSMENT] = risk_assessment
        
        # Strategic planning (from raw data if available)
        strategic_planning = 0.5  # Default
        if 'strategic_planning_score' in raw_data:
            strategic_planning = raw_data['strategic_planning_score']
        elif 'long_term_decisions' in raw_data:
            # Calculate from long-term decision quality
            long_term_decisions = raw_data['long_term_decisions']
            if isinstance(long_term_decisions, dict) and 'quality_score' in long_term_decisions:
                strategic_planning = long_term_decisions['quality_score']
        components[SkillComponent.STRATEGIC_PLANNING] = strategic_planning
        
        # Emotional control (from consistency in decision making)
        emotional_control = 0.5  # Default
        if 'tilt_indicators' in raw_data:
            tilt_indicators = raw_data['tilt_indicators']
            # Lower tilt = higher emotional control
            emotional_control = 1.0 - tilt_indicators.get('score', 0.5)
        elif 'decision_consistency' in raw_data:
            emotional_control = raw_data['decision_consistency']
        components[SkillComponent.EMOTIONAL_CONTROL] = emotional_control
        
        # Adaptability (from response to changing conditions)
        adaptability = 0.5  # Default
        if 'adaptability_score' in raw_data:
            adaptability = raw_data['adaptability_score']
        elif 'condition_responses' in raw_data:
            condition_responses = raw_data['condition_responses']
            if isinstance(condition_responses, dict) and 'score' in condition_responses:
                adaptability = condition_responses['score']
        components[SkillComponent.ADAPTABILITY] = adaptability
        
        # Focus duration (from session_duration and consistency)
        focus_duration = 0.5  # Default
        if PerformanceMetric.SESSION_DURATION in metrics:
            session_duration = metrics[PerformanceMetric.SESSION_DURATION]
            
            # Combine with performance consistency if available
            if 'performance_consistency' in raw_data:
                consistency = raw_data['performance_consistency']
                focus_duration = (session_duration * 0.4) + (consistency * 0.6)
            else:
                focus_duration = session_duration
        components[SkillComponent.FOCUS_DURATION] = focus_duration
        
        # Update profile components
        for component, value in components.items():
            if component in profile.components:
                # Exponential moving average
                alpha = 0.3  # Weight for new data
                profile.components[component] = (1 - alpha) * profile.components[component] + alpha * value
            else:
                profile.components[component] = value
        
        # Calculate overall skill
        if profile.components:
            # Weighted average of components
            weights = {
                SkillComponent.DECISION_MAKING: 0.25,
                SkillComponent.PATTERN_RECOGNITION: 0.15,
                SkillComponent.RISK_ASSESSMENT: 0.15,
                SkillComponent.STRATEGIC_PLANNING: 0.15,
                SkillComponent.EMOTIONAL_CONTROL: 0.1,
                SkillComponent.ADAPTABILITY: 0.1,
                SkillComponent.REACTION_TIME: 0.05,
                SkillComponent.FOCUS_DURATION: 0.05
            }
            
            total_weight = 0.0
            weighted_sum = 0.0
            
            for component, value in profile.components.items():
                weight = weights.get(component, 0.1)
                weighted_sum += value * weight
                total_weight += weight
            
            if total_weight > 0:
                profile.overall_skill = weighted_sum / total_weight
        
        # Update confidence based on data quantity
        session_count = len(raw_data.get('session_ids', [])) if 'session_ids' in raw_data else 1
        profile.confidence = min(1.0, session_count / self.config['min_sessions_for_confidence'])
        
        # Update timestamp
        profile.last_updated = int(time.time())
    
    def analyze_engagement_state(self, player_id: str, game_type: GameType, 
                               performance_profile: PlayerPerformanceProfile) -> EngagementState:
        """
        Analyze a player's current engagement state.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            performance_profile: Player's performance profile
            
        Returns:
            Current engagement state
        """
        # Not enough data
        if len(performance_profile.historical_performance) < 3:
            return EngagementState.LEARNING
        
        # Get skill profile
        skill_profile = self.get_skill_profile(player_id, game_type)
        
        # Get recent performance data
        window_size = min(self.config['engagement_window_size'], len(performance_profile.historical_performance))
        recent_performance = performance_profile.historical_performance[-window_size:]
        
        # Extract win rates
        win_rates = []
        for session in recent_performance:
            if 'metrics' in session and 'win_rate' in session['metrics']:
                win_rates.append(session['metrics']['win_rate'])
        
        # Calculate metrics
        avg_win_rate = sum(win_rates) / len(win_rates) if win_rates else 0.5
        win_rate_std_dev = np.std(win_rates) if len(win_rates) > 1 else 0.0
        
        # Calculate win rate trend
        win_rate_trend = 0.0
        if len(win_rates) >= 3:
            # Simple linear regression
            x = np.array(range(len(win_rates)))
            y = np.array(win_rates)
            
            # Calculate slope
            n = len(x)
            win_rate_trend = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x * x) - np.sum(x) ** 2)
        
        # Check for boredom (consistently high win rate)
        if avg_win_rate > self.config['boredom_win_rate'] and win_rate_std_dev < self.config['consistency_threshold']:
            return EngagementState.BORED
        
        # Check for frustration (consistently low win rate)
        if avg_win_rate < self.config['frustration_win_rate'] and win_rate_std_dev < self.config['consistency_threshold']:
            return EngagementState.FRUSTRATED
        
        # Check for mastery (high skill level and consistent performance)
        if skill_profile.overall_skill > self.config['mastery_threshold'] and win_rate_std_dev < self.config['consistency_threshold']:
            return EngagementState.MASTERY
        
        # Check for learning (improving win rate)
        if win_rate_trend > self.config['learning_rate_threshold']:
            return EngagementState.LEARNING
        
        # Check for declining (decreasing win rate)
        if win_rate_trend < -self.config['learning_rate_threshold']:
            return EngagementState.DECLINING
        
        # Check for inconsistency (high standard deviation)
        if win_rate_std_dev > self.config['consistency_threshold'] * 2:
            return EngagementState.INCONSISTENT
        
        # Check for experimenting (moderate standard deviation with varied strategies)
        if win_rate_std_dev > self.config['consistency_threshold']:
            # Check if strategy complexity is changing
            strategy_complexity_values = []
            for session in recent_performance:
                if 'metrics' in session and 'strategy_complexity' in session['metrics']:
                    strategy_complexity_values.append(session['metrics']['strategy_complexity'])
            
            if strategy_complexity_values and np.std(strategy_complexity_values) > 0.1:
                return EngagementState.EXPERIMENTING
        
        # Default to flow state
        return EngagementState.FLOW
    
    def get_learning_curve_analysis(self, player_id: str, game_type: GameType) -> Dict[str, Any]:
        """
        Analyze a player's learning curve over time.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            
        Returns:
            Learning curve analysis results
        """
        # Get profiles
        if player_id not in self.skill_profiles or game_type not in self.skill_profiles[player_id]:
            return {
                'status': 'no_data',
                'message': 'No skill profile data available for this player and game'
            }
        
        skill_profile = self.skill_profiles[player_id][game_type]
        
        # Not enough confidence
        if skill_profile.confidence < 0.5:
            return {
                'status': 'insufficient_data',
                'message': 'Not enough data for reliable learning curve analysis',
                'confidence': skill_profile.confidence
            }
        
        # Get performance profile data
        if player_id not in self.player_profiles or game_type not in self.player_profiles[player_id]:
            return {
                'status': 'no_performance_data',
                'message': 'No performance data available for learning curve analysis'
            }
        
        performance_profile = self.player_profiles[player_id][game_type]
        
        # Not enough historical data
        if len(performance_profile.historical_performance) < 5:
            return {
                'status': 'insufficient_history',
                'message': 'Not enough historical performance data for learning curve analysis',
                'sessions_available': len(performance_profile.historical_performance)
            }
        
        # Extract win rates over time
        timestamps = []
        win_rates = []
        skill_components = {component: [] for component in SkillComponent}
        
        for session in performance_profile.historical_performance:
            if 'timestamp' in session and 'metrics' in session and 'win_rate' in session['metrics']:
                timestamps.append(session['timestamp'])
                win_rates.append(session['metrics']['win_rate'])
        
        # Calculate learning rate
        learning_rate = 0.0
        plateau_detected = False
        learning_phase_end = None
        
        if len(win_rates) >= 5:
            # Segment the win rate data
            segments = []
            segment_size = min(5, len(win_rates) // 3)
            
            for i in range(0, len(win_rates), segment_size):
                segment = win_rates[i:i+segment_size]
                if segment:
                    segments.append(sum(segment) / len(segment))
            
            # Calculate learning rate from first to last segment
            if len(segments) >= 2:
                learning_rate = (segments[-1] - segments[0]) / len(segments)
            
            # Detect plateau
            if len(segments) >= 3:
                # Check if recent segments have flattened
                recent_slope = (segments[-1] - segments[-2]) / (segments[-2] - segments[-3])
                plateau_detected = abs(recent_slope) < 0.1
                
                if plateau_detected:
                    # Estimate when learning phase ended
                    for i in range(len(segments) - 2, 0, -1):
                        if abs(segments[i] - segments[i-1]) > 0.05:
                            learning_phase_end = timestamps[i * segment_size]
                            break
        
        # Calculate skill acquisition rate for each component
        skill_acquisition_rates = {}
        for component in skill_profile.components:
            # We don't have historical component data, so estimate from current value
            current_value = skill_profile.components[component]
            
            # Estimate initial value (assume started at 0.3 for most components)
            initial_value = 0.3
            
            # Calculate sessions needed to reach current value
            sessions_count = len(performance_profile.historical_performance)
            
            if sessions_count > 0:
                # Simple linear model
                skill_acquisition_rates[component.value] = (current_value - initial_value) / sessions_count
        
        # Determine learning style
        learning_style = "balanced"
        if skill_profile.components:
            # Check which components improved fastest
            fastest_components = []
            slowest_components = []
            
            if SkillComponent.REACTION_TIME in skill_profile.components and skill_profile.components[SkillComponent.REACTION_TIME] > 0.7:
                fastest_components.append("reaction_time")
            
            if SkillComponent.PATTERN_RECOGNITION in skill_profile.components and skill_profile.components[SkillComponent.PATTERN_RECOGNITION] > 0.7:
                fastest_components.append("pattern_recognition")
            
            if SkillComponent.STRATEGIC_PLANNING in skill_profile.components and skill_profile.components[SkillComponent.STRATEGIC_PLANNING] > 0.7:
                fastest_components.append("strategic_planning")
            
            # Determine style based on strengths
            if "reaction_time" in fastest_components and "pattern_recognition" in fastest_components:
                learning_style = "intuitive"
            elif "strategic_planning" in fastest_components:
                learning_style = "analytical"
            elif "pattern_recognition" in fastest_components:
                learning_style = "pattern-based"
        
        # Estimate time to mastery
        time_to_mastery = None
        if not plateau_detected and learning_rate > 0:
            current_win_rate = win_rates[-1] if win_rates else 0.5
            target_win_rate = 0.65  # Approximate win rate for mastery
            
            if current_win_rate < target_win_rate:
                # Estimate sessions needed
                sessions_needed = (target_win_rate - current_win_rate) / learning_rate
                
                # Convert to time estimate (assume 1 session per day)
                time_to_mastery = int(sessions_needed)
        
        return {
            'status': 'success',
            'learning_rate': learning_rate,
            'plateau_detected': plateau_detected,
            'learning_phase_end': learning_phase_end,
            'skill_acquisition_rates': skill_acquisition_rates,
            'learning_style': learning_style,
            'time_to_mastery': time_to_mastery,
            'current_skill_level': skill_profile.overall_skill,
            'confidence': skill_profile.confidence,
            'engagement_state': self.analyze_engagement_state(player_id, game_type, performance_profile).value
        }
    
    def get_difficulty_recommendation(self, player_id: str, game_type: GameType) -> Dict[str, Any]:
        """
        Get a personalized difficulty recommendation for a player.
        
        Args:
            player_id: ID of the player
            game_type: Type of game
            
        Returns:
            Difficulty recommendation
        """
        # Get profiles
        if player_id not in self.skill_profiles or game_type not in self.skill_profiles[player_id]:
            return {
                'status': 'no_data',
                'message': 'No skill profile data available for this player and game',
                'recommended_difficulty': DifficultyLevel.MEDIUM.value
            }
        
        skill_profile = self.skill_profiles[player_id][game_type]
        
        # Get performance profile
        if player_id not in self.player_profiles or game_type not in self.player_profiles[player_id]:
            return {
                'status': 'no_performance_data',
                'message': 'No performance data available for difficulty recommendation',
                'recommended_difficulty': DifficultyLevel.MEDIUM.value
            }
        
        performance_profile = self.player_profiles[player_id][game_type]
        
        # Analyze engagement state
        engagement_state = self.analyze_engagement_state(player_id, game_type, performance_profile)
        
        # Calculate base difficulty from skill level
        skill_level = skill_profile.overall_skill
        base_difficulty = skill_level * 6.0  # Convert 0-1 skill to 0-6 difficulty
        
        # Adjust based on engagement state
        adjustment = 0.0
        reason = f"Base difficulty {base_difficulty:.1f} from skill level {skill_level:.2f}"
        
        if engagement_state == EngagementState.BORED:
            adjustment = 1.0
            reason += ", increased due to player boredom"
        elif engagement_state == EngagementState.FRUSTRATED:
            adjustment = -1.0
            reason += ", decreased due to player frustration"
        elif engagement_state == EngagementState.LEARNING:
            adjustment = -0.5
            reason += ", slightly decreased to support learning"
        elif engagement_state == EngagementState.MASTERY:
            adjustment = 0.5
            reason += ", slightly increased due to player mastery"
        elif engagement_state == EngagementState.DECLINING:
            adjustment = -0.5
            reason += ", slightly decreased due to declining performance"
        
        # Calculate final difficulty
        final_difficulty = max(0.0, min(6.0, base_difficulty + adjustment))
        
        # Find closest standard difficulty level
        closest_level = DifficultyLevel(round(final_difficulty))
        
        # Get confidence level
        confidence = skill_profile.confidence
        
        return {
            'status': 'success',
            'recommended_difficulty': final_difficulty,
            'recommended_difficulty_level': closest_level.value,
            'recommended_difficulty_name': closest_level.name,
            'base_difficulty': base_difficulty,
            'adjustment': adjustment,
            'reason': reason,
            'engagement_state': engagement_state.value,
            'confidence': confidence
        }
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the performance analyzer to a file.
        
        Args:
            filepath: Path to save the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to serializable format
            state = {
                'skill_profiles': {},
                'config': self.config
            }
            
            # Serialize skill profiles
            for player_id, game_profiles in self.skill_profiles.items():
                state['skill_profiles'][player_id] = {}
                
                for game_type, profile in game_profiles.items():
                    state['skill_profiles'][player_id][game_type.value] = {
                        'player_id': profile.player_id,
                        'game_type': profile.game_type.value,
                        'components': {component.value: value for component, value in profile.components.items()},
                        'overall_skill': profile.overall_skill,
                        'confidence': profile.confidence,
                        'last_updated': profile.last_updated
                    }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving performance analyzer state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the state of the performance analyzer from a file.
        
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
            
            # Load skill profiles
            self.skill_profiles = {}
            for player_id, game_profiles_data in state.get('skill_profiles', {}).items():
                self.skill_profiles[player_id] = {}
                
                for game_type_str, profile_data in game_profiles_data.items():
                    game_type = GameType(game_type_str)
                    
                    profile = PlayerSkillProfile(
                        player_id=profile_data['player_id'],
                        game_type=game_type
                    )
                    
                    # Convert components keys from strings to enums
                    profile.components = {
                        SkillComponent(component): value 
                        for component, value in profile_data['components'].items()
                    }
                    
                    profile.overall_skill = profile_data['overall_skill']
                    profile.confidence = profile_data['confidence']
                    profile.last_updated = profile_data['last_updated']
                    
                    self.skill_profiles[player_id][game_type] = profile
            
            return True
        
        except Exception as e:
            print(f"Error loading performance analyzer state: {e}")
            return False
