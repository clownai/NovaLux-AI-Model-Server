"""
Demo Script for Procedural Content Generation

This script demonstrates the procedural content generation system by creating
various types of content and showing how they adapt to player preferences.

The demo includes:
- Player profile creation and preference management
- Quest generation with personalization
- Environment generation with faction dynamics
- Character generation with relationships
- Content evaluation and selection
"""

import os
import json
import time
import random
from typing import Dict, List, Any

from core.procedural_content import (
    ContentType, ContentComplexity, ContentTheme, ContentTone, ContentFaction,
    GenerationStrategy, PlayerPreferenceProfile
)

from generators.quest_generator import QuestType
from generators.environment_generator import EnvironmentType
from generators.character_generator import CharacterRole, RelationshipType

from integration import ContentGenerationAPI


def create_data_directory():
    """Create data directory structure for templates and state."""
    os.makedirs("data/templates", exist_ok=True)
    os.makedirs("data/state", exist_ok=True)


def create_sample_templates():
    """Create sample templates for demonstration."""
    # Quest template
    quest_template = {
        "id": "cyberpunk_heist_quest",
        "name": "Corporate Data Heist",
        "content_type": "quest",
        "description": "Infiltrate a corporate facility to steal valuable data",
        "complexity": 3,
        "themes": ["cyberpunk", "noir", "technological"],
        "tones": ["tense", "mysterious"],
        "factions": ["hackers", "corporate"],
        "tags": ["heist", "stealth", "hacking"],
        "template_data": {
            "structure": {
                "name": "$var:quest_name",
                "description": "$var:quest_description",
                "quest_type": "$var:quest_type",
                "objectives": "$generate:3:objective",
                "steps": "$generate:$var:step_count:step",
                "rewards": "$generate:2:reward",
                "difficulty": "$var:difficulty",
                "time_limit": "$var:time_limit",
                "faction": "$var:faction"
            },
            "variables": {
                "quest_name": "Data Breach: $var:target_name",
                "quest_description": "Infiltrate $var:target_name and extract valuable data without being detected.",
                "quest_type": "side",
                "step_count": "$range:3,5",
                "difficulty": 3,
                "time_limit": "$range:1800,3600",
                "faction": "hackers",
                "target_name": "$random:NeoTech Industries,Arasaka Tower,MiliTech Research,Biotechnica Labs"
            },
            "content_blocks": {
                "objective": [
                    {
                        "description": "Infiltrate the $var:target_name facility",
                        "type": "reach",
                        "target": "$var:target_name security entrance",
                        "completion_criteria": "Player reaches the designated area"
                    },
                    {
                        "description": "Hack the security system",
                        "type": "hack",
                        "target": "$var:target_name security mainframe",
                        "completion_criteria": "Player successfully completes hacking minigame"
                    },
                    {
                        "description": "Download the confidential data",
                        "type": "interact",
                        "target": "Secure server room terminal",
                        "completion_criteria": "Player interacts with the terminal and waits for download"
                    },
                    {
                        "description": "Escape without raising the alarm",
                        "type": "reach",
                        "target": "Extraction point",
                        "completion_criteria": "Player reaches extraction point with stealth meter below threshold"
                    }
                ],
                "step": [
                    {
                        "step_number": 1,
                        "description": "Meet your fixer at the Night City bar to get the details",
                        "location": "Downtown Night City",
                        "npc": "Rogue Amendiares"
                    },
                    {
                        "step_number": 2,
                        "description": "Acquire the security keycard from a corporate employee",
                        "location": "Corporate Residential District",
                        "npc": "Corporate Middle Manager"
                    },
                    {
                        "step_number": 3,
                        "description": "Infiltrate the facility using the service entrance",
                        "location": "$var:target_name",
                        "npc": null
                    },
                    {
                        "step_number": 4,
                        "description": "Hack the security system to disable cameras",
                        "location": "$var:target_name",
                        "npc": null
                    },
                    {
                        "step_number": 5,
                        "description": "Download the data from the secure server",
                        "location": "$var:target_name",
                        "npc": null
                    },
                    {
                        "step_number": 6,
                        "description": "Escape and deliver the data to your fixer",
                        "location": "Downtown Night City",
                        "npc": "Rogue Amendiares"
                    }
                ],
                "reward": [
                    {
                        "type": "currency",
                        "name": "Eurodollars",
                        "amount": "$range:1000,5000",
                        "description": "Payment for the job"
                    },
                    {
                        "type": "item",
                        "name": "Militech Cyberdeck",
                        "quality": "rare",
                        "description": "Advanced cyberdeck with enhanced hacking capabilities"
                    },
                    {
                        "type": "reputation",
                        "faction": "hackers",
                        "amount": "$range:10,25",
                        "description": "Increased standing with the hacker community"
                    }
                ]
            }
        }
    }
    
    # Environment template
    environment_template = {
        "id": "night_city_district",
        "name": "Night City District",
        "content_type": "environment",
        "description": "A procedurally generated district in Night City",
        "complexity": 4,
        "themes": ["cyberpunk", "dystopian", "technological"],
        "tones": ["dark", "tense"],
        "factions": ["corporate", "underground", "hackers"],
        "tags": ["urban", "city", "night"],
        "template_data": {
            "structure": {
                "name": "$var:district_name",
                "description": "$var:district_description",
                "environment_type": "$var:environment_type",
                "controlling_faction": "$var:controlling_faction",
                "state": "$var:district_state",
                "features": "$generate:$var:feature_count:feature",
                "points_of_interest": "$generate:$var:poi_count:poi",
                "npcs": "$generate:$var:npc_count:npc",
                "resources": {
                    "credits": "$var:credit_resources",
                    "tech_parts": "$var:tech_resources",
                    "black_market_goods": "$var:black_market_resources"
                }
            },
            "variables": {
                "district_name": "$random:Watson,Westbrook,Heywood,Pacifica,Santo Domingo,City Center",
                "district_description": "A bustling district in Night City, known for $var:district_feature",
                "district_feature": "$random:its corporate towers,the underground clubs,black market activity,gang warfare,luxury apartments,tech startups",
                "environment_type": "urban",
                "controlling_faction": "$random:corporate,underground,hackers,outcasts",
                "district_state": "$random:peaceful,tense,conflict,celebration",
                "feature_count": "$range:3,6",
                "poi_count": "$range:4,8",
                "npc_count": "$range:5,10",
                "credit_resources": "$range:5000,20000",
                "tech_resources": "$range:100,500",
                "black_market_resources": "$range:50,200"
            },
            "content_blocks": {
                "feature": [
                    {
                        "name": "Corporate Plaza",
                        "description": "A large open plaza surrounded by corporate towers",
                        "type": "landmark",
                        "faction_presence": "corporate",
                        "security_level": "high"
                    },
                    {
                        "name": "Underground Market",
                        "description": "A hidden marketplace selling illegal goods and services",
                        "type": "black_market",
                        "faction_presence": "underground",
                        "security_level": "low"
                    },
                    {
                        "name": "Netrunner Den",
                        "description": "A hideout for hackers and netrunners",
                        "type": "hidden_area",
                        "faction_presence": "hackers",
                        "security_level": "moderate"
                    },
                    {
                        "name": "Surveillance Network",
                        "description": "An extensive network of cameras and drones",
                        "type": "security_systems",
                        "faction_presence": "corporate",
                        "security_level": "very_high"
                    },
                    {
                        "name": "Nightclub District",
                        "description": "A strip of popular nightclubs and bars",
                        "type": "entertainment",
                        "faction_presence": "neutral",
                        "security_level": "moderate"
                    },
                    {
                        "name": "Restricted Zone",
                        "description": "A cordoned-off area with restricted access",
                        "type": "restricted_access",
                        "faction_presence": "corporate",
                        "security_level": "very_high"
                    }
                ],
                "poi": [
                    {
                        "name": "The Afterlife",
                        "description": "Legendary mercenary bar and gathering place",
                        "type": "bar",
                        "faction": "neutral",
                        "importance": "high"
                    },
                    {
                        "name": "Arasaka Tower",
                        "description": "Headquarters of the Arasaka Corporation",
                        "type": "corporate",
                        "faction": "corporate",
                        "importance": "very_high"
                    },
                    {
                        "name": "Lizzie's Bar",
                        "description": "Popular nightclub with underground connections",
                        "type": "nightclub",
                        "faction": "underground",
                        "importance": "moderate"
                    },
                    {
                        "name": "Kabuki Market",
                        "description": "Bustling market with various vendors",
                        "type": "market",
                        "faction": "neutral",
                        "importance": "moderate"
                    },
                    {
                        "name": "Netrunner Collective",
                        "description": "Secret meeting place for elite hackers",
                        "type": "hidden",
                        "faction": "hackers",
                        "importance": "high"
                    },
                    {
                        "name": "Megabuilding H10",
                        "description": "Massive residential complex housing thousands",
                        "type": "residential",
                        "faction": "neutral",
                        "importance": "moderate"
                    }
                ],
                "npc": [
                    {
                        "name": "Jackie Welles",
                        "description": "Loyal mercenary and fixer",
                        "role": "fixer",
                        "faction": "neutral",
                        "traits": ["loyal", "ambitious", "charismatic"]
                    },
                    {
                        "name": "Rogue Amendiares",
                        "description": "Legendary fixer and former mercenary",
                        "role": "fixer",
                        "faction": "neutral",
                        "traits": ["cunning", "disciplined", "mysterious"]
                    },
                    {
                        "name": "Meredith Stout",
                        "description": "Corporate agent with a ruthless streak",
                        "role": "corporate",
                        "faction": "corporate",
                        "traits": ["ambitious", "ruthless", "disciplined"]
                    },
                    {
                        "name": "T-Bug",
                        "description": "Skilled netrunner for hire",
                        "role": "hacker",
                        "faction": "hackers",
                        "traits": ["analytical", "cautious", "mysterious"]
                    },
                    {
                        "name": "Dexter DeShawn",
                        "description": "High-profile fixer with big ambitions",
                        "role": "fixer",
                        "faction": "underground",
                        "traits": ["ambitious", "greedy", "charismatic"]
                    },
                    {
                        "name": "Viktor Vector",
                        "description": "Skilled ripperdoc with a heart of gold",
                        "role": "merchant",
                        "faction": "neutral",
                        "traits": ["loyal", "disciplined", "honorable"]
                    }
                ]
            }
        }
    }
    
    # Character template
    character_template = {
        "id": "cyberpunk_npc",
        "name": "Night City Character",
        "content_type": "character",
        "description": "A procedurally generated character in the cyberpunk world",
        "complexity": 3,
        "themes": ["cyberpunk", "noir"],
        "tones": ["dark", "mysterious"],
        "factions": ["corporate", "underground", "hackers", "outcasts"],
        "tags": ["npc", "character"],
        "template_data": {
            "structure": {
                "name": "$var:character_name",
                "description": "$var:character_description",
                "role": "$var:character_role",
                "faction": "$var:character_faction",
                "traits": "$var:character_traits",
                "background": "$var:character_background",
                "appearance": {
                    "style": "$var:style",
                    "notable_features": "$var:notable_features",
                    "cybernetics": "$var:cybernetics"
                },
                "motivations": {
                    "primary": "$var:primary_motivation",
                    "secondary": "$var:secondary_motivation"
                },
                "skills": "$var:skills",
                "inventory": "$generate:$var:inventory_count:inventory_item"
            },
            "variables": {
                "character_name": "$random:Johnny Silverhand,Alt Cunningham,Adam Smasher,Judy Alvarez,Panam Palmer,River Ward,Kerry Eurodyne,Evelyn Parker",
                "character_description": "A $var:character_adjective figure in Night City's $var:character_scene scene",
                "character_adjective": "$random:notorious,respected,feared,mysterious,influential,skilled,ambitious,cunning",
                "character_scene": "$random:underground,corporate,mercenary,tech,entertainment,criminal,hacking,gambling",
                "character_role": "$random:fixer,hacker,corporate,enforcer,merchant,entertainer,outcast,gambler",
                "character_faction": "$random:corporate,underground,hackers,outcasts,neutral",
                "character_traits": ["$random:ambitious,cautious,charismatic,cunning,loyal,greedy,honorable,ruthless,paranoid,reckless", 
                                    "$random:mysterious,analytical,creative,disciplined,rebellious"],
                "character_background": "Born in the $var:origin_location of Night City, $var:character_name rose through the ranks of the $var:character_faction faction by $var:achievement.",
                "origin_location": "$random:slums,corporate zone,combat zone,suburbs,megabuildings,outskirts",
                "achievement": "$random:sheer determination,cunning deals,technical brilliance,brutal force,charismatic leadership,lucky breaks",
                "style": "$random:corporate,streetwear,punk,nomad,high fashion,minimalist,retro,military",
                "notable_features": "$random:distinctive tattoos,unique hairstyle,striking eyes,facial scars,chrome implants,unusual clothing,distinctive voice,memorable mannerisms",
                "cybernetics": ["$random:optical implants,arm replacements,neural interface,subdermal armor,reflex boosters,cyberdeck,voice modulator,pain editor"],
                "primary_motivation": "$random:wealth,power,revenge,knowledge,freedom,survival,recognition,loyalty",
                "secondary_motivation": "$random:protection,curiosity,thrill,stability,connection,redemption,legacy,escape",
                "skills": ["$random:hacking,combat,negotiation,stealth,engineering,medicine,driving,leadership", 
                          "$random:electronics,marksmanship,intimidation,persuasion,piloting,crafting"],
                "inventory_count": "$range:2,4"
            },
            "content_blocks": {
                "inventory_item": [
                    {
                        "name": "Militech M-76 Pistol",
                        "type": "weapon",
                        "quality": "common",
                        "description": "Standard sidearm with decent stopping power"
                    },
                    {
                        "name": "Arasaka Cyberdeck",
                        "type": "tech",
                        "quality": "rare",
                        "description": "High-end hacking device with military-grade ICE breakers"
                    },
                    {
                        "name": "Trauma Team Platinum Card",
                        "type": "service",
                        "quality": "legendary",
                        "description": "Premium medical evacuation service for the wealthy elite"
                    },
                    {
                        "name": "Armored Jacket",
                        "type": "clothing",
                        "quality": "uncommon",
                        "description": "Stylish jacket with hidden ballistic weave"
                    },
                    {
                        "name": "Neural Booster Chips",
                        "type": "consumable",
                        "quality": "uncommon",
                        "description": "Temporary cognitive enhancement, popular among netrunners"
                    },
                    {
                        "name": "Access Keycard",
                        "type": "key",
                        "quality": "rare",
                        "description": "Security access to restricted corporate areas"
                    }
                ]
            }
        }
    }
    
    # Save templates to files
    templates_dir = "data/templates"
    
    with open(os.path.join(templates_dir, "quest_template.json"), "w") as f:
        json.dump(quest_template, f, indent=2)
    
    with open(os.path.join(templates_dir, "environment_template.json"), "w") as f:
        json.dump(environment_template, f, indent=2)
    
    with open(os.path.join(templates_dir, "character_template.json"), "w") as f:
        json.dump(character_template, f, indent=2)


