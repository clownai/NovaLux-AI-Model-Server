"""
Adaptive Difficulty API Module

This module provides a REST API for the adaptive difficulty system, allowing game clients
to interact with the system for real-time difficulty adjustments and player performance tracking.

The API handles:
- Session initialization and tracking
- Performance data submission
- Difficulty level requests
- Player profile queries
- Analytics and insights
"""

from typing import Dict, List, Any, Optional
import json
import time
import uuid
from fastapi import FastAPI, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field

from core.adaptive_difficulty import (
    AdaptiveDifficultySystem, GameType, DifficultyLevel,
    PerformanceMetric, AdaptationTrigger, PlayerPerformanceProfile
)
from analysis.performance_analyzer import (
    PerformanceAnalyzer, EngagementState, SkillComponent
)
from config.parameter_configurator import GameParameterConfigurator


# Initialize the adaptive difficulty system components
difficulty_system = AdaptiveDifficultySystem()
performance_analyzer = PerformanceAnalyzer()
parameter_configurator = GameParameterConfigurator()

# Create FastAPI app
app = FastAPI(
    title="NovaLux Adaptive Difficulty API",
    description="API for dynamic difficulty adjustment based on player performance",
    version="1.0.0"
)


# Pydantic models for request/response validation
class SessionInitRequest(BaseModel):
    player_id: str = Field(..., description="Unique identifier for the player")
    game_type: str = Field(..., description="Type of game being played")
    client_info: Dict[str, Any] = Field(default={}, description="Client information")


class SessionInitResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the game session")
    difficulty_level: float = Field(..., description="Initial difficulty level (0-6 scale)")
    difficulty_name: str = Field(..., description="Difficulty level name")
    parameters: Dict[str, float] = Field(..., description="Game parameters for this difficulty")
    player_info: Dict[str, Any] = Field(..., description="Player profile information")


class PerformanceDataRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    player_id: str = Field(..., description="Player identifier")
    game_type: str = Field(..., description="Type of game")
    raw_data: Dict[str, Any] = Field(..., description="Raw game performance data")
    metrics: Optional[Dict[str, float]] = Field(default=None, description="Pre-calculated performance metrics (optional)")
    outcome: Dict[str, Any] = Field(..., description="Session outcome data")


class PerformanceDataResponse(BaseModel):
    success: bool = Field(..., description="Whether the data was successfully processed")
    metrics: Dict[str, float] = Field(..., description="Processed performance metrics")
    engagement_state: str = Field(..., description="Current player engagement state")
    next_difficulty: Optional[float] = Field(default=None, description="Recommended next difficulty level")


class DifficultyRequest(BaseModel):
    player_id: str = Field(..., description="Player identifier")
    game_type: str = Field(..., description="Type of game")
    session_id: Optional[str] = Field(default=None, description="Session identifier (optional)")
    explicit_difficulty: Optional[float] = Field(default=None, description="Explicitly requested difficulty (0-6 scale, optional)")


class DifficultyResponse(BaseModel):
    difficulty_level: float = Field(..., description="Difficulty level (0-6 scale)")
    difficulty_name: str = Field(..., description="Difficulty level name")
    parameters: Dict[str, float] = Field(..., description="Game parameters for this difficulty")
    adaptation_reason: Optional[str] = Field(default=None, description="Reason for difficulty adaptation")


class PlayerProfileResponse(BaseModel):
    player_id: str = Field(..., description="Player identifier")
    game_type: str = Field(..., description="Type of game")
    current_difficulty: float = Field(..., description="Current difficulty level")
    optimal_difficulty: Optional[float] = Field(default=None, description="Optimal difficulty level")
    skill_level: float = Field(..., description="Overall skill level (0-1 scale)")
    engagement_state: str = Field(..., description="Current engagement state")
    metrics: Dict[str, float] = Field(..., description="Performance metrics")
    skill_components: Dict[str, float] = Field(..., description="Skill component breakdown")
    learning_curve: Dict[str, Any] = Field(..., description="Learning curve analysis")
    adaptation_history: List[Dict[str, Any]] = Field(..., description="Recent difficulty adaptations")


class AnalyticsResponse(BaseModel):
    difficulty_distribution: Dict[str, Any] = Field(..., description="Distribution of difficulty levels")
    engagement_distribution: Dict[str, Any] = Field(..., description="Distribution of engagement states")
    skill_distribution: Dict[str, Any] = Field(..., description="Distribution of skill levels")
    adaptation_stats: Dict[str, Any] = Field(..., description="Statistics about difficulty adaptations")


