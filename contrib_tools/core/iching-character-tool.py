import sys
import random
import logging
import os
import string
import json
import datetime
from typing import Dict, Any, List, Optional, Union

__version__ = "0.2.0"
__updated__ = "2025-05-15"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "iching_character_generator.log"))
    ]
)
logger = logging.getLogger("iching_character_generator")

# Import MCP server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("iching-character-generator-server")

# Define the canonical set of emotions
EMOTIONS = [
    "Joy", 
    "Trust", 
    "Fear", 
    "Surprise", 
    "Sadness", 
    "Boredom", 
    "Anger", 
    "Interest"
]

# Define a list of character name prefixes and suffixes for procedural generation
NAME_PREFIXES = [
    "Ar", "Br", "Cr", "Dr", "El", "Fr", "Gr", "Ha", "In", "Ja", 
    "Ka", "Li", "Mo", "Ne", "Ori", "Pi", "Qu", "Ra", "Se", "Tr", 
    "Ul", "Vi", "Wa", "Xe", "Yu", "Za"
]

NAME_SUFFIXES = [
    "ack", "ber", "cor", "dor", "ek", "fin", "gon", "hel", "il", "jin",
    "kin", "lar", "mor", "nir", "ond", "pex", "rin", "sar", "tor", "ven",
    "wix", "xar", "yll", "zor"
]

# Define character trait pools
TRAITS = [
    "Brave", "Cautious", "Clever", "Determined", "Empathetic", 
    "Forgiving", "Generous", "Honest", "Impulsive", "Judgmental",
    "Kind", "Loyal", "Mysterious", "Nurturing", "Observant", 
    "Practical", "Quiet", "Resourceful", "Stubborn", "Thoughtful"
]

QUIRKS = [
    "Always hums when thinking", "Blinks rapidly when nervous", 
    "Collects odd trinkets", "Doodles in the margins", 
    "Eats one food at a time", "Fidgets with a coin", 
    "Gestures wildly while talking", "Has perfect pitch",
    "Interrupts with 'actually' frequently", "Jumps at loud noises",
    "Keeps a journal of dreams", "Laughs at inappropriate times",
    "Memorizes obscure facts", "Never uses contractions",
    "Only wears one color", "Prefers the night", 
    "Quotes ancient proverbs", "Repeats the last word spoken",
    "Speaks to inanimate objects", "Twirls hair when lying"
]