def create_player_profiles(api: ContentGenerationAPI):
    """Create sample player profiles with different preferences."""
    # Action-oriented player
    action_player = {
        "themes": {
            "cyberpunk": 0.8,
            "noir": 0.6,
            "dystopian": 0.7,
            "technological": 0.9
        },
        "tones": {
            "dark": 0.7,
            "tense": 0.9,
            "thrilling": 0.8,
            "serious": 0.6
        },
        "factions": {
            "corporate": 0.3,
            "underground": 0.7,
            "hackers": 0.8,
            "outcasts": 0.6
        },
        "complexity": {
            "quest": 4,
            "environment": 3,
            "character": 2
        },
        "engagement": {
            "quest": 0.9,
            "environment": 0.7,
            "character": 0.5
        },
        "custom": {
            "prefers_combat": True,
            "prefers_stealth": False,
            "risk_tolerance": 0.8
        }
    }
    
    # Story-oriented player
    story_player = {
        "themes": {
            "cyberpunk": 0.7,
            "noir": 0.9,
            "dystopian": 0.8,
            "technological": 0.6
        },
        "tones": {
            "dark": 0.8,
            "mysterious": 0.9,
            "philosophical": 0.7,
            "melancholic": 0.6
        },
        "factions": {
            "corporate": 0.6,
            "underground": 0.8,
            "hackers": 0.7,
            "outcasts": 0.9
        },
        "complexity": {
            "quest": 5,
            "environment": 4,
            "character": 5
        },
        "engagement": {
            "quest": 0.8,
            "environment": 0.6,
            "character": 0.9
        },
        "custom": {
            "prefers_combat": False,
            "prefers_stealth": True,
            "risk_tolerance": 0.4
        }
    }
    
    # Social-oriented player
    social_player = {
        "themes": {
            "cyberpunk": 0.6,
            "noir": 0.5,
            "dystopian": 0.4,
            "technological": 0.7,
            "luxurious": 0.8
        },
        "tones": {
            "humorous": 0.7,
            "light": 0.6,
            "thrilling": 0.5,
            "mysterious": 0.6
        },
        "factions": {
            "corporate": 0.7,
            "underground": 0.6,
            "hackers": 0.5,
            "elites": 0.8
        },
        "complexity": {
            "quest": 3,
            "environment": 4,
            "character": 5
        },
        "engagement": {
            "quest": 0.6,
            "environment": 0.7,
            "character": 0.9
        },
        "custom": {
            "prefers_combat": False,
            "prefers_stealth": False,
            "risk_tolerance": 0.5,
            "social_focus": True
        }
    }
    
    # Register players
    api.register_player("action_player", action_player)
    api.register_player("story_player", story_player)
    api.register_player("social_player", social_player)
    
    print("Created player profiles:")
    print("- Action-oriented player (action_player)")
    print("- Story-oriented player (story_player)")
    print("- Social-oriented player (social_player)")