# Helper functions
def get_game_type_enum(game_type_str: str) -> GameType:
    """Convert game type string to enum."""
    try:
        return GameType(game_type_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid game type: {game_type_str}")


def get_difficulty_level_enum(difficulty_value: float) -> DifficultyLevel:
    """Convert difficulty value to closest enum."""
    difficulty_value = max(0.0, min(6.0, difficulty_value))
    return DifficultyLevel(round(difficulty_value))


def convert_metrics_dict(metrics_dict: Dict[str, float]) -> Dict[PerformanceMetric, float]:
    """Convert string metric keys to enum keys."""
    result = {}
    for key_str, value in metrics_dict.items():
        try:
            key_enum = PerformanceMetric(key_str)
            result[key_enum] = value
        except ValueError:
            # Skip invalid metrics
            pass
    return result


# API routes
@app.post("/sessions/init", response_model=SessionInitResponse)
async def initialize_session(request: SessionInitRequest):
    """Initialize a new game session with appropriate difficulty level."""
    try:
        # Convert game type string to enum
        game_type = get_game_type_enum(request.game_type)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Get player profile
        player_profile = difficulty_system.get_player_profile(request.player_id, game_type)
        
        # Get skill profile if available
        skill_profile = None
        if hasattr(performance_analyzer, 'get_skill_profile'):
            skill_profile = performance_analyzer.get_skill_profile(request.player_id, game_type)
        
        # Get difficulty recommendation
        difficulty_recommendation = None
        if hasattr(performance_analyzer, 'get_difficulty_recommendation'):
            difficulty_recommendation = performance_analyzer.get_difficulty_recommendation(
                request.player_id, game_type
            )
        
        # Determine initial difficulty
        if difficulty_recommendation and difficulty_recommendation.get('status') == 'success':
            difficulty_level = difficulty_recommendation.get('recommended_difficulty', player_profile.current_difficulty)
        else:
            difficulty_level = player_profile.current_difficulty
        
        # Get difficulty name
        difficulty_enum = get_difficulty_level_enum(difficulty_level)
        difficulty_name = difficulty_enum.name
        
        # Get game parameters
        parameters = difficulty_system.get_game_parameters(
            request.player_id, game_type, session_id
        )
        
        # Prepare player info
        player_info = {
            "current_difficulty": player_profile.current_difficulty,
            "optimal_difficulty": player_profile.optimal_difficulty,
            "metrics": {k.value: v for k, v in player_profile.metrics.items()},
            "sessions_count": len(player_profile.historical_performance),
        }
        
        # Add skill info if available
        if skill_profile:
            player_info["skill_level"] = skill_profile.overall_skill
            player_info["skill_confidence"] = skill_profile.confidence
            player_info["skill_components"] = {k.value: v for k, v in skill_profile.components.items()}
        
        # Add engagement state if available
        if hasattr(performance_analyzer, 'analyze_engagement_state'):
            engagement_state = performance_analyzer.analyze_engagement_state(
                request.player_id, game_type, player_profile
            )
            player_info["engagement_state"] = engagement_state.value
        
        return SessionInitResponse(
            session_id=session_id,
            difficulty_level=difficulty_level,
            difficulty_name=difficulty_name,
            parameters=parameters,
            player_info=player_info
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing session: {str(e)}")


@app.post("/performance/submit", response_model=PerformanceDataResponse)
async def submit_performance_data(request: PerformanceDataRequest):
    """Submit performance data from a game session."""
    try:
        # Convert game type string to enum
        game_type = get_game_type_enum(request.game_type)
        
        # Process metrics if not provided
        metrics = {}
        if request.metrics:
            # Convert string keys to enum keys
            metrics = convert_metrics_dict(request.metrics)
        else:
            # Analyze raw data to extract metrics
            metrics = performance_analyzer.analyze_raw_game_data(
                request.player_id, game_type, request.session_id, request.raw_data
            )
        
        # Record performance data
        difficulty_system.record_performance(
            request.player_id, game_type, request.session_id, metrics, request.outcome
        )
        
        # Get player profile
        player_profile = difficulty_system.get_player_profile(request.player_id, game_type)
        
        # Analyze engagement state
        engagement_state = performance_analyzer.analyze_engagement_state(
            request.player_id, game_type, player_profile
        )
        
        # Determine if difficulty should be adapted
        should_adapt, trigger = difficulty_system._should_adapt_difficulty(player_profile, request.session_id)
        
        # Calculate next difficulty if needed
        next_difficulty = None
        if should_adapt:
            next_difficulty = difficulty_system._calculate_optimal_difficulty(player_profile)
        
        return PerformanceDataResponse(
            success=True,
            metrics={k.value: v for k, v in metrics.items()},
            engagement_state=engagement_state.value,
            next_difficulty=next_difficulty
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing performance data: {str(e)}")


@app.post("/difficulty/get", response_model=DifficultyResponse)
async def get_difficulty(request: DifficultyRequest):
    """Get difficulty parameters for a player."""
    try:
        # Convert game type string to enum
        game_type = get_game_type_enum(request.game_type)
        
        # Handle explicit difficulty request
        if request.explicit_difficulty is not None:
            # Set difficulty directly
            parameters = difficulty_system.set_difficulty_directly(
                request.player_id, game_type, request.explicit_difficulty
            )
            
            difficulty_level = request.explicit_difficulty
            difficulty_enum = get_difficulty_level_enum(difficulty_level)
            
            return DifficultyResponse(
                difficulty_level=difficulty_level,
                difficulty_name=difficulty_enum.name,
                parameters=parameters,
                adaptation_reason="Explicit difficulty selection"
            )
        
        # Get game parameters based on player profile
        parameters = difficulty_system.get_game_parameters(
            request.player_id, game_type, request.session_id
        )
        
        # Get player profile
        player_profile = difficulty_system.get_player_profile(request.player_id, game_type)
        
        # Get difficulty level and name
        difficulty_level = player_profile.current_difficulty
        difficulty_enum = get_difficulty_level_enum(difficulty_level)
        
        # Get adaptation reason from history if available
        adaptation_reason = None
        if player_profile.adaptation_history:
            latest_adaptation = player_profile.adaptation_history[-1]
            adaptation_reason = latest_adaptation.get('reason')
        
        return DifficultyResponse(
            difficulty_level=difficulty_level,
            difficulty_name=difficulty_enum.name,
            parameters=parameters,
            adaptation_reason=adaptation_reason
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting difficulty: {str(e)}")


@app.get("/players/{player_id}/profile", response_model=PlayerProfileResponse)
async def get_player_profile(
    player_id: str,
    game_type: str = Query(..., description="Type of game")
):
    """Get detailed profile information for a player."""
    try:
        # Convert game type string to enum
        game_type_enum = get_game_type_enum(game_type)
        
        # Get player performance profile
        player_profile = difficulty_system.get_player_profile(player_id, game_type_enum)
        
        # Get skill profile
        skill_profile = performance_analyzer.get_skill_profile(player_id, game_type_enum)
        
        # Get learning curve analysis
        learning_curve = performance_analyzer.get_learning_curve_analysis(player_id, game_type_enum)
        
        # Get engagement state
        engagement_state = performance_analyzer.analyze_engagement_state(
            player_id, game_type_enum, player_profile
        )
        
        return PlayerProfileResponse(
            player_id=player_id,
            game_type=game_type,
            current_difficulty=player_profile.current_difficulty,
            optimal_difficulty=player_profile.optimal_difficulty,
            skill_level=skill_profile.overall_skill,
            engagement_state=engagement_state.value,
            metrics={k.value: v for k, v in player_profile.metrics.items()},
            skill_components={k.value: v for k, v in skill_profile.components.items()},
            learning_curve=learning_curve,
            adaptation_history=player_profile.adaptation_history[-10:] if player_profile.adaptation_history else []
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting player profile: {str(e)}")


@app.get("/analytics/system", response_model=AnalyticsResponse)
async def get_system_analytics():
    """Get system-wide analytics about difficulty distribution and adaptations."""
    try:
        # Get difficulty distribution
        difficulty_distribution = difficulty_system.get_difficulty_distribution()
        
        # Calculate engagement distribution
        engagement_distribution = {
            "status": "success",
            "counts": {},
            "percentage": {}
        }
        
        # Calculate skill distribution
        skill_distribution = {
            "status": "success",
            "average": 0.0,
            "histogram": []
        }
        
        # Calculate adaptation stats
        adaptation_stats = {
            "status": "success",
            "total_adaptations": 0,
            "adaptations_by_trigger": {},
            "average_adjustment": 0.0
        }
        
        # Process all player profiles to gather statistics
        total_players = 0
        total_adaptations = 0
        total_skill = 0.0
        engagement_counts = {state.value: 0 for state in EngagementState}
        trigger_counts = {trigger.value: 0 for trigger in AdaptationTrigger}
        total_adjustment = 0.0
        
        for player_id, game_profiles in difficulty_system.player_profiles.items():
            for game_type, profile in game_profiles.items():
                total_players += 1
                
                # Count adaptations
                if profile.adaptation_history:
                    total_adaptations += len(profile.adaptation_history)
                    
                    # Count by trigger
                    for adaptation in profile.adaptation_history:
                        trigger = adaptation.get('trigger')
                        if trigger in trigger_counts:
                            trigger_counts[trigger] += 1
                        
                        # Sum adjustment amounts
                        adjustment = adaptation.get('new_difficulty', 0) - adaptation.get('previous_difficulty', 0)
                        total_adjustment += abs(adjustment)
                
                # Get engagement state
                if hasattr(performance_analyzer, 'analyze_engagement_state'):
                    engagement_state = performance_analyzer.analyze_engagement_state(
                        player_id, game_type, profile
                    )
                    engagement_counts[engagement_state.value] += 1
                
                # Get skill level
                if player_id in performance_analyzer.skill_profiles and game_type in performance_analyzer.skill_profiles[player_id]:
                    skill_profile = performance_analyzer.skill_profiles[player_id][game_type]
                    total_skill += skill_profile.overall_skill
        
        # Calculate averages and percentages
        if total_players > 0:
            # Engagement distribution
            engagement_distribution["counts"] = engagement_counts
            engagement_distribution["percentage"] = {
                state: (count / total_players) * 100 
                for state, count in engagement_counts.items()
            }
            
            # Skill distribution
            skill_distribution["average"] = total_skill / total_players
        
        if total_adaptations > 0:
            # Adaptation stats
            adaptation_stats["total_adaptations"] = total_adaptations
            adaptation_stats["adaptations_by_trigger"] = trigger_counts
            adaptation_stats["average_adjustment"] = total_adjustment / total_adaptations
        
        return AnalyticsResponse(
            difficulty_distribution=difficulty_distribution,
            engagement_distribution=engagement_distribution,
            skill_distribution=skill_distribution,
            adaptation_stats=adaptation_stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system analytics: {str(e)}")


@app.post("/system/save")
async def save_system_state(
    filepath: str = Body(..., embed=True, description="Filepath to save state")
):
    """Save the current state of the adaptive difficulty system."""
    try:
        # Save difficulty system state
        difficulty_success = difficulty_system.save_state(filepath + ".difficulty")
        
        # Save performance analyzer state
        analyzer_success = performance_analyzer.save_state(filepath + ".analyzer")
        
        # Save parameter configurator state
        config_success = parameter_configurator.save_configurations(filepath + ".config")
        
        if difficulty_success and analyzer_success and config_success:
            return {"success": True, "message": "System state saved successfully"}
        else:
            return {
                "success": False, 
                "message": "Partial save completed", 
                "details": {
                    "difficulty_system": difficulty_success,
                    "performance_analyzer": analyzer_success,
                    "parameter_configurator": config_success
                }
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving system state: {str(e)}")


@app.post("/system/load")
async def load_system_state(
    filepath: str = Body(..., embed=True, description="Filepath to load state from")
):
    """Load the state of the adaptive difficulty system."""
    try:
        # Load difficulty system state
        difficulty_success = difficulty_system.load_state(filepath + ".difficulty")
        
        # Load performance analyzer state
        analyzer_success = performance_analyzer.load_state(filepath + ".analyzer")
        
        # Load parameter configurator state
        config_success = parameter_configurator.load_configurations(filepath + ".config")
        
        if difficulty_success and analyzer_success and config_success:
            return {"success": True, "message": "System state loaded successfully"}
        else:
            return {
                "success": False, 
                "message": "Partial load completed", 
                "details": {
                    "difficulty_system": difficulty_success,
                    "performance_analyzer": analyzer_success,
                    "parameter_configurator": config_success
                }
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading system state: {str(e)}")


# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