# I Ching Hexagram definitions with names and meanings
HEXAGRAMS = {
    1: {"name": "Ch'ien (The Creative, Heaven)", "meaning": "Strength, creativity, pure yang energy, leadership"},
    2: {"name": "K'un (The Receptive, Earth)", "meaning": "Receptivity, devotion, nurturing, pure yin energy"},
    3: {"name": "Chun (Difficulty at the Beginning)", "meaning": "Initial obstacles, growth through challenge, new ventures"},
    4: {"name": "Mêng (Youthful Folly)", "meaning": "Inexperience, learning, need for guidance, potential"},
    5: {"name": "Hsü (Waiting, Nourishment)", "meaning": "Patience, timing, natural progression, necessary preparation"},
    6: {"name": "Sung (Conflict)", "meaning": "Disagreement, tension, resolution through compromise"},
    7: {"name": "Shih (The Army)", "meaning": "Discipline, organized action, strategic leadership"},
    8: {"name": "Pi (Holding Together)", "meaning": "Unity, alliance, mutual support, social bonds"},
    9: {"name": "Hsiao Ch'u (The Taming Power of the Small)", "meaning": "Attention to detail, gradual progress, restraint"},
    10: {"name": "Lü (Treading)", "meaning": "Conduct, careful action, walking a careful path, dignified progress"},
    11: {"name": "T'ai (Peace)", "meaning": "Harmony, balance, prosperity, heaven and earth in communion"},
    12: {"name": "P'i (Standstill)", "meaning": "Stagnation, decline, adversity, heaven and earth out of communion"},
    13: {"name": "T'ung Jên (Fellowship with Others, Brotherhood)", "meaning": "Community, partnership, shared ideals"},
    14: {"name": "Ta Yu (Possession in Great Measure)", "meaning": "Abundance, prosperity, great possession with humility"},
    15: {"name": "Ch'ien (Modesty)", "meaning": "Humility, moderation, balanced attitude, reserve"},
    16: {"name": "Yü (Enthusiasm)", "meaning": "Joy, harmony, motivation, readiness to act"},
    17: {"name": "Sui (Following)", "meaning": "Adaptation, alignment, natural response, willing followers"},
    18: {"name": "Ku (Work on What Has Been Spoiled)", "meaning": "Decay, correction of corruption, addressing problems"},
    19: {"name": "Lin (Approach)", "meaning": "Advancement, influence, approaching greatness"},
    20: {"name": "Kuan (Contemplation)", "meaning": "Observation, perspective, overview, careful consideration"},
    21: {"name": "Shih Ho (Biting Through)", "meaning": "Decision, powerful action, justice, clarity"},
    22: {"name": "Pi (Grace)", "meaning": "Elegance, refinement, aesthetic clarity, adornment"},
    23: {"name": "Po (Splitting Apart)", "meaning": "Deterioration, undermining influences, unavoidable decay"},
    24: {"name": "Fu (Return)", "meaning": "Turning point, renewal, return of positive energy"},
    25: {"name": "Wu Wang (Innocence)", "meaning": "Naturalness, spontaneity, unpremeditated action"},
    26: {"name": "Ta Ch'u (The Taming Power of the Great)", "meaning": "Accumulation of energy, great power restrained"},
    27: {"name": "I (Corners of the Mouth, Providing Nourishment)", "meaning": "Sustenance, careful attention to nourishment"},
    28: {"name": "Ta Kuo (Preponderance of the Great)", "meaning": "Critical mass, great excess, burden of responsibility"},
    29: {"name": "K'an (The Abysmal, Water)", "meaning": "Danger, the abyss, repeated trials, flowing through difficulty"},
    30: {"name": "Li (The Clinging, Fire)", "meaning": "Clarity, brightness, dependence, attachment"},
    31: {"name": "Hsien (Influence)", "meaning": "Mutual influence, attraction, courtship, responsiveness"},
    32: {"name": "Hêng (Duration)", "meaning": "Persistence, stability, endurance, constancy"},
    33: {"name": "Tun (Retreat)", "meaning": "Strategic withdrawal, conservation, timing, necessary distance"},
    34: {"name": "Ta Chuang (The Power of the Great)", "meaning": "Great vigor, great strength, focused power"},
    35: {"name": "Chin (Progress)", "meaning": "Advancement, rapid progress, clarity of purpose, sunrise"},
    36: {"name": "Ming I (Darkening of the Light)", "meaning": "Adversity, inner light during darkness, perseverance"},
    37: {"name": "Chia Jên (The Family)", "meaning": "Clan, relationships, structure, domestic order"},
    38: {"name": "K'uei (Opposition)", "meaning": "Contradiction, divergence, contrasting forces, polarization"},
    39: {"name": "Chien (Obstruction)", "meaning": "Difficulty, obstacle, impasse, seeking another path"},
    40: {"name": "Hsieh (Deliverance)", "meaning": "Release, resolution, dissolving tensions, transition"},
    41: {"name": "Sun (Decrease)", "meaning": "Reduction, accepting loss, simplification, focusing"},
    42: {"name": "I (Increase)", "meaning": "Gain, expanding resources, beneficial influence"},
    43: {"name": "Kuai (Breakthrough)", "meaning": "Resolution, decisive action, overcoming resistance"},
    44: {"name": "Kou (Coming to Meet)", "meaning": "Unexpected encounter, temptation, alertness needed"},
    45: {"name": "Ts'ui (Gathering Together)", "meaning": "Congregation, assembly, communal effort, focused gathering"},
    46: {"name": "Shêng (Pushing Upward)", "meaning": "Ascending, gradual progress, step-by-step advancement"},
    47: {"name": "K'un (Oppression)", "meaning": "Adversity, being constrained, exhaustion, perseverance under difficulty"},
    48: {"name": "Ching (The Well)", "meaning": "Source, center of community, reliability, renewal"},
    49: {"name": "Ko (Revolution)", "meaning": "Deep change, transformation, major reform"},
    50: {"name": "Ting (The Cauldron)", "meaning": "Transformation, cooking vessel, nourishment, crystallization"},
    51: {"name": "Chên (Arousing, Thunder)", "meaning": "Shock, awakening, sudden change, stimulus to action"},
    52: {"name": "Kên (Keeping Still, Mountain)", "meaning": "Stillness, stopping, meditation, stability"},
    53: {"name": "Chien (Development)", "meaning": "Gradual progress, marrying well, orderly growth"},
    54: {"name": "Kuei Mei (The Marrying Maiden)", "meaning": "Temporary arrangements, subordinate role, limitations"},
    55: {"name": "Fêng (Abundance)", "meaning": "Fullness, peak of prosperity, zenith, flourishing"},
    56: {"name": "Lü (The Wanderer)", "meaning": "Transience, journey, impermanence, adaptability"},
    57: {"name": "Sun (The Gentle, Wind)", "meaning": "Penetrating influence, subtle action, persistence"},
    58: {"name": "Tui (The Joyous, Lake)", "meaning": "Joy, satisfaction, pleasure, equanimity"},
    59: {"name": "Huan (Dispersion)", "meaning": "Dissolution, dispersal, letting go, release of tension"},
    60: {"name": "Chieh (Limitation)", "meaning": "Restriction, boundaries, necessary constraints, clear definition"},
    61: {"name": "Chung Fu (Inner Truth)", "meaning": "Inner alignment, sincerity, central stability, confidence"},
    62: {"name": "Hsiao Kuo (Preponderance of the Small)", "meaning": "Small matters, attention to detail, adaptability"},
    63: {"name": "Chi Chi (After Completion)", "meaning": "Completion, achievement, danger of complacency, transition"},
    64: {"name": "Wei Chi (Before Completion)", "meaning": "Incomplete, anticipation, on the cusp of completion"}
}

