import streamlit as st
import random
import json
from dotenv import load_dotenv
import os
import google.generativeai as genai
from dataclasses import dataclass
from typing import List, Dict, Any
import datetime

# Configuration class
@dataclass
class Config:
    MODEL_NAME: str = "gemini-1.5-pro-latest"
    MAX_CONTEXT_LENGTH: int = 1048576
    MAX_OUTPUT_TOKENS: int = 8192
    ROUNDS_PER_GAME: int = 5

# Load environment variables
load_dotenv(override=True)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize Gemini model
model = genai.GenerativeModel(
    Config.MODEL_NAME,
    generation_config={
        'temperature': 0.7,
        'top_p': 0.8,
        'top_k': 40,
        'max_output_tokens': Config.MAX_OUTPUT_TOKENS
    }
)

# Page configuration
st.set_page_config(
    page_title="SWA Crew Quest: Trivia & Training",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .scenario-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .game-stats {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .chip {
        padding: 5px 15px;
        border-radius: 16px;
        display: inline-block;
        margin: 2px;
        font-size: 14px;
    }
    .chip-correct {
        background-color: #4caf50;
        color: white;
    }
    .chip-incorrect {
        background-color: #f44336;
        color: white;
    }
    .chip-context {
        background-color: #2196f3;
        color: white;
    }
    .chip-difficulty {
        background-color: #ff9800;
        color: white;
    }
    .question-summary {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Fallback scenarios in case of API issues
FALLBACK_SCENARIOS = [
    {
        "scenario": "During boarding, a passenger is struggling with an oversized bag while others wait",
        "context": "Boarding",
        "difficulty": "Easy",
        "points": 5,
        "options": [
            {"text": "Offer to gate-check the bag for free", "is_correct": True},
            {"text": "Let them keep trying while the line builds up", "is_correct": False},
            {"text": "Tell them they have to check it at the counter", "is_correct": False}
        ],
        "explanation": "Offering free gate-check keeps boarding moving and maintains good customer service."
    },
    # Add more fallback scenarios here...
]
    

class GameManager:
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize all session state variables"""
        if 'game_active' not in st.session_state:
            st.session_state.game_active = False
        if 'current_round' not in st.session_state:
            st.session_state.current_round = 0
        if 'total_score' not in st.session_state:
            st.session_state.total_score = 0
        if 'player_name' not in st.session_state:
            st.session_state.player_name = ""
        if 'game_history' not in st.session_state:
            st.session_state.game_history = []
        if 'leaderboard' not in st.session_state:
            st.session_state.leaderboard = []
        if 'current_scenario' not in st.session_state:
            st.session_state.current_scenario = None
        if 'showing_answer' not in st.session_state:
            st.session_state.showing_answer = False
        if 'player_role' not in st.session_state:
            st.session_state.player_role = "Any"  # Default to "Any" if no role selected
        if 'show_about' not in st.session_state:
            st.session_state.show_about = False
        if 'topic_categories' not in st.session_state:
            st.session_state.topic_categories = {
                'customer_service': [],
                'operations': [],
                'culture': [],
                'history': [],
                'technical': [],
                'fun_moments': [],
                'problem_solving': [],
                'teamwork': [],
                'leadership': [],
                'innovation': []
            }

    def generate_scenario(self):
        """Generate a new unique scenario or airline trivia question using Gemini"""
        is_trivia = random.choice([True, False])
        
        # Get selected role from session state
        selected_role = st.session_state.player_role
        
        # Add role-specific context to the prompt if a specific role was selected
        role_context = ""
        if selected_role != "Any Role":
            role_context = f"""
            Focus on scenarios and questions specifically relevant to a {selected_role}.
            Make sure the situations and questions are realistic and appropriate for this role.
            Include role-specific terminology and procedures when applicable.
            """
        
        # Get least used categories
        used_counts = {cat: len(topics) for cat, topics in st.session_state.topic_categories.items()}
        min_count = min(used_counts.values())
        available_categories = [cat for cat, count in used_counts.items() if count == min_count]
        selected_category = random.choice(available_categories)
        
        if is_trivia:
            prompt = f"""
            Generate an interesting aviation trivia question for category: {selected_category}
            {role_context}

            Focus areas for this category:
            - For customer_service: Unique passenger interactions, creative solutions
            - For operations: Airport procedures, flight planning, scheduling
            - For culture: Airline traditions, company values, celebrations
            - For history: Airline milestones, industry developments
            - For technical: Aircraft systems, aviation technology
            - For fun_moments: Memorable flights, special events
            - For problem_solving: Creative solutions, quick thinking
            - For teamwork: Crew coordination, ground cooperation
            - For leadership: Captain decisions, crew management
            - For innovation: New procedures, industry firsts

            Requirements:
            1. Make it engaging, unique, and educational
            2. Provide three distinct answer options
            3. Include surprising facts in the explanation
            4. Add three fascinating aviation fun facts
            
            Return as JSON:
            {{
                "scenario": "Your trivia question",
                "context": "Category context",
                "category": "{selected_category}",
                "difficulty": "Easy/Medium/Hard",
                "points": number 5-15,
                "options": [
                    {{"text": "option 1", "is_correct": true/false}},
                    {{"text": "option 2", "is_correct": true/false}},
                    {{"text": "option 3", "is_correct": true/false}}
                ],
                "explanation": "Detailed explanation",
                "fun_facts": [
                    "fact 1",
                    "fact 2",
                    "fact 3"
                ]
            }}
            """
        else:
            prompt = f"""
            Generate a unique crew scenario for category: {selected_category}
            {role_context}

            Focus areas for this category:
            - For customer_service: Unique passenger situations, special requests
            - For operations: Unusual flight situations, ground operations
            - For culture: Team building, company values in action
            - For history: Using experience in current situations
            - For technical: Handling equipment, system operations
            - For fun_moments: Creating special memories, celebrations
            - For problem_solving: Unexpected challenges, creative solutions
            - For teamwork: Crew cooperation, department coordination
            - For leadership: Guiding others, making decisions
            - For innovation: Trying new approaches, improvements

            Requirements:
            1. Create an engaging scenario not previously used
            2. Make it realistic but interesting
            3. Provide three distinct response options
            4. Include practical learning in explanation
            5. Add three fascinating aviation fun facts
            
            Return as JSON:
            {{
                "scenario": "Your unique scenario",
                "context": "Category context",
                "category": "{selected_category}",
                "difficulty": "Easy/Medium/Hard",
                "points": number 5-15,
                "options": [
                    {{"text": "option 1", "is_correct": true/false}},
                    {{"text": "option 2", "is_correct": true/false}},
                    {{"text": "option 3", "is_correct": true/false}}
                ],
                "explanation": "Detailed explanation",
                "fun_facts": [
                    "fact 1",
                    "fact 2",
                    "fact 3"
                ]
            }}
            """

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                scenario_str = response.text.strip()
                scenario_str = scenario_str.replace("```json", "").replace("```", "").strip()
                scenario = json.loads(scenario_str)
                
                # Add the scenario to its category
                category = scenario.get('category', selected_category)
                st.session_state.topic_categories[category].append(scenario['scenario'])
                
                # Randomly shuffle options
                options = scenario['options']
                random.shuffle(options)
                scenario['options'] = options
                
                # Add type flag to scenario
                scenario['is_trivia'] = is_trivia
                return scenario
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # If all attempts fail, create a basic scenario from templates
                    return self.generate_fallback_scenario(selected_category, is_trivia)
                continue
                
        return self.generate_fallback_scenario(selected_category, is_trivia)

    def generate_fallback_scenario(self, category, is_trivia):
        """Generate a basic scenario based on templates if API fails"""
        templates = {
            'customer_service': {
                'scenario': f"A passenger requests a unique accommodation during {random.choice(['boarding', 'the flight', 'deplaning'])}",
                'options': [
                    {"text": "Address their needs with a creative solution", "is_correct": True},
                    {"text": "Refer them to another department", "is_correct": False},
                    {"text": "Explain why it's not possible", "is_correct": False}
                ]
            },
            'operations': {
                'scenario': f"An unexpected {random.choice(['weather change', 'schedule adjustment', 'equipment issue'])} requires quick thinking",
                'options': [
                    {"text": "Implement efficient backup plan", "is_correct": True},
                    {"text": "Continue with original plan", "is_correct": False},
                    {"text": "Wait for further instructions", "is_correct": False}
                ]
            },
            'culture': {
                'scenario': f"An opportunity arises to demonstrate SWA's {random.choice(['spirit', 'values', 'culture'])} during a flight",
                'options': [
                    {"text": "Create a memorable moment", "is_correct": True},
                    {"text": "Focus on routine tasks", "is_correct": False},
                    {"text": "Let someone else handle it", "is_correct": False}
                ]
            }
        }
        
        # If category not in templates, use random template
        template = templates.get(category, random.choice(list(templates.values())))
        
        scenario = {
            'scenario': template['scenario'],
            'context': category.replace('_', ' ').title(),
            'category': category,
            'difficulty': 'Medium',
            'points': 10,
            'options': template['options'],
            'explanation': "The best approach is to be proactive and solution-oriented while maintaining Southwest's values.",
            'fun_facts': [
                "Southwest Airlines was the first airline to offer profit-sharing to employees in 1973",
                "The average flight attendant walks about 5 miles during each flight",
                "Southwest's first flight took off from Dallas Love Field in 1971"
            ],
            'is_trivia': is_trivia
        }
        
        return scenario

    def display_scenario(self, scenario):
        """Display the current scenario or trivia with enhanced visuals"""
        is_trivia = scenario.get('is_trivia', False)
        icon = "🎯" if is_trivia else "✈️"
        title = "Aviation Trivia" if is_trivia else f"Scenario {st.session_state.current_round}"
        category = scenario.get('category', '').replace('_', ' ').title()
        
        st.markdown(
            f"""
            <div class="scenario-box">
                <span class="chip chip-context">{scenario['context']}</span>
                <span class="chip chip-difficulty">{scenario['difficulty']}</span>
                <h3>{icon} {title}</h3>
                <h4>Category: {category}</h4>
                <p>{scenario['scenario']}</p>
                <p><strong>Points possible: {scenario['points']}</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        options = [option['text'] for option in scenario['options']]
        choice = st.radio("Select your answer:", options)
        return choice

    def process_answer(self, scenario, choice):
        """Process the answer and display feedback with fun facts that are also true and accurate to SWA or the aviation industry"""
        for option in scenario['options']:
            if option['text'] == choice:
                is_correct = option['is_correct']
                points = scenario['points'] if is_correct else 0
                
                if is_correct:
                    st.success(f"✅ Correct! You earned {points} points!", icon="🎯")
                else:
                    correct_answer = next(opt['text'] for opt in scenario['options'] if opt['is_correct'])
                    st.error("❌ Not quite right.", icon="⚠️")
                    st.warning(f"The correct answer was: {correct_answer}")
                
                st.info(f"📝 Explanation: {scenario['explanation']}")
                
                with st.expander("🎨 Fun Aviation Facts"):
                    for i, fact in enumerate(scenario['fun_facts'], 1):
                        st.markdown(f"**Fact {i}:** {fact}")
                        
                # Add delay to ensure user can read feedback
                st.empty().markdown("---")
                
                return points, is_correct, scenario['explanation']
                
        return 0, False, "Error processing answer"

    def display_game_stats(self):
        """Display current game statistics"""
        role_display = f"Role: {st.session_state.player_role} | " if st.session_state.player_role != "Any Role" else ""
        st.markdown(
            f"""
            <div class="game-stats">
                <h3>✈️ Flight Log</h3>
                <p>
                    Round: {st.session_state.current_round}/{Config.ROUNDS_PER_GAME} | 
                    Score: {st.session_state.total_score} points | 
                    {role_display}
                    Player: {st.session_state.player_name}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    def display_game_summary(self):
        """Display end-game summary with enhanced visuals"""
        st.markdown("## Game Summary")
        st.markdown(f"**Final Score: {st.session_state.total_score} points**")
        
        for idx, round_data in enumerate(st.session_state.game_history, 1):
            with st.expander(f"Round {idx} - {round_data['context']}"):
                st.markdown(
                    f"""
                    <div class="question-summary">
                        <span class="chip chip-context">{round_data['context']}</span>
                        <span class="chip chip-difficulty">{round_data['difficulty']}</span>
                        <p><strong>Scenario:</strong> {round_data['scenario']}</p>
                        <p><strong>Your Answer:</strong> {round_data['player_choice']}</p>
                        <p><strong>Correct Answer:</strong> {round_data['correct_answer']}</p>
                        <p><strong>Points Earned:</strong> {round_data['points']}/{round_data['possible_points']}</p>
                        <p><strong>Explanation:</strong> {round_data['explanation']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    def update_leaderboard(self):
        """Update the leaderboard with current game results"""
        st.session_state.leaderboard.append({
            "name": st.session_state.player_name,
            "score": st.session_state.total_score,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        st.session_state.leaderboard.sort(key=lambda x: x["score"], reverse=True)
        st.session_state.leaderboard = st.session_state.leaderboard[:10]    
    
    
        
def main():
    game = GameManager()
    
    st.title("✈️ SWA Crew Quest: Trivia & Training")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ✈️ Freedom One: The First SWA 737-800")
        st.markdown("## Source: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Freedom_one.png)")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Freedom_one.png/320px-Freedom_one.png", width=200)
        st.markdown("### 🏆 Top Performers")
        for idx, entry in enumerate(st.session_state.leaderboard[:5], 1):
            st.write(f"{idx}. {entry['name']}: {entry['score']} pts ({entry['date']})")
            
        st.markdown("---")  # Adds a separator line
        st.markdown("### 🌟 ✈️ About This App ❤️ 🎯")
        
        # Toggle button with dynamic text
        button_text = "✨ Hide About SWA Crew Quest ✨" if st.session_state.show_about else "✨ Learn More About SWA Crew Quest ✨"
        if st.button(button_text, key="about_button"):
            st.markdown("""
                <style>
                    .about-box {
                        background-color: #f0f2f6;
                        padding: 20px;
                        border-radius: 10px;
                        border: 2px solid #1e88e5;
                        margin: 10px 0;
                        animation: fadeIn 0.5s;
                    }
                    @keyframes fadeIn {
                        from { opacity: 0; }
                        to { opacity: 1; }
                    }
                    .developer-note {
                        margin-top: 15px;
                        padding-top: 15px;
                        border-top: 1px solid #1e88e5;
                    }
                </style>
                <div class="about-box">
                <p>Welcome to SWA Crew Quest: Trivia & Training—a heartfelt tribute to Southwest Airlines' dedicated team members who make every flight special.</p>
                
                <p>Through engaging scenarios and trivia, we celebrate the professionalism, humor, and hospitality that helps SWA safely transport over 137 million passengers each year.</p>
                
                <p>Thank you for your unwavering dedication to excellence and for making every journey memorable.</p>
                
                <p>👨‍👩‍👧‍👦 ✈️ Your Happy and Thankful SWA Passengers 🙏 💝</p>

                <div class="developer-note">
                <p>✨ Developed by Lindsay Hiebert, a Generative AI expert creating outcomes that focus on the health, happiness, and growth of people—just like every member of the SWA team.</p>
                
                <p>💡 Connect with me on <a href="https://www.linkedin.com/in/lindsayhiebert/" target="_blank" style="color: #1e88e5;">LinkedIn</a> for feedback or to learn more about AI solutions that make a difference.</p>
                </div>
                </div>
            """, unsafe_allow_html=True)
            st.session_state.show_about = not st.session_state.show_about

            
    if st.session_state.game_active:
        game.display_game_stats()
    
    if not st.session_state.game_active:
        st.markdown("""
        ### Welcome to a New Day of SWA Experience! 
        
        Test your skills in handling real-world situations across 5 unique and challenging scenarios.
        Show us you've got the Southwest Spirit! ✨
        """)
        
        name = st.text_input("Enter your name:", key="name_input")
        
        # Add this new section for role selection
        cols = st.columns([2, 1])  # Create two columns for layout
        with cols[0]:
            role = st.selectbox(
                "Choose your role (Optional):",
                [
                    "Any Role",
                    "Flight Attendant",
                    "Pilot",
                    "Ground Operations",
                    "Customer Service Agent",
                    "Operations Agent"
                ],
                index=0,  # Default to "Any Role"
                help="Select your SWA role to get role-specific scenarios!"
            )       
             
        with cols[1]:
            if st.button("Start Your Challenge! ✈️"):
                if name.strip():
                    st.session_state.player_name = name
                    st.session_state.player_role = role
                    st.session_state.game_active = True
                    st.session_state.current_round = 1
                    st.session_state.total_score = 0
                    st.session_state.game_history = []
                    st.rerun()
                else:
                    st.warning("Please enter your name to begin!")


    elif st.session_state.current_round <= Config.ROUNDS_PER_GAME:
        if st.session_state.current_scenario is None:
            st.session_state.current_scenario = game.generate_scenario()
        
        choice = game.display_scenario(st.session_state.current_scenario)
        
        if st.button("Submit Answer"):
            points, is_correct, explanation = game.process_answer(
                st.session_state.current_scenario, choice
            )
            st.session_state.total_score += points
            
            # Record round history
            st.session_state.game_history.append({
                "round": st.session_state.current_round,
                "context": st.session_state.current_scenario['context'],
                "difficulty": st.session_state.current_scenario['difficulty'],
                "scenario": st.session_state.current_scenario['scenario'],
                "player_choice": choice,
                "correct_answer": next(opt['text'] for opt in st.session_state.current_scenario['options'] if opt['is_correct']),
                "points": points,
                "possible_points": st.session_state.current_scenario['points'],
                "explanation": explanation
            })
            
            # Display immediate feedback
            if is_correct:
                st.success(f"Correct! You earned {points} points!")
            else:
                st.error("Not quite right. No points awarded.")
            st.info(f"Explanation: {explanation}")
            
            st.session_state.current_round += 1
            st.session_state.current_scenario = None
            
            if st.session_state.current_round <= Config.ROUNDS_PER_GAME:
                if st.button("Next Scenario"):
                    st.rerun()
            else:
                game.update_leaderboard()
                st.rerun()

    else:
        st.balloons()
        game.display_game_summary()
        
        if st.button("Start New Game"):
            st.session_state.game_active = False
            st.rerun()

if __name__ == "__main__":
    main()