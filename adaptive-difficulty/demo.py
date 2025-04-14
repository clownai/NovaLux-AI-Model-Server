"""
Adaptive Difficulty System Demo

This script demonstrates the functionality of the NovaLux adaptive difficulty system
by simulating player interactions and showing how the system adapts to different
player performance patterns.

The demo includes:
- Player session initialization
- Performance data submission
- Difficulty adaptation visualization
- Player profile analysis
- System analytics
"""

import time
import random
import uuid
import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional

from core.adaptive_difficulty import (
    AdaptiveDifficultySystem, GameType, DifficultyLevel,
    PerformanceMetric, AdaptationTrigger, PlayerPerformanceProfile
)
from analysis.performance_analyzer import (
    PerformanceAnalyzer, EngagementState, SkillComponent
)
from config.parameter_configurator import GameParameterConfigurator


class AdaptiveDifficultyDemo:
    """Demo class for showcasing the adaptive difficulty system."""
    
    def __init__(self):
        """Initialize the demo with system components."""
        self.difficulty_system = AdaptiveDifficultySystem()
        self.performance_analyzer = PerformanceAnalyzer()
        self.parameter_configurator = GameParameterConfigurator()
        
        # Demo players with different skill profiles
        self.players = {
            "novice_player": {
                "skill_level": 0.2,
                "learning_rate": 0.05,
                "consistency": 0.3,
                "risk_taking": 0.4,
                "game_types": [GameType.ECLIPSE_ROULETTE, GameType.CHAOS_SLOTS]
            },
            "average_player": {
                "skill_level": 0.5,
                "learning_rate": 0.03,
                "consistency": 0.6,
                "risk_taking": 0.5,
                "game_types": [GameType.NEURAL_HOLDEM, GameType.ECLIPSE_ROULETTE]
            },
            "expert_player": {
                "skill_level": 0.8,
                "learning_rate": 0.01,
                "consistency": 0.8,
                "risk_taking": 0.7,
                "game_types": [GameType.NEURAL_HOLDEM, GameType.CHAOS_SLOTS]
            },
            "inconsistent_player": {
                "skill_level": 0.6,
                "learning_rate": 0.02,
                "consistency": 0.2,
                "risk_taking": 0.8,
                "game_types": [GameType.ECLIPSE_ROULETTE]
            }
        }
        
        # Tracking data for visualization
        self.tracking_data = {}
    
    def run_demo(self, num_sessions: int = 30):
        """
        Run the full demo with multiple players and game types.
        
        Args:
            num_sessions: Number of sessions to simulate per player
        """
        print("=== NovaLux Adaptive Difficulty System Demo ===\n")
        
        # Initialize tracking data
        for player_id in self.players:
            self.tracking_data[player_id] = {}
            for game_type in self.players[player_id]["game_types"]:
                self.tracking_data[player_id][game_type] = {
                    "difficulties": [],
                    "win_rates": [],
                    "engagement_states": []
                }
        
        # Run simulations for each player
        for player_id, player_info in self.players.items():
            print(f"\n--- Simulating {player_id} ---")
            
            for game_type in player_info["game_types"]:
                print(f"\nGame: {game_type.value}")
                
                # Simulate sessions
                for session_num in range(1, num_sessions + 1):
                    # Simulate session
                    session_id, difficulty, parameters = self._simulate_session_start(
                        player_id, game_type
                    )
                    
                    # Simulate gameplay and performance
                    performance_data, win_rate = self._simulate_gameplay(
                        player_id, game_type, session_id, difficulty, parameters,
                        player_info, session_num, num_sessions
                    )
                    
                    # Submit performance data
                    engagement_state = self._submit_performance_data(
                        player_id, game_type, session_id, performance_data, win_rate
                    )
                    
                    # Track data for visualization
                    player_profile = self.difficulty_system.get_player_profile(player_id, game_type)
                    self.tracking_data[player_id][game_type]["difficulties"].append(player_profile.current_difficulty)
                    self.tracking_data[player_id][game_type]["win_rates"].append(win_rate)
                    self.tracking_data[player_id][game_type]["engagement_states"].append(engagement_state.value)
                    
                    # Print progress
                    if session_num % 5 == 0 or session_num == 1:
                        print(f"  Session {session_num}: Difficulty={player_profile.current_difficulty:.2f}, "
                              f"Win Rate={win_rate:.2f}, Engagement={engagement_state.value}")
                
                # Analyze player profile after all sessions
                self._analyze_player_profile(player_id, game_type)
        
        # Show system analytics
        self._show_system_analytics()
        
        # Visualize results
        self._visualize_results()
    
    def _simulate_session_start(self, player_id: str, game_type: GameType):
        """
        Simulate starting a new game session.
        
        Args:
            player_id: Player identifier
            game_type: Type of game
            
        Returns:
            Tuple of (session_id, difficulty_level, parameters)
        """
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Get game parameters based on player profile
        parameters = self.difficulty_system.get_game_parameters(
            player_id, game_type, session_id
        )
        
        # Get player profile
        player_profile = self.difficulty_system.get_player_profile(player_id, game_type)
        difficulty = player_profile.current_difficulty
        
        return session_id, difficulty, parameters
    
    def _simulate_gameplay(self, player_id: str, game_type: GameType, 
                         session_id: str, difficulty: float, parameters: Dict[str, float],
                         player_info: Dict[str, Any], session_num: int, total_sessions: int):
        """
        Simulate gameplay and generate performance data.
        
        Args:
            player_id: Player identifier
            game_type: Type of game
            session_id: Session identifier
            difficulty: Current difficulty level
            parameters: Game parameters
            player_info: Player skill information
            session_num: Current session number
            total_sessions: Total number of sessions
            
        Returns:
            Tuple of (performance_data, win_rate)
        """
        # Get base skill level
        base_skill = player_info["skill_level"]
        
        # Apply learning curve
        learning_progress = min(1.0, session_num / total_sessions)
        learning_improvement = learning_progress * player_info["learning_rate"] * 10
        current_skill = min(0.95, base_skill + learning_improvement)
        
        # Calculate win rate based on skill vs difficulty
        # Higher skill and lower difficulty = higher win rate
        normalized_difficulty = difficulty / 6.0  # Convert to 0-1 scale
        base_win_rate = max(0.1, min(0.9, current_skill - (normalized_difficulty * 0.5)))
        
        # Add randomness based on consistency
        consistency = player_info["consistency"]
        randomness = (1.0 - consistency) * 0.4  # Scale randomness
        win_rate = max(0.05, min(0.95, base_win_rate + random.uniform(-randomness, randomness)))
        
        # Generate performance metrics
        metrics = {
            PerformanceMetric.WIN_RATE: win_rate,
            PerformanceMetric.AVERAGE_BET: random.uniform(10, 100),
            PerformanceMetric.TIME_PER_DECISION: random.uniform(1, 10),
            PerformanceMetric.RISK_TAKING: player_info["risk_taking"] + random.uniform(-0.1, 0.1),
            PerformanceMetric.STRATEGY_COMPLEXITY: current_skill * 0.8 + random.uniform(-0.1, 0.1),
            PerformanceMetric.VARIANCE_TOLERANCE: player_info["risk_taking"] * 0.7 + random.uniform(-0.1, 0.1),
            PerformanceMetric.SESSION_DURATION: random.uniform(0.3, 0.8)
        }
        
        # Clamp values to valid ranges
        for key in metrics:
            metrics[key] = max(0.0, min(1.0, metrics[key]))
        
        # Generate raw data based on game type
        raw_data = self._generate_raw_game_data(game_type, win_rate, metrics, parameters)
        
        # Generate session outcome
        wins = int(win_rate * 100)
        losses = 100 - wins
        outcome = {
            "win": win_rate > 0.5,
            "wins": wins,
            "losses": losses,
            "net_gain": wins - losses,
            "session_complete": True
        }
        
        # Combine into performance data
        performance_data = {
            "raw_data": raw_data,
            "metrics": metrics,
            "outcome": outcome
        }
        
        return performance_data, win_rate
    
    def _generate_raw_game_data(self, game_type: GameType, win_rate: float, 
                              metrics: Dict[PerformanceMetric, float],
                              parameters: Dict[str, float]):
        """
        Generate simulated raw game data based on game type.
        
        Args:
            game_type: Type of game
            win_rate: Player win rate
            metrics: Performance metrics
            parameters: Game parameters
            
        Returns:
            Raw game data dictionary
        """
        # Common data
        raw_data = {
            "session_ids": [str(uuid.uuid4())],
            "timestamp": int(time.time()),
            "win_rate": win_rate,
            "session_duration": metrics[PerformanceMetric.SESSION_DURATION] * 7200  # 0-2 hours
        }
        
        # Game-specific data
        if game_type == GameType.ECLIPSE_ROULETTE:
            # Eclipse Roulette specific data
            num_bets = 100
            wins = int(win_rate * num_bets)
            
            raw_data.update({
                "bets": list(range(num_bets)),
                "wins": random.sample(range(num_bets), wins),
                "bet_amounts": [random.uniform(5, 50) for _ in range(num_bets)],
                "decision_times": [random.uniform(1, 10) for _ in range(num_bets)],
                "bet_types": random.choices(["straight", "split", "street", "corner", "line"], k=num_bets),
                "bet_patterns": [random.sample(range(37), random.randint(1, 6)) for _ in range(10)],
                "consecutive_losses": self._simulate_consecutive_events(num_bets, 1 - win_rate),
                "max_drawdown": random.uniform(0.1, 0.5)
            })
            
        elif game_type == GameType.NEURAL_HOLDEM:
            # Neural Hold'em specific data
            num_hands = 50
            hands_won = int(win_rate * num_hands)
            
            raw_data.update({
                "hands_played": list(range(num_hands)),
                "hands_won": random.sample(range(num_hands), hands_won),
                "bet_amounts": [random.uniform(10, 200) for _ in range(num_hands)],
                "decision_times": [random.uniform(2, 20) for _ in range(num_hands)],
                "bluffs": random.sample(range(num_hands), int(num_hands * metrics[PerformanceMetric.RISK_TAKING])),
                "folds": random.sample(range(num_hands), int(num_hands * (1 - metrics[PerformanceMetric.RISK_TAKING]))),
                "pot_sizes": [random.uniform(50, 1000) for _ in range(num_hands)],
                "action_sequences": [random.choices(["check", "call", "raise", "fold"], k=random.randint(1, 5)) 
                                    for _ in range(num_hands)],
                "position_actions": {"awareness_score": metrics[PerformanceMetric.STRATEGY_COMPLEXITY]},
                "hand_strength_actions": {"appropriateness_score": metrics[PerformanceMetric.STRATEGY_COMPLEXITY]},
                "stack_volatility": metrics[PerformanceMetric.VARIANCE_TOLERANCE]
            })
            
        elif game_type == GameType.CHAOS_SLOTS:
            # Chaos Slots specific data
            num_spins = 200
            wins = int(win_rate * num_spins)
            
            raw_data.update({
                "spins": list(range(num_spins)),
                "wins": random.sample(range(num_spins), wins),
                "bet_amounts": [random.uniform(1, 10) for _ in range(num_spins)],
                "feature_triggers": random.sample(range(num_spins), int(num_spins * parameters.get("feature_trigger_chance", 0.05))),
                "bet_adjustments": random.sample(range(num_spins), int(num_spins * metrics[PerformanceMetric.STRATEGY_COMPLEXITY])),
                "outcome_responses": {"score": metrics[PerformanceMetric.STRATEGY_COMPLEXITY]},
                "max_drawdown": random.uniform(0.2, 0.7),
                "max_consecutive_losses": self._simulate_consecutive_events(num_spins, 1 - win_rate),
                "days_since_last_session": random.randint(0, 10)
            })
        
        return raw_data
    
    def _simulate_consecutive_events(self, total_events: int, event_probability: float) -> int:
        """
        Simulate consecutive events (wins or losses) and return the maximum streak.
        
        Args:
            total_events: Total number of events
            event_probability: Probability of the event occurring
            
        Returns:
            Maximum consecutive streak
        """
        events = [random.random() < event_probability for _ in range(total_events)]
        max_streak = 0
        current_streak = 0
        
        for event in events:
            if event:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _submit_performance_data(self, player_id: str, game_type: GameType, 
                               session_id: str, performance_data: Dict[str, Any],
                               win_rate: float) -> EngagementState:
        """
        Submit performance data to the adaptive difficulty system.
        
        Args:
            player_id: Player identifier
            game_type: Type of game
            session_id: Session identifier
            performance_data: Performance data
            win_rate: Player win rate
            
        Returns:
            Current engagement state
        """
        # Extract components
        raw_data = performance_data["raw_data"]
        metrics = performance_data["metrics"]
        outcome = performance_data["outcome"]
        
        # Analyze raw data to extract metrics
        analyzed_metrics = self.performance_analyzer.analyze_raw_game_data(
            player_id, game_type, session_id, raw_data
        )
        
        # Record performance data
        self.difficulty_system.record_performance(
            player_id, game_type, session_id, analyzed_metrics, outcome
        )
        
        # Get player profile
        player_profile = self.difficulty_system.get_player_profile(player_id, game_type)
        
        # Analyze engagement state
        engagement_state = self.performance_analyzer.analyze_engagement_state(
            player_id, game_type, player_profile
        )
        
        return engagement_state
    
    def _analyze_player_profile(self, player_id: str, game_type: GameType):
        """
        Analyze and print player profile information.
        
        Args:
            player_id: Player identifier
            game_type: Type of game
        """
        # Get player performance profile
        player_profile = self.difficulty_system.get_player_profile(player_id, game_type)
        
        # Get skill profile
        skill_profile = self.performance_analyzer.get_skill_profile(player_id, game_type)
        
        # Get learning curve analysis
        learning_curve = self.performance_analyzer.get_learning_curve_analysis(player_id, game_type)
        
        # Get engagement state
        engagement_state = self.performance_analyzer.analyze_engagement_state(
            player_id, game_type, player_profile
        )
        
        # Get difficulty recommendation
        difficulty_recommendation = self.performance_analyzer.get_difficulty_recommendation(
            player_id, game_type
        )
        
        # Print analysis
        print(f"\n  Player Profile Analysis for {player_id} in {game_type.value}:")
        print(f"  - Final Difficulty: {player_profile.current_difficulty:.2f}")
        print(f"  - Optimal Difficulty: {player_profile.optimal_difficulty if player_profile.optimal_difficulty else 'Not determined'}")
        print(f"  - Skill Level: {skill_profile.overall_skill:.2f}")
        print(f"  - Engagement State: {engagement_state.value}")
        
        if learning_curve.get("status") == "success":
            print(f"  - Learning Rate: {learning_curve.get('learning_rate', 0):.3f}")
            print(f"  - Learning Style: {learning_curve.get('learning_style', 'unknown')}")
            print(f"  - Plateau Detected: {learning_curve.get('plateau_detected', False)}")
        
        if difficulty_recommendation.get("status") == "success":
            print(f"  - Recommended Difficulty: {difficulty_recommendation.get('recommended_difficulty', 0):.2f}")
            print(f"  - Recommendation Reason: {difficulty_recommendation.get('reason', 'unknown')}")
    
    def _show_system_analytics(self):
        """Show system-wide analytics about difficulty distribution and adaptations."""
        print("\n=== System Analytics ===")
        
        # Get difficulty distribution
        difficulty_distribution = self.difficulty_system.get_difficulty_distribution()
        
        if difficulty_distribution.get("status") == "success":
            print("\nDifficulty Distribution:")
            print(f"  - Average Difficulty: {difficulty_distribution['overall']['average']:.2f}")
            print(f"  - Median Difficulty: {difficulty_distribution['overall']['median']:.2f}")
            print(f"  - Range: {difficulty_distribution['overall']['min']:.2f} - {difficulty_distribution['overall']['max']:.2f}")
            
            print("\nDifficulty by Game Type:")
            for game_type, stats in difficulty_distribution.get("by_game", {}).items():
                print(f"  - {game_type}: Avg={stats['average']:.2f}, Count={stats['count']}")
        
        # Count adaptations
        total_adaptations = 0
        adaptations_by_trigger = {}
        
        for player_id, game_profiles in self.difficulty_system.player_profiles.items():
            for game_type, profile in game_profiles.items():
                if profile.adaptation_history:
                    total_adaptations += len(profile.adaptation_history)
                    
                    # Count by trigger
                    for adaptation in profile.adaptation_history:
                        trigger = adaptation.get('trigger')
                        if trigger in adaptations_by_trigger:
                            adaptations_by_trigger[trigger] += 1
                        else:
                            adaptations_by_trigger[trigger] = 1
        
        print(f"\nTotal Adaptations: {total_adaptations}")
        if adaptations_by_trigger:
            print("Adaptations by Trigger:")
            for trigger, count in adaptations_by_trigger.items():
                print(f"  - {trigger}: {count} ({count/total_adaptations*100:.1f}%)")
    
    def _visualize_results(self):
        """Visualize the results of the simulation."""
        # Create figure with subplots
        fig, axs = plt.subplots(len(self.players), 2, figsize=(15, 4 * len(self.players)))
        
        # Flatten axs if there's only one player
        if len(self.players) == 1:
            axs = [axs]
        
        # Plot data for each player
        for i, (player_id, player_data) in enumerate(self.tracking_data.items()):
            # Skip if no data
            if not player_data:
                continue
            
            # Get first game type for this player
            game_type = list(player_data.keys())[0]
            data = player_data[game_type]
            
            # Plot difficulty over time
            axs[i][0].plot(data["difficulties"], 'b-', label='Difficulty')
            axs[i][0].set_title(f"{player_id} - {game_type.value} - Difficulty")
            axs[i][0].set_xlabel("Session")
            axs[i][0].set_ylabel("Difficulty (0-6)")
            axs[i][0].set_ylim(0, 6)
            axs[i][0].grid(True)
            
            # Plot win rate over time
            axs[i][1].plot(data["win_rates"], 'g-', label='Win Rate')
            axs[i][1].set_title(f"{player_id} - {game_type.value} - Win Rate")
            axs[i][1].set_xlabel("Session")
            axs[i][1].set_ylabel("Win Rate")
            axs[i][1].set_ylim(0, 1)
            axs[i][1].grid(True)
            
            # Add engagement state markers
            engagement_colors = {
                "flow": "g",
                "bored": "b",
                "frustrated": "r",
                "learning": "c",
                "mastery": "m",
                "experimenting": "y",
                "declining": "k",
                "inconsistent": "orange"
            }
            
            for j, state in enumerate(data["engagement_states"]):
                color = engagement_colors.get(state, "gray")
                axs[i][1].axvline(x=j, color=color, alpha=0.2)
            
            # Add legend for engagement states
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color=color, lw=4, label=state)
                for state, color in engagement_colors.items()
                if state in data["engagement_states"]
            ]
            axs[i][1].legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig("adaptive_difficulty_demo_results.png")
        print("\nVisualization saved to 'adaptive_difficulty_demo_results.png'")


if __name__ == "__main__":
    demo = AdaptiveDifficultyDemo()
    demo.run_demo(num_sessions=30)