# Hexagram-related abilities and philosophies
HEXAGRAM_ABILITIES = {
    1: ["Creative Leadership", "Strategic Vision", "Unwavering Determination", "Divine Inspiration"],
    2: ["Deep Receptivity", "Nurturing Support", "Patient Cultivation", "Harmonious Adaptability"],
    3: ["Crisis Management", "Initial Breakthrough", "Chaos Navigation", "Growth Through Difficulty"],
    4: ["Innocent Perception", "Learning Receptivity", "Youthful Adaptation", "Beginner's Mind"],
    5: ["Patient Observation", "Strategic Waiting", "Timely Action", "Careful Nourishment"],
    6: ["Conflict Resolution", "Diplomatic Mediation", "Tension Management", "Strategic Compromise"],
    7: ["Disciplined Coordination", "Strategic Deployment", "Group Leadership", "Organizational Skill"],
    8: ["Alliance Building", "Community Coordination", "Strong Bonds", "Mutual Support"],
    9: ["Detailed Precision", "Gradual Influence", "Measured Restraint", "Small-Scale Mastery"],
    10: ["Careful Navigation", "Dignified Conduct", "Risk Management", "Tiger Taming"],
    11: ["Harmonious Integration", "Balanced Perspective", "Prosperous Leadership", "Peaceful Influence"],
    12: ["Endurance Through Decline", "Recognition of Stagnation", "Preserving Resources", "Weathering Adversity"],
    13: ["Brotherhood Leadership", "Community Building", "Shared Purpose", "Collaborative Strength"],
    14: ["Abundant Resource Management", "Generous Distribution", "Humble Power", "Prosperity Guidance"],
    15: ["Humble Influence", "Quiet Effectiveness", "Moderate Approach", "Unassuming Strength"],
    16: ["Motivational Leadership", "Enthusiastic Engagement", "Energetic Inspiration", "Harmonious Direction"],
    17: ["Adaptive Following", "Natural Response", "Receptive Alignment", "Flexible Adaptation"],
    18: ["Problem Solving", "Reform Implementation", "Decay Reversal", "Corruption Correction"],
    19: ["Powerful Approach", "Influential Advancement", "Authoritative Presence", "Inspirational Leadership"],
    20: ["Deep Observation", "Insightful Understanding", "Objective Analysis", "Contemplative Awareness"],
    21: ["Decisive Action", "Sharp Discernment", "Just Intervention", "Breaking Through Obstacles"],
    22: ["Refined Expression", "Aesthetic Discernment", "Beautiful Communication", "Elegant Presentation"],
    23: ["Recognizing Deterioration", "Managing Decline", "Acceptance of Endings", "Preparing for Renewal"],
    24: ["Initiating Renewal", "Turning Point Navigation", "Rebirth Guidance", "Cyclical Understanding"],
    25: ["Natural Spontaneity", "Unbiased Perception", "Pure Intention", "Alignment with Nature"],
    26: ["Energy Accumulation", "Powerful Restraint", "Resource Concentration", "Controlled Strength"],
    27: ["Nourishment Provision", "Resource Distribution", "Support Coordination", "Sustenance Management"],
    28: ["Critical Mass Management", "Structural Support", "Load-bearing Capacity", "Extraordinary Pressure Handling"],
    29: ["Water Affinity", "Danger Sense", "Emotional Resilience", "Patient Observation"],
    30: ["Illuminating Clarity", "Dependent Connection", "Bright Articulation", "Loyal Attachment"],
    31: ["Responsive Sensitivity", "Mutual Connection", "Influential Attraction", "Gentle Persuasion"],
    32: ["Enduring Consistency", "Stable Foundation", "Persistent Effort", "Reliable Presence"],
    33: ["Strategic Retreat", "Conservation Insight", "Timing Awareness", "Dignified Withdrawal"],
    34: ["Powerful Implementation", "Strong Leadership", "Dynamic Action", "Energetic Initiative"],
    35: ["Rapid Advancement", "Dawn Recognition", "Progressive Vision", "Forward Momentum"],
    36: ["Inner Light Preservation", "Adversity Navigation", "Dark Times Endurance", "Hidden Wisdom"],
    37: ["Family Leadership", "Relationship Structure", "Role Definition", "Domestic Harmony"],
    38: ["Polarization Management", "Complementary Understanding", "Divergent Integration", "Opposing Force Balance"],
    39: ["Obstacle Navigation", "Alternative Pathfinding", "Impasse Resolution", "Creative Problem-Solving"],
    40: ["Tension Release", "Transition Management", "Resolution Discovery", "Liberation Insight"],
    41: ["Simplification Skill", "Loss Acceptance", "Essential Focus", "Deliberate Reduction"],
    42: ["Growth Management", "Resource Expansion", "Beneficial Influence", "Accumulation Strategy"],
    43: ["Resistance Breaking", "Decisive Resolution", "Breakthrough Achievement", "Firm Commitment"],
    44: ["Encounter Awareness", "Temptation Recognition", "Alert Discernment", "Cautious Engagement"],
    45: ["Community Building", "Focused Gathering", "Collective Organization", "Team Leadership"],
    46: ["Gradual Advancement", "Upward Mobility", "Step-by-Step Progress", "Ascending Vision"],
    47: ["Adversity Endurance", "Constraint Management", "Limited Resource Navigation", "Inner Strength"],
    48: ["Source Connection", "Community Nourishment", "Reliable Support", "Renewable Resource Management"],
    49: ["Transformation Guidance", "Revolution Management", "Deep Change Navigation", "Renewal Leadership"],
    50: ["Alchemical Transformation", "Nourishment Creation", "Substance Refinement", "Cultural Appreciation"],
    51: ["Shock Adaptation", "Awakening Insight", "Sudden Change Management", "Decisive Action"],
    52: ["Stillness Cultivation", "Meditation Insight", "Stable Presence", "Inner Quiet"],
    53: ["Gradual Development", "Appropriate Connection", "Orderly Growth", "Steady Progress"],
    54: ["Limitation Navigation", "Temporary Arrangement", "Role Acceptance", "Dignified Adaptation"],
    55: ["Abundance Management", "Peak Experience", "Fullness Appreciation", "Prosperous Leadership"],
    56: ["Journey Navigation", "Adaptable Mobility", "Transient Understanding", "Traveler's Wisdom"],
    57: ["Gentle Persistence", "Subtle Influence", "Penetrating Insight", "Flexible Advancement"],
    58: ["Joy Cultivation", "Satisfying Connection", "Harmonious Pleasure", "Open Communication"],
    59: ["Dispersal Management", "Tension Release", "Letting Go Skill", "Energy Distribution"],
    60: ["Boundary Setting", "Limitation Definition", "Constraint Navigation", "Clear Demarcation"],
    61: ["Inner Truth Connection", "Sincere Communication", "Central Alignment", "Authentic Expression"],
    62: ["Detail Management", "Small Matter Navigation", "Adaptable Handling", "Precise Action"],
    63: ["Completion Awareness", "Achievement Recognition", "Transition Management", "Vigilant Success"],
    64: ["Anticipation Management", "Final Stage Navigation", "Almost-there Awareness", "Pre-completion Focus"]
}