def generate_personalized_quests(api: ContentGenerationAPI):
    """Generate personalized quests for different player types."""
    print("\n=== Generating Personalized Quests ===")
    
    # Generate quests for each player
    action_quest = api.generate_quest("action_player", "challenge")
    story_quest = api.generate_quest("story_player", "side")
    social_quest = api.generate_quest("social_player", "faction")
    
    # Display quest differences
    print("\nAction Player Quest:")
    print(f"Name: {action_quest['name']}")
    print(f"Description: {action_quest['description']}")
    print(f"Objectives: {len(action_quest['content_data'].get('objectives', []))} objectives")
    
    print("\nStory Player Quest:")
    print(f"Name: {story_quest['name']}")
    print(f"Description: {story_quest['description']}")
    print(f"Objectives: {len(story_quest['content_data'].get('objectives', []))} objectives")
    
    print("\nSocial Player Quest:")
    print(f"Name: {social_quest['name']}")
    print(f"Description: {social_quest['description']}")
    print(f"Objectives: {len(social_quest['content_data'].get('objectives', []))} objectives")


def generate_environments(api: ContentGenerationAPI):
    """Generate environments with faction dynamics."""
    print("\n=== Generating Dynamic Environments ===")
    
    # Generate environments
    corporate_env = api.generate_environment(
        "action_player", 
        "corporate",
        {"variables": {"controlling_faction": "corporate"}}
    )
    
    underground_env = api.generate_environment(
        "story_player", 
        "underground",
        {"variables": {"controlling_faction": "underground"}}
    )
    
    # Display environment differences
    print("\nCorporate Environment:")
    print(f"Name: {corporate_env['name']}")
    print(f"Description: {corporate_env['description']}")
    print(f"Controlling Faction: {corporate_env['content_data'].get('controlling_faction', 'none')}")
    print(f"State: {corporate_env['content_data'].get('state', 'unknown')}")
    
    print("\nUnderground Environment:")
    print(f"Name: {underground_env['name']}")
    print(f"Description: {underground_env['description']}")
    print(f"Controlling Faction: {underground_env['content_data'].get('controlling_faction', 'none')}")
    print(f"State: {underground_env['content_data'].get('state', 'unknown')}")