HEXAGRAM_PHILOSOPHIES = {
    1: "Embrace the creative power within to manifest great works.",
    2: "True strength lies in receptivity and gentle persistence.",
    3: "The greatest growth emerges from the most challenging beginnings.",
    4: "A beginner's mind remains open to all possibilities and guidance.",
    5: "Patient waiting is not passive; it is the active nourishment of potential.",
    6: "In conflict lies the opportunity for greater understanding and harmony.",
    7: "Discipline and organization transform individual strength into collective power.",
    8: "Unity of purpose creates bonds stronger than any individual force.",
    9: "Small, consistent actions ultimately create the greatest changes.",
    10: "Walk with dignity and care upon dangerous ground.",
    11: "When heaven and earth commune, all beings flourish in harmony.",
    12: "Even in times of standstill, inner progress remains possible.",
    13: "A captain serves his crew; a crew serves each other; no one serves the merchants.",
    14: "Great possession brings responsibility; abundance without humility becomes burden.",
    15: "The truly great accomplish much while appearing to do little.",
    16: "Enthusiasm harmonizes heaven and earth, bringing all beings into alignment.",
    17: "True leadership knows when to follow the natural course of events.",
    18: "What has been spoiled through neglect can be restored through devoted work.",
    19: "Approach greatness with the reverence and preparation it deserves.",
    20: "Contemplation from a proper distance reveals the true nature of all things.",
    21: "Justice requires decisive action that cuts through obstacles with clarity.",
    22: "True beauty lies in form that perfectly expresses essence.",
    23: "Recognizing deterioration is the first step toward renewal.",
    24: "After the darkest time, the light always returns.",
    25: "Act without calculation, as heaven does, bringing forth life without expectation.",
    26: "Great power requires great restraint and careful cultivation.",
    27: "Pay attention to what nourishes the self and others.",
    28: "Extraordinary times require extraordinary structure and support.",
    29: "The depth of the abyss measures the height of the possible ascent.",
    30: "Cling to clarity and illumination in all situations.",
    31: "Influence between beings creates the conditions for all relationships.",
    32: "Endurance without constancy is merely stubbornness.",
    33: "Strategic retreat is not surrender but preparation for future advance.",
    34: "Great strength requires heightened awareness of responsibility.",
    35: "Progress comes to those who rise early and work with clarity of purpose.",
    36: "When external light dims, the inner light must burn more brightly.",
    37: "The family is the foundation upon which all social structures are built.",
    38: "Opposing forces create the tension from which harmony can emerge.",
    39: "When facing obstruction, seek a different path rather than forcing ahead.",
    40: "Resolution comes when we release what we have been unnecessarily holding.",
    41: "Decrease what is above to increase what is below.",
    42: "Increase what is below to benefit what is above.",
    43: "Breakthrough requires both decisiveness and appropriate caution.",
    44: "The unexpected encounter brings both opportunity and danger.",
    45: "Proper gathering requires a center of gravity and clear purpose.",
    46: "Growth emerges gradually, step by step, like a tree reaching skyward.",
    47: "In exhaustion and constraint, maintain dignity and inner strength.",
    48: "The well remains the same though the generations change.",
    49: "Revolution succeeds only when it accords with the higher truth of the time.",
    50: "The cauldron's value lies in what transformative nourishment it can provide.",
    51: "Thunder awakens and arouses all beings to new awareness.",
    52: "In stillness, we reconnect with our essential nature.",
    53: "Development proceeds gradually, like a tree growing on a mountain.",
    54: "Even in subordinate positions, maintain dignity and proper relationships.",
    55: "At the peak of abundance, prepare for the inevitable decline to follow.",
    56: "The wanderer finds security in proper conduct rather than fixed position.",
    57: "Gentle penetration ultimately overcomes rigid resistance.",
    58: "True joy emerges from inner harmony rather than external circumstances.",
    59: "Dispersion of what has become rigid allows new patterns to form.",
    60: "Without limitation, there can be no clear form or purpose.",
    61: "Inner truth manifests when intention and action are perfectly aligned.",
    62: "When great things cannot be done, small things should be done with great love.",
    63: "After completion, remain vigilant for the seeds of new decline.",
    64: "Before completion, focus all energies toward the final goal."
}

# Special personality traits associated with each hexagram
HEXAGRAM_TRAITS = {
    1: ["Commanding", "Visionary", "Self-Assured", "Creative"],
    2: ["Nurturing", "Supportive", "Patient", "Accommodating"],
    3: ["Resilient", "Pioneering", "Resourceful", "Tenacious"],
    4: ["Curious", "Teachable", "Inexperienced", "Open-minded"],
    5: ["Patient", "Observant", "Strategic", "Deliberate"],
    6: ["Diplomatic", "Assertive", "Principled", "Reconciling"],
    7: ["Disciplined", "Organized", "Strategic", "Authoritative"],
    8: ["Cooperative", "Loyal", "Unifying", "Supportive"],
    9: ["Meticulous", "Prudent", "Restrained", "Detail-oriented"],
    10: ["Cautious", "Dignified", "Balanced", "Respectful"],
    11: ["Harmonious", "Prosperous", "Balanced", "Integrative"],
    12: ["Resilient", "Realistic", "Preserving", "Enduring"],
    13: ["Brotherly", "Communal", "Inclusive", "Collaborative"],
    14: ["Generous", "Abundant", "Humble", "Resource-rich"],
    15: ["Modest", "Understated", "Centered", "Genuine"],
    16: ["Enthusiastic", "Motivating", "Harmonizing", "Inspired"],
    17: ["Adaptable", "Receptive", "Aligned", "Following"],
    18: ["Reforming", "Corrective", "Restorative", "Problem-solving"],
    19: ["Advancing", "Influential", "Commanding", "Progressive"],
    20: ["Observant", "Contemplative", "Insightful", "Objective"],
    21: ["Decisive", "Direct", "Justice-seeking", "Penetrating"],
    22: ["Elegant", "Refined", "Tasteful", "Aesthetic"],
    23: ["Realistic", "Accepting", "Transitional", "Aware"],
    24: ["Renewing", "Cyclical", "Hopeful", "Rebounding"],
    25: ["Natural", "Spontaneous", "Innocent", "Pure"],
    26: ["Powerful", "Restrained", "Accumulated", "Controlled"],
    27: ["Nurturing", "Providing", "Supportive", "Sustaining"],
    28: ["Burdened", "Responsible", "Weight-bearing", "Structural"],
    29: ["Deep", "Resilient", "Water-like", "Flow-finding"],
    30: ["Illuminating", "Attached", "Dependent", "Bright"],
    31: ["Sensitive", "Responsive", "Attractive", "Influential"],
    32: ["Consistent", "Enduring", "Persistent", "Stable"],
    33: ["Strategic", "Withdrawing", "Timing-sensitive", "Conserving"],
    34: ["Powerful", "Vigorous", "Energetic", "Dynamic"],
    35: ["Progressive", "Dawn-like", "Advancing", "Clear-purposed"],
    36: ["Preserving", "Enduring", "Inner-focused", "Resilient"],
    37: ["Familial", "Structural", "Role-conscious", "Traditional"],
    38: ["Contrasting", "Polar", "Complementary", "Divergent"],
    39: ["Obstacle-aware", "Problem-solving", "Alternative-seeking", "Resourceful"],
    40: ["Releasing", "Resolving", "Transitional", "Unburdening"],
    41: ["Simplifying", "Reducing", "Focusing", "Accepting"],
    42: ["Increasing", "Expanding", "Benefiting", "Growing"],
    43: ["Breakthrough-seeking", "Decisive", "Resolving", "Determined"],
    44: ["Alert", "Discerning", "Encounter-ready", "Cautious"],
    45: ["Gathering", "Communal", "Focused", "Organizational"],
    46: ["Ascending", "Gradual", "Step-by-step", "Upward-moving"],
    47: ["Enduring", "Constrained", "Inner-strong", "Limited"],
    48: ["Reliable", "Central", "Renewing", "Source-connected"],
    49: ["Transformative", "Revolutionary", "Changing", "Radical"],
    50: ["Transformative", "Nourishing", "Cultural", "Refining"],
    51: ["Arousing", "Shocking", "Awakening", "Sudden"],
    52: ["Still", "Meditative", "Stable", "Centered"],
    53: ["Developmental", "Progressive", "Well-connected", "Orderly"],
    54: ["Adaptable", "Role-aware", "Temporary", "Dignified"],
    55: ["Abundant", "Flourishing", "Peak-oriented", "Zenith-aware"],
    56: ["Transient", "Adaptable", "Journey-oriented", "Unattached"],
    57: ["Penetrating", "Gentle", "Persistent", "Subtle"],
    58: ["Joyful", "Satisfying", "Pleasure-oriented", "Open"],
    59: ["Dispersing", "Releasing", "Dissolving", "Distributing"],
    60: ["Boundary-conscious", "Limiting", "Defining", "Demarcating"],
    61: ["Centered", "Sincere", "Truthful", "Authentic"],
    62: ["Detail-focused", "Small-scale", "Adaptable", "Precise"],
    63: ["Complete", "Achieved", "Vigilant", "Transitional"],
    64: ["Anticipatory", "Almost-there", "Pre-complete", "Final-stage"]
}

# Helper Functions for I Ching
def cast_coins():
    """Cast three coins and return the result as a value 6, 7, 8, or 9."""
    coins = [random.choice(["heads", "tails"]) for _ in range(3)]
    heads_count = coins.count("heads")
    
    # Convert to traditional I Ching values
    if heads_count == 3:  # 3 heads
        return 9  # Old Yang (changing)
    elif heads_count == 2:  # 2 heads, 1 tails
        return 7  # Young Yang
    elif heads_count == 1:  # 1 heads, 2 tails
        return 8  # Young Yin
    else:  # 0 heads, 3 tails
        return 6  # Old Yin (changing)

def cast_hexagram():
    """Cast a complete hexagram and identify changing lines."""
    lines = [cast_coins() for _ in range(6)]
    
    # Determine the hexagram number based on the lines
    # Convert 6->0, 7->1, 8->0, 9->1 for primary hexagram
    primary_binary = [1 if line in [7, 9] else 0 for line in lines]
    primary_trigrams = (
        4 * primary_binary[0] + 2 * primary_binary[1] + primary_binary[2],
        4 * primary_binary[3] + 2 * primary_binary[4] + primary_binary[5]
    )
    
    # Calculate hexagram number using the traditional King Wen sequence lookup table
    hexagram_lookup = [
        [1, 34, 5, 26, 11, 9, 14, 43],
        [25, 51, 3, 27, 24, 42, 21, 17],
        [6, 40, 29, 4, 7, 59, 64, 47],
        [33, 62, 39, 52, 15, 53, 56, 31],
        [12, 16, 8, 23, 2, 20, 35, 45],
        [44, 32, 48, 18, 46, 57, 50, 28],
        [13, 55, 63, 22, 36, 37, 30, 49],
        [10, 54, 60, 41, 19, 61, 38, 58]
    ]
    primary_hexagram = hexagram_lookup[primary_trigrams[0]][primary_trigrams[1]]
    
    # Identify changing lines
    changing_lines = [i+1 for i, line in enumerate(lines) if line in [6, 9]]
    
    # Generate the transformed hexagram if there are changing lines
    if changing_lines:
        # Convert 6->1, 7->1, 8->0, 9->0 for transformed hexagram
        transformed_binary = [(1 if line == 6 else 0 if line == 9 else value) 
                             for line, value in zip(lines, primary_binary)]
        transformed_trigrams = (
            4 * transformed_binary[0] + 2 * transformed_binary[1] + transformed_binary[2],
            4 * transformed_binary[3] + 2 * transformed_binary[4] + transformed_binary[5]
        )
        transformed_hexagram = hexagram_lookup[transformed_trigrams[0]][transformed_trigrams[1]]
    else:
        transformed_hexagram = None
    
    return {
        "primary": primary_hexagram,
        "changing_lines": changing_lines,
        "transformed": transformed_hexagram,
        "raw_lines": lines
    }

def get_hexagram_details(hexagram_casting):
    """Get full details for a hexagram casting including names, meanings, etc."""
    primary = hexagram_casting["primary"]
    transformed = hexagram_casting["transformed"]
    changing_lines = hexagram_casting["changing_lines"]
    
    # Get primary hexagram details
    primary_details = HEXAGRAMS.get(primary, {"name": f"Unknown Hexagram {primary}", 
                                             "meaning": "Meaning not available"})
    
    # Get transformed hexagram details if applicable
    transformed_details = None
    if transformed:
        transformed_details = HEXAGRAMS.get(transformed, {"name": f"Unknown Hexagram {transformed}", 
                                                        "meaning": "Meaning not available"})
    
    # Select abilities and philosophy based on hexagrams
    abilities = HEXAGRAM_ABILITIES.get(primary, ["Adaptability", "Resilience"])
    if len(abilities) > 4:
        abilities = random.sample(abilities, 4)  # Select 4 random abilities if more are available
    
    # Get primary hexagram philosophy
    philosophy = HEXAGRAM_PHILOSOPHIES.get(primary, "The way unfolds according to its own nature.")
    
    # Get traits associated with the hexagram
    traits = HEXAGRAM_TRAITS.get(primary, ["Adaptable", "Balanced"])
    
    return {
        "primary": {
            "number": primary,
            "name": primary_details["name"],
            "meaning": primary_details["meaning"]
        },
        "transformed": {
            "number": transformed,
            "name": transformed_details["name"] if transformed_details else None,
            "meaning": transformed_details["meaning"] if transformed_details else None
        } if transformed else None,
        "changing_lines": changing_lines,
        "abilities": abilities,
        "philosophy": philosophy,
        "traits": traits
    }