def generate_characters(api: ContentGenerationAPI):
    """Generate characters with relationships."""
    print("\n=== Generating Dynamic Characters ===")
    
    # Generate characters
    corporate_char = api.generate_character(
        "action_player", 
        "corporate",
        "corporate"
    )
    
    hacker_char = api.generate_character(
        "story_player", 
        "hacker",
        "hackers"
    )
    
    # Display character differences
    print("\nCorporate Character:")
    print(f"Name: {corporate_char['name']}")
    print(f"Description: {corporate_char['description']}")
    print(f"Role: {corporate_char['content_data'].get('role', 'unknown')}")
    print(f"Faction: {corporate_char['content_data'].get('faction', 'unknown')}")
    print(f"Traits: {corporate_char['content_data'].get('traits', [])}")
    
    print("\nHacker Character:")
    print(f"Name: {hacker_char['name']}")
    print(f"Description: {hacker_char['description']}")
    print(f"Role: {hacker_char['content_data'].get('role', 'unknown')}")
    print(f"Faction: {hacker_char['content_data'].get('faction', 'unknown')}")
    print(f"Traits: {hacker_char['content_data'].get('traits', [])}")


def demonstrate_preference_evolution(api: ContentGenerationAPI):
    """Demonstrate how content adapts as player preferences evolve."""
    print("\n=== Demonstrating Preference Evolution ===")
    
    # Generate initial quest
    print("\nInitial quest for action player:")
    initial_quest = api.generate_quest("action_player")
    print(f"Name: {initial_quest['name']}")
    print(f"Description: {initial_quest['description']}")
    
    # Update preferences
    print("\nUpdating player preferences to favor noir and mysterious content...")
    api.update_player_preference("action_player", "theme", "noir", 0.9)
    api.update_player_preference("action_player", "tone", "mysterious", 0.9)
    api.update_player_preference("action_player", "faction", "underground", 0.9)
    
    # Generate new quest with updated preferences
    print("\nNew quest after preference update:")
    updated_quest = api.generate_quest("action_player")
    print(f"Name: {updated_quest['name']}")
    print(f"Description: {updated_quest['description']}")


def run_demo():
    """Run the complete demonstration."""
    print("=== NovaLux Procedural Content Generation Demo ===\n")
    
    # Setup
    create_data_directory()
    create_sample_templates()
    
    # Initialize API
    api = ContentGenerationAPI(".")
    
    # Create player profiles
    create_player_profiles(api)
    
    # Generate content
    generate_personalized_quests(api)
    generate_environments(api)
    generate_characters(api)
    demonstrate_preference_evolution(api)
    
    # Save state
    api.save_state()
    
    print("\n=== Demo Complete ===")
    print("The procedural content generation system has demonstrated:")
    print("1. Player preference-based content personalization")
    print("2. Dynamic environment generation with faction dynamics")
    print("3. Character generation with traits and relationships")
    print("4. Content adaptation as player preferences evolve")
    print("\nState has been saved to the data/state directory.")


if __name__ == "__main__":
    run_demo()