# Character Generation Functions
def generate_character_name():
    """Generate a character name from prefix and suffix combinations."""
    prefix = random.choice(NAME_PREFIXES)
    suffix = random.choice(NAME_SUFFIXES)
    return f"{prefix}{suffix}"

def generate_emotional_narrative(primary, secondary, name, trait):
    """Generate a short narrative based on the character's emotions."""
    
    # Map emotions to narrative templates
    emotion_templates = {
        "Joy": [
            f"{name} radiates warmth and positivity, finding delight in the smallest things.",
            f"The world seems brighter through {name}'s eyes, as they embrace each moment with enthusiasm."
        ],
        "Trust": [
            f"With an open heart, {name} approaches others without reservation or suspicion.",
            f"{name} builds connections easily, offering reliability and steadfast support."
        ],
        "Fear": [
            f"Shadows seem to follow {name}, whose eyes constantly scan for unseen threats.",
            f"Behind {name}'s cautious demeanor lies a mind mapping every possible danger."
        ],
        "Surprise": [
            f"{name} lives in a state of constant wonder, easily amazed by the unexpected.",
            f"The world never ceases to astonish {name}, whose perspective shifts with each new discovery."
        ],
        "Sadness": [
            f"A melancholy aura surrounds {name}, who carries an invisible weight on their shoulders.",
            f"{name} finds beauty in sorrow, connecting deeply with the bittersweet nature of existence."
        ],
        "Boredom": [
            f"Nothing seems to hold {name}'s interest for long, as they search for something truly engaging.",
            f"{name} moves through life with detached indifference, waiting for something worthy of attention."
        ],
        "Anger": [
            f"Passion burns intensely within {name}, whose emotions simmer just below the surface.",
            f"{name} channels their fierce energy into every pursuit, driven by an inner fire."
        ],
        "Interest": [
            f"Curiosity guides {name}'s journey, as they explore the world with insatiable fascination.",
            f"{name} approaches everything with analytical focus, collecting knowledge like precious gems."
        ]
    }
    
    # Select a random template for the primary emotion
    primary_narrative = random.choice(emotion_templates[primary])
    
    # Create secondary emotion influence
    if primary != secondary:
        # If emotions are different, create a contrast
        secondary_templates = {
            "Joy": f"Yet beneath this {trait.lower()} exterior, unexpected moments of delight break through.",
            "Trust": f"Despite everything, {name} maintains a surprising willingness to believe in others.",
            "Fear": f"However, an undercurrent of anxiety influences many of {name}'s decisions.",
            "Surprise": f"At times, {name}'s perspective shifts dramatically when confronted with the unexpected.",
            "Sadness": f"In quiet moments, a profound melancholy reveals the depth of {name}'s character.",
            "Boredom": f"Still, {name} often finds themselves unimpressed by what others find captivating.",
            "Anger": f"When provoked, {name} reveals a fierce intensity that transforms their demeanor.",
            "Interest": f"Nevertheless, {name}'s attention is quickly captured by intriguing new concepts."
        }
        secondary_narrative = secondary_templates[secondary]
    else:
        # If primary and secondary are the same, intensify the primary
        intensifiers = {
            "Joy": f"This overwhelming positivity defines {name}'s very essence.",
            "Trust": f"This profound faith in others is the cornerstone of {name}'s worldview.",
            "Fear": f"This pervasive anxiety colors every aspect of {name}'s existence.",
            "Surprise": f"This perpetual astonishment defines how {name} experiences reality.",
            "Sadness": f"This deep-seated melancholy has become inseparable from {name}'s identity.",
            "Boredom": f"This chronic disinterest has become {name}'s defining characteristic.",
            "Anger": f"This smoldering intensity is fundamental to understanding {name}'s nature.",
            "Interest": f"This relentless curiosity is the driving force behind all {name} does."
        }
        secondary_narrative = intensifiers[primary]
    
    # Combine narratives
    return f"{primary_narrative} {secondary_narrative}"

def generate_origin_story(name, hexagram_details):
    """Generate a character origin story based on hexagram details."""
    primary_hexagram = hexagram_details["primary"]
    transformed_hexagram = hexagram_details["transformed"]
    changing_lines = hexagram_details["changing_lines"]
    
    # Origin story templates based on primary hexagram categories
    templates = [
        f"Born during a time of {primary_hexagram['meaning'].lower()}, {name}'s early life was shaped by "
        f"the need to navigate challenging situations with care and insight.",
        
        f"{name} comes from a lineage where {primary_hexagram['meaning'].lower()} was the guiding principle, "
        f"instilling these values from an early age and shaping their worldview.",
        
        f"A pivotal moment in {name}'s childhood connected them deeply to the essence of "
        f"{primary_hexagram['name']}, forever altering their perspective on life's journey."
    ]
    
    # Add transformation element if applicable
    if transformed_hexagram:
        transformation_templates = [
            f"After experiencing a profound change, {name} began a transformation from "
            f"{primary_hexagram['meaning'].lower()} toward {transformed_hexagram['meaning'].lower()}.",
            
            f"Life's trials have pushed {name} to evolve beyond their initial nature of "
            f"{primary_hexagram['meaning'].lower()}, gradually embodying the qualities of "
            f"{transformed_hexagram['meaning'].lower()}.",
            
            f"{name} stands at a crucial transition point, their essence shifting from "
            f"{primary_hexagram['name']} toward {transformed_hexagram['name']}."
        ]
        templates.extend(transformation_templates)
    
    # Add specific details based on changing lines if applicable
    if changing_lines:
        line_templates = [
            f"The changing {get_ordinal(changing_lines[0])} line in their hexagram manifests as "
            f"a defining moment when they had to {get_line_action(changing_lines[0])}.",
        ]
        if len(changing_lines) > 1:
            line_templates.append(
                f"Their personality was forged through {len(changing_lines)} pivotal experiences, "
                f"most notably when they {get_line_action(changing_lines[-1])}."
            )
        templates.extend(line_templates)
    
    # Select and return a random template
    origin = random.choice(templates)
    
    # Add philosophical element
    philosophy = f" {name} lives by the principle: \"{hexagram_details['philosophy']}\""
    
    return origin + philosophy

def get_ordinal(n):
    """Return ordinal string for a number (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def get_line_action(line_number):
    """Generate a specific action for a changing line."""
    actions = {
        1: "faced a fundamental choice about their direction in life",
        2: "discovered an inner strength they didn't know they possessed",
        3: "overcame a significant obstacle through perseverance",
        4: "formed an unexpected alliance that changed their course",
        5: "rose to a position of influence they hadn't sought",
        6: "achieved a significant goal only to find it wasn't their true destination"
    }
    return actions.get(line_number, "experienced a profound transformation")

def generate_appearance(name, hexagram_details, emotion_primary, emotion_secondary):
    """Generate a character appearance description based on hexagram and emotions."""
    # Base templates for different hexagram categories
    heaven_earth_templates = [
        f"{name} has a commanding presence with perfect posture and clear, penetrating eyes.",
        f"{name}'s form seems to radiate stability and grounding energy.",
        f"There is something elemental about {name}'s appearance, as if embodying pure archetypal energy."
    ]
    
    water_fire_templates = [
        f"{name} has eyes that shift between depths of emotion and flashes of insight.",
        f"There's a fluid quality to {name}'s movements, alternating between flowing grace and energetic bursts.",
        f"{name}'s appearance seems to transform subtly with their emotional state, never quite the same twice."
    ]
    
    mountain_lake_templates = [
        f"{name} carries themselves with a stillness that suggests inner depths.",
        f"{name}'s reflective eyes seem to mirror the soul of whoever they're speaking with.",
        f"There's a balanced quality to {name}'s features, suggesting harmony between opposing forces."
    ]
    
    thunder_wind_templates = [
        f"{name}'s sudden movements and expressions can startle those around them.",
        f"There's a subtle, persistent quality to {name}'s presence that slowly influences any environment.",
        f"{name} has a voice that can shift from whisper-soft to commanding depending on their purpose."
    ]
    
    # Map hexagram numbers to template categories
    hexagram_num = hexagram_details["primary"]["number"]
    if hexagram_num in [1, 2, 11, 12, 26, 27]:
        templates = heaven_earth_templates
    elif hexagram_num in [29, 30, 63, 64, 39, 40]:
        templates = water_fire_templates
    elif hexagram_num in [52, 58, 15, 16, 23, 24]:
        templates = mountain_lake_templates
    elif hexagram_num in [51, 57, 53, 54, 55, 56]:
        templates = thunder_wind_templates
    else:
        # Default mix of templates
        templates = heaven_earth_templates + water_fire_templates + mountain_lake_templates + thunder_wind_templates
    
    # Select base appearance
    appearance = random.choice(templates)
    
    # Add emotional overlay
    emotion_appearances = {
        "Joy": f" Their features often light up with subtle warmth, and they tend to lean slightly forward when engaged.",
        "Trust": f" There's an openness to their gaze that invites confidence, and their hands are often relaxed and open.",
        "Fear": f" Despite their composure, their eyes frequently scan their surroundings, and they position themselves with clear sight lines to exits.",
        "Surprise": f" Their eyebrows are expressive and often raised, and they have a habit of tilting their head when processing new information.",
        "Sadness": f" A touch of melancholy softens their features, and they sometimes seem to be looking at something distant rather than what's before them.",
        "Boredom": f" Their gaze frequently drifts, and there's often a slight delay before they respond, as if returning from somewhere else.",
        "Anger": f" A certain tension radiates from their jaw and hands, and their movements tend to be more deliberate and controlled than casual.",
        "Interest": f" They lean in when listening and their eyes widen slightly when encountering new ideas or information."
    }
    
    appearance += emotion_appearances.get(emotion_primary, "")
    
    # Add distinctive feature based on hexagram
    distinctive_features = [
        f" A unique {get_hexagram_marker(hexagram_num)} pattern marks their {random.choice(['right hand', 'left wrist', 'neck', 'shoulder'])}.",
        f" They always carry a small {get_hexagram_object(hexagram_num)} that they touch when deep in thought.",
        f" Their {random.choice(['hair', 'eyes', 'voice', 'gestures'])} has a distinctive quality that subtly references {hexagram_details['primary']['name']}."
    ]
    
    appearance += random.choice(distinctive_features)
    
    return appearance

def get_hexagram_marker(hexagram_num):
    """Return an appropriate symbol or pattern for a hexagram."""
    categories = {
        "spiral": [1, 2, 11, 12, 24, 44],
        "wave": [5, 29, 59, 60, 40, 64],
        "branching": [42, 22, 27, 28, 53, 54],
        "geometric": [7, 15, 16, 51, 52, 62],
        "celestial": [30, 55, 37, 63, 56, 31],
        "natural": [33, 34, 48, 49, 57, 58]
    }
    
    for pattern, numbers in categories.items():
        if hexagram_num in numbers:
            return pattern
    
    return random.choice(["intricate", "subtle", "distinctive", "unusual"])

def get_hexagram_object(hexagram_num):
    """Return an appropriate symbolic object for a hexagram."""
    objects = {
        1: "crystal", 2: "clay token", 3: "sprouting seed", 4: "small mirror",
        5: "hourglass", 6: "balanced scales", 7: "compass", 8: "knotted cord",
        9: "magnifying lens", 10: "amber stone", 11: "harmonious chime", 12: "withered leaf",
        13: "brotherhood token", 14: "wealth token", 15: "plain stone", 16: "musical pipe",
        17: "follower's badge", 18: "restoration tool", 19: "approach map", 20: "viewing lens",
        21: "justice token", 22: "ornate emblem", 23: "cracked stone", 24: "renewal token",
        25: "innocence token", 26: "power restraint", 27: "nourishment vessel", 28: "support beam",
        29: "water vial", 30: "fire emblem", 31: "attraction token", 32: "endurance medal",
        33: "retreat map", 34: "strength token", 35: "dawn emblem", 36: "hidden light",
        37: "family crest", 38: "opposition token", 39: "obstacle fragment", 40: "liberation key",
        41: "reduction tool", 42: "increase token", 43: "breakthrough implement", 44: "encounter token",
        45: "gathering symbol", 46: "climbing tool", 47: "pressure stone", 48: "well token",
        49: "revolution emblem", 50: "cauldron fragment", 51: "thunder stone", 52: "meditation token",
        53: "development plan", 54: "temporary badge", 55: "abundance symbol", 56: "traveler's token",
        57: "wind chime", 58: "joy emblem", 59: "dispersal token", 60: "boundary marker",
        61: "truth token", 62: "detail lens", 63: "completion seal", 64: "threshold token"
    }
    
    return objects.get(hexagram_num, "symbolic token")

@mcp.tool()
async def iching_character_generator(
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generates a character based on I Ching hexagram divination combined with emotional attributes.
    
    Args:
        seed: Optional seed for the random generator for reproducible results
        
    Returns:
        Dictionary with generated character and their attributes
    """
    logger.info(f"I Ching character generator called with seed={seed}")
    
    # Set seed if provided
    if seed is not None:
        random.seed(seed)
        logger.info(f"Using seed: {seed}")
    
    try:
        # Step 1: Cast I Ching hexagram
        logger.info("Casting I Ching hexagram")
        hexagram_casting = cast_hexagram()
        hexagram_details = get_hexagram_details(hexagram_casting)
        
        # Log hexagram results
        logger.info(f"Primary hexagram: {hexagram_details['primary']['number']} - {hexagram_details['primary']['name']}")
        if hexagram_details['transformed']:
            logger.info(f"Transformed hexagram: {hexagram_details['transformed']['number']} - {hexagram_details['transformed']['name']}")
        logger.info(f"Changing lines: {hexagram_details['changing_lines']}")
        
        # Step 2: Generate character name
        char_name = generate_character_name()
        logger.info(f"Generated character name: {char_name}")
        
        # Step 3: Select emotions influenced by hexagram
        # Map certain hexagram types to emotions
        hexagram_emotion_affinities = {
            "water": ["Sadness", "Fear"],
            "fire": ["Joy", "Anger"],
            "earth": ["Trust", "Boredom"],
            "heaven": ["Interest", "Surprise"],
            "mountain": ["Boredom", "Trust"],
            "lake": ["Joy", "Interest"],
            "thunder": ["Surprise", "Anger"],
            "wind": ["Interest", "Fear"]
        }
        
        # Determine hexagram type based on number
        hexagram_types = {
            "water": [29, 5, 60, 40, 64],
            "fire": [30, 35, 56, 63, 37],
            "earth": [2, 23, 12, 16, 45],
            "heaven": [1, 44, 14, 43, 33],
            "mountain": [52, 4, 18, 46, 26],
            "lake": [58, 47, 48, 49, 31],
            "thunder": [51, 55, 54, 62, 32],
            "wind": [57, 53, 50, 28, 61]
        }
        
        hexagram_type = None
        for type_name, numbers in hexagram_types.items():
            if hexagram_details["primary"]["number"] in numbers:
                hexagram_type = type_name
                break
        
        if hexagram_type and hexagram_type in hexagram_emotion_affinities:
            preferred_emotions = hexagram_emotion_affinities[hexagram_type]
            primary_emotion = random.choice(preferred_emotions)
            # 50% chance to select secondary from preferred, otherwise random
            if random.random() < 0.5:
                secondary_emotion = random.choice(preferred_emotions)
            else:
                secondary_emotion = random.choice(EMOTIONS)
        else:
            # Fallback to completely random emotions
            primary_emotion = random.choice(EMOTIONS)
            secondary_emotion = random.choice(EMOTIONS)
        
        logger.info(f"Selected emotions - Primary: {primary_emotion}, Secondary: {secondary_emotion}")
        
        # Step 4: Select trait and quirk
        # 50% chance to select trait from hexagram traits
        if random.random() < 0.5 and hexagram_details["traits"]:
            trait = random.choice(hexagram_details["traits"])
        else:
            trait = random.choice(TRAITS)
            
        quirk = random.choice(QUIRKS)
        logger.info(f"Selected trait: {trait}, quirk: {quirk}")
        
        # Step 5: Generate narrative elements
        emotional_narrative = generate_emotional_narrative(primary_emotion, secondary_emotion, char_name, trait)
        origin_story = generate_origin_story(char_name, hexagram_details)
        appearance = generate_appearance(char_name, hexagram_details, primary_emotion, secondary_emotion)
        
        # Step 6: Assemble character data
        character = {
            "id": f"CHAR_{random.randint(1000, 9999)}",
            "name": char_name,
            "emotional_state": {
                "primary": primary_emotion,
                "secondary": secondary_emotion
            },
            "trait": trait,
            "quirk": quirk,
            "hexagram": {
                "current": hexagram_details["primary"]["name"],
                "meaning": hexagram_details["primary"]["meaning"],
                "becoming": hexagram_details["transformed"]["name"] if hexagram_details["transformed"] else None,
                "changing_lines": hexagram_details["changing_lines"]
            },
            "abilities": hexagram_details["abilities"],
            "philosophy": hexagram_details["philosophy"],
            "narrative": emotional_narrative,
            "origin": origin_story,
            "appearance": appearance
        }
        
        logger.info(f"Successfully generated I Ching character: {char_name}")
        
        return {
            "success": True,
            "character": character,
            "hexagram_casting": {
                "primary": hexagram_details["primary"]["number"],
                "primary_name": hexagram_details["primary"]["name"],
                "transformed": hexagram_details["transformed"]["number"] if hexagram_details["transformed"] else None,
                "transformed_name": hexagram_details["transformed"]["name"] if hexagram_details["transformed"] else None,
                "changing_lines": hexagram_details["changing_lines"]
            }
        }
    
    except Exception as e:
        logger.error(f"Character generation failed: {str(e)}")
        return {
            "success": False,
            "error": "Character generation failed",
            "reason": str(e)
        }

if __name__ == "__main__":
    logger.info("Starting I Ching Character Generator MCP server")
    mcp.run(transport='stdio')