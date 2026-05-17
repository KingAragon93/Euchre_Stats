"""
Euchre Stats - A Streamlit app for tracking and analyzing Euchre games.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import database_firestore as db
import analytics
from models import COMMON_CALL_VALUES

# Helper to scroll to top of page (call this at start of page to check if scroll needed)
def check_scroll_to_top():
    """Check if we should scroll to top and do it."""
    if st.session_state.get('scroll_to_top', False):
        st.session_state['scroll_to_top'] = False
        components.html(
            """
            <script>
                window.parent.document.querySelector('section.main').scrollTo({top: 0, behavior: 'instant'});
            </script>
            """,
            height=0
        )

def trigger_scroll_to_top():
    """Set flag to scroll to top on next rerun."""
    st.session_state['scroll_to_top'] = True

# Initialize database connection
db.init_database()

# Page config
st.set_page_config(
    page_title="Euchre Stats",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern dark theme CSS
st.markdown("""
<style>
    :root {
        --accent: #6366f1;
        --accent-hover: #818cf8;
        --bg: #0b0d12;
        --surface: #161922;
        --surface-2: #1e2230;
        --border: #2a2f3d;
        --text: #e6e8ee;
        --text-muted: #8a92a6;
    }

    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
        background: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #fff !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #fff !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
    }

    .score-display {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: -0.02em;
    }

    .team-score {
        padding: 1.25rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        background: var(--surface);
        border: 1px solid var(--border);
    }

    .team-score.team-accent {
        border-left: 4px solid var(--accent);
    }

    .team-score.team-secondary {
        border-left: 4px solid #14b8a6;
    }

    .winner-banner {
        background: linear-gradient(135deg, #6366f1, #14b8a6);
        padding: 1.25rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1rem 0;
        color: white;
        letter-spacing: -0.01em;
    }

    .page-header {
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        margin-bottom: 1.5rem;
    }

    .page-header h1, .page-header h2 {
        margin: 0;
        font-weight: 600;
        letter-spacing: -0.02em;
    }

    .page-header p {
        margin: 0.4rem 0 0 0;
        color: var(--text-muted);
        font-size: 0.95rem;
    }

    .game-time {
        font-size: 0.85rem;
        color: var(--text-muted);
    }

    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("### 🃏 Euchre Stats")
st.sidebar.caption("Track. Visualize. Win.")
st.sidebar.markdown("---")

# Navigation options
nav_options = ["🏠 Home", "➕ New Game", "🎮 Active Games", "🏆 Finished Games", "📊 Statistics"]

# Check if we need to navigate to a specific page (before rendering radio)
if 'nav_to' in st.session_state:
    st.session_state['nav_radio'] = st.session_state['nav_to']
    del st.session_state['nav_to']

page = st.sidebar.radio(
    "Navigate",
    nav_options,
    key="nav_radio"
)

st.sidebar.markdown("---")


def format_game_time(iso_time: str) -> str:
    """Format ISO time string to readable format."""
    try:
        dt = datetime.fromisoformat(iso_time)
        return dt.strftime("%b %d, %Y @ %I:%M %p")
    except:
        return iso_time


def home_page():
    """Display home page with overview."""
    st.markdown("""
    <div class="page-header">
        <h1>🃏 Euchre Stats</h1>
        <p>Track, visualize, and analyze your Euchre games with custom house rules.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    stats = analytics.get_all_games_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎮 Total Games", stats['total_games'])
    with col2:
        st.metric("▶️ Active Games", stats['active_games'])
    with col3:
        st.metric("🏆 Finished Games", stats['finished_games'])
    with col4:
        st.metric("🃏 Total Hands", stats['total_hands'])
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Start New Game", use_container_width=True):
            st.session_state['nav_to'] = "➕ New Game"
            st.rerun()
    with col2:
        active = db.get_active_games()
        if active:
            if st.button(f"🎮 Continue Game ({len(active)} active)", use_container_width=True):
                st.session_state['nav_to'] = "🎮 Active Games"
                st.rerun()
    
    # Recent games
    st.subheader("🕐 Recent Games")
    games = db.get_all_games()[:5]
    if games:
        for game in games:
            status_emoji = "🎮" if game['status'] == 'active' else "🏆"
            game_time = format_game_time(game['created_at'])
            with st.expander(f"{status_emoji} {game['team1_name']} vs {game['team2_name']} ({game['team1_score']}-{game['team2_score']}) - {game_time}"):
                st.markdown(f"🕐 **Started:** {game_time}")
                st.write(f"**Status:** {game['status'].title()}")
                st.write(f"**Target:** {game['target_score']} points")
                if game['winner']:
                    st.write(f"**Winner:** {game['winner']} 🎉")
    else:
        st.info("No games yet. Start a new game to begin tracking!")


def new_game_page():
    """Create a new game."""
    st.markdown("""
    <div class="page-header">
        <h2>➕ Start New Game</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("new_game_form"):
        st.subheader("Team 1")
        team1_name = st.text_input("Team 1 Name", value="Team 1")
        team1_players_str = st.text_area(
            "Team 1 Players (one per line)",
            placeholder="Alice\nBob\nCharlie"
        )
        
        st.subheader("Team 2")
        team2_name = st.text_input("Team 2 Name", value="Team 2")
        team2_players_str = st.text_area(
            "Team 2 Players (one per line)",
            placeholder="Dave\nEve\nFrank"
        )
        
        st.subheader("Game Settings")
        target_score = st.number_input("Target Score", min_value=1, value=32)
        
        submitted = st.form_submit_button("🎮 Start Game", use_container_width=True)
        
        if submitted:
            # Parse players
            team1_players = [p.strip() for p in team1_players_str.strip().split('\n') if p.strip()]
            team2_players = [p.strip() for p in team2_players_str.strip().split('\n') if p.strip()]
            
            if not team1_players or not team2_players:
                st.error("Both teams must have at least one player!")
            elif not team1_name or not team2_name:
                st.error("Both teams must have names!")
            else:
                game_id = db.create_game(
                    team1_name=team1_name,
                    team2_name=team2_name,
                    team1_players=team1_players,
                    team2_players=team2_players,
                    target_score=target_score
                )
                st.success(f"Game created! ID: {game_id}")
                st.session_state['active_game_id'] = game_id
                st.session_state['nav_to'] = "🎮 Active Games"
                st.rerun()


def active_games_page():
    """View and manage active games."""
    # Check if we need to scroll to top (after logging a hand)
    check_scroll_to_top()
    
    # Show success message if set
    if 'show_success' in st.session_state:
        st.success(st.session_state['show_success'])
        del st.session_state['show_success']
    
    @st.dialog("Confirm Delete")
    def confirm_delete_dialog(game_id):
        st.write("Are you sure you want to delete this game? This action cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Delete", type="primary", use_container_width=True):
                db.delete_game(game_id)
                st.session_state.pop('active_game_id', None)
                st.success("Game deleted!")
                st.rerun()
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.rerun()
    
    st.markdown("""
    <div class="page-header">
        <h2>🎮 Active Games</h2>
    </div>
    """, unsafe_allow_html=True)
    
    games = db.get_active_games()
    
    if not games:
        st.info("No active games. Start a new game!")
        if st.button("➕ Start New Game"):
            st.session_state['nav_to'] = "➕ New Game"
            st.rerun()
        return
    
    # Game selector with time
    game_options = {}
    for g in games:
        game_time = format_game_time(g['created_at'])
        label = f"{g['team1_name']} vs {g['team2_name']} ({g['team1_score']}-{g['team2_score']}) - {game_time}"
        game_options[label] = g['id']
    
    # Use session state to pre-select game if set
    default_idx = 0
    if 'active_game_id' in st.session_state:
        for i, g in enumerate(games):
            if g['id'] == st.session_state['active_game_id']:
                default_idx = i
                break
    
    selected_game_name = st.selectbox("Select Game", list(game_options.keys()), index=default_idx)
    game_id = game_options[selected_game_name]
    game = db.get_game(game_id)
    if not game:
        st.error("Game not found.")
        st.stop()
    
    # Store for next time
    st.session_state['active_game_id'] = game_id
    
    # Display game start time
    game_time = format_game_time(game['created_at'])
    st.markdown(f"🕐 **Game Started:** {game_time}")
    
    # Display current score
    st.subheader("📊 Current Score")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="team-score team-accent">
            <h3 style="margin: 0; font-weight: 600;">{game['team1_name']}</h3>
            <p class="score-display" style="margin: 0;">{game['team1_score']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="team-score team-secondary">
            <h3 style="margin: 0; font-weight: 600;">{game['team2_name']}</h3>
            <p class="score-display" style="margin: 0;">{game['team2_score']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption(f"Target: {game['target_score']} points")
    
    st.divider()
    
    # Check if there's a pending game-ending hand to confirm
    if 'pending_game_end' in st.session_state and st.session_state['pending_game_end'] is not None:
        pending = st.session_state['pending_game_end']
        
        # Only show if it's for the current game
        if pending['game_id'] == game_id:
            st.warning(f"🏆 **Game Over!** This hand would end the game!")
            st.markdown(f"**{pending['winner']}** wins with a score of **{pending['winning_score']} - {pending['losing_score']}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm End Game", use_container_width=True, type="primary"):
                    # Log the hand and finish the game
                    db.add_hand(
                        game_id=pending['game_id'],
                        caller_name=pending['caller_name'],
                        caller_team=pending['caller_team'],
                        call_value=pending['call_value'],
                        points_scored=pending['points_to_record'],
                        is_euchre=pending['is_euchre'],
                        other_team_points=pending['other_team_points'],
                        notes=pending['notes'],
                        auto_finish=True  # This will finish the game
                    )
                    st.session_state['pending_game_end'] = None
                    st.session_state['form_key'] = st.session_state.get('form_key', 0) + 1
                    st.session_state['caller_index'] = 0  # Reset caller to unassigned
                    st.balloons()
                    st.success(f"🎉 Game Over! {pending['winner']} wins!")
                    st.session_state['nav_to'] = "🏆 Finished Games"
                    st.rerun()
            
            with col2:
                if st.button("↩️ Cancel / Go Back", use_container_width=True):
                    st.session_state['pending_game_end'] = None
                    st.rerun()
            
            st.divider()
    
    # Log new hand
    st.subheader("📝 Log Hand")
    
    all_players = game['team1_players'] + game['team2_players']
    caller_options = ["Unassigned"] + all_players
    
    if 'caller_index' not in st.session_state:
        st.session_state['caller_index'] = 0
    
    selected_caller = st.selectbox("Caller", caller_options, index=st.session_state['caller_index'], key=f"caller_select_{st.session_state.get('form_key', 0)}")
    
    if selected_caller != "Unassigned":
        if selected_caller in game['team1_players']:
            selected_team = "team1"
            selected_team_name = game['team1_name']
        else:
            selected_team = "team2"
            selected_team_name = game['team2_name']
        st.info(f"Team: {selected_team_name}")
    else:
        selected_team = None
        st.info("Team: Unassigned")
    
    # Main hand entry form - use dynamic key to reset form after submission
    form_key = f"log_hand_form_{st.session_state.get('form_key', 0)}"
    with st.form(form_key, clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            call_value = st.selectbox("What Was Called", COMMON_CALL_VALUES + ["Other"])
            if call_value == "Other":
                call_value = st.text_input("Enter call value")
        
        with col2:
            # Points scored - if less than call value, it's a euchre
            points_scored = st.number_input("Points Scored by Caller", min_value=0, value=0)
        
        notes = st.text_input("Notes (optional)")
        
        submitted = st.form_submit_button("✅ Log Hand", use_container_width=True)
        
        if submitted:
            if selected_caller == "Unassigned":
                st.error("Please select a caller!")
            elif not call_value:
                st.error("Please select or enter a call value!")
            else:
                caller_name = selected_caller
                caller_team = selected_team
                # Parse call value to determine if it's a euchre
                # Special calls have specific point requirements
                if call_value == "Partner Best":
                    # For Partner Best, input is TRICKS (0-8), not points
                    # Must get all 8 tricks to succeed
                    tricks_gotten = points_scored  # Input is tricks, not points
                    is_euchre = tricks_gotten < 8
                    if is_euchre:
                        other_team_points = 8 - tricks_gotten
                        euchre_penalty = 16  # Caller loses 16 points
                    else:
                        other_team_points = 0
                        euchre_penalty = 0
                    # Record the actual points (tricks * 2 for success, or penalty for euchre)
                    points_to_record = euchre_penalty if is_euchre else 16
                elif call_value == "Alone":
                    # For Alone, input is also TRICKS (0-8)
                    tricks_gotten = points_scored
                    is_euchre = tricks_gotten < 8
                    if is_euchre:
                        other_team_points = 8 - tricks_gotten
                        euchre_penalty = 8  # Caller loses 8 points
                    else:
                        other_team_points = 0
                        euchre_penalty = 0
                    points_to_record = euchre_penalty if is_euchre else 8
                else:
                    try:
                        call_value_int = int(call_value)
                    except ValueError:
                        # Unknown call type, default to requiring the points entered
                        call_value_int = points_scored  # No euchre detection
                    
                    # Detect euchre: if points scored < call value
                    is_euchre = points_scored < call_value_int
                    
                    if is_euchre:
                        # Other team gets (8 - points_scored)
                        other_team_points = 8 - points_scored
                        euchre_penalty = call_value_int  # Caller loses what they called
                    else:
                        other_team_points = 0
                        euchre_penalty = 0
                    
                    # For euchre, pass the penalty as points_scored (what caller loses)
                    # For normal hands, pass the actual points scored
                    points_to_record = euchre_penalty if is_euchre else points_scored
                
                # Calculate what the new scores would be
                if is_euchre:
                    if caller_team == "team1":
                        new_team1_score = game['team1_score'] - points_to_record
                        new_team2_score = game['team2_score'] + other_team_points
                    else:
                        new_team1_score = game['team1_score'] + other_team_points
                        new_team2_score = game['team2_score'] - points_to_record
                else:
                    if caller_team == "team1":
                        new_team1_score = game['team1_score'] + points_to_record
                        new_team2_score = game['team2_score']
                    else:
                        new_team1_score = game['team1_score']
                        new_team2_score = game['team2_score'] + points_to_record
                
                # Check if this hand would end the game
                target = game['target_score']
                would_end_game = new_team1_score >= target or new_team2_score >= target
                
                if would_end_game:
                    # Determine winner
                    if new_team1_score >= target:
                        potential_winner = game['team1_name']
                        winning_score = new_team1_score
                        losing_score = new_team2_score
                    else:
                        potential_winner = game['team2_name']
                        winning_score = new_team2_score
                        losing_score = new_team1_score
                    
                    # Store pending game-ending hand for confirmation
                    st.session_state['pending_game_end'] = {
                        'game_id': game_id,
                        'caller_name': caller_name,
                        'caller_team': caller_team,
                        'call_value': call_value,
                        'points_to_record': points_to_record,
                        'is_euchre': is_euchre,
                        'other_team_points': other_team_points,
                        'notes': notes if notes else None,
                        'winner': potential_winner,
                        'winning_score': winning_score,
                        'losing_score': losing_score
                    }
                    st.rerun()
                else:
                    # Normal hand - just log it
                    db.add_hand(
                        game_id=game_id,
                        caller_name=caller_name,
                        caller_team=caller_team,
                        call_value=call_value,
                        points_scored=points_to_record,
                        is_euchre=is_euchre,
                        other_team_points=other_team_points,
                        notes=notes if notes else None
                    )
                    st.session_state['form_key'] = st.session_state.get('form_key', 0) + 1
                    st.session_state['caller_index'] = 0  # Reset caller to unassigned
                    if is_euchre:
                        st.session_state['show_success'] = f"💥 Euchre! Caller loses {points_to_record}, other team gets {other_team_points}!"
                    else:
                        st.session_state['show_success'] = "✅ Hand logged!"
                    trigger_scroll_to_top()
                    st.rerun()
    
    st.divider()
    
    # Hand history
    st.subheader("📜 Hand History")
    hands_df = analytics.get_game_hands_df(game_id)
    if not hands_df.empty:
        st.dataframe(hands_df, use_container_width=True, hide_index=True)
        
        # Undo last hand
        if st.button("↩️ Undo Last Hand"):
            if db.delete_last_hand(game_id):
                st.success("Last hand removed!")
                st.rerun()
    else:
        st.info("No hands logged yet.")
    
    st.divider()
    
    # Score chart
    st.subheader("📈 Score by Round")
    score_df = analytics.get_game_score_history(game_id)
    if len(score_df) > 1:
        st.line_chart(
            score_df.set_index('hand_number'),
            use_container_width=True
        )
    
    st.divider()
    
    # Game actions
    col1, col2 = st.columns(2)
    with col2:
        if st.button("🗑️ Delete Game", type="secondary"):
            confirm_delete_dialog(game_id)


def finished_games_page():
    """View finished games."""
    
    @st.dialog("Confirm Delete")
    def confirm_delete_dialog(game_id):
        st.write("Are you sure you want to delete this game? This action cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Delete", type="primary", use_container_width=True):
                db.delete_game(game_id)
                st.success("Game deleted!")
                st.rerun()
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.rerun()
    
    st.markdown("""
    <div class="page-header">
        <h2>🏆 Finished Games</h2>
    </div>
    """, unsafe_allow_html=True)

    games = db.get_finished_games()

    if not games:
        st.info("No finished games yet.")
        return
    
    for game in games:
        game_time = format_game_time(game['created_at'])
        with st.expander(f"🏆 {game['winner']} wins! - {game['team1_name']} vs {game['team2_name']} ({game['team1_score']}-{game['team2_score']}) - {game_time}"):
            # Game time
            st.markdown(f"🕐 **Started:** {game_time}")
            if game['finished_at']:
                st.markdown(f"🏁 **Finished:** {format_game_time(game['finished_at'])}")
            
            # Winner banner
            st.markdown(f"""
            <div class="winner-banner">
                🏆 {game['winner']} Wins!
            </div>
            """, unsafe_allow_html=True)
            
            # Final score
            col1, col2 = st.columns(2)
            with col1:
                st.metric(game['team1_name'], game['team1_score'])
                st.write("**Players:**")
                for p in game['team1_players']:
                    st.write(f"  • {p}")
            with col2:
                st.metric(game['team2_name'], game['team2_score'])
                st.write("**Players:**")
                for p in game['team2_players']:
                    st.write(f"  • {p}")
            
            st.divider()
            
            # Score chart
            st.subheader("📈 Score Progression")
            score_df = analytics.get_game_score_history(game['id'])
            if len(score_df) > 1:
                st.line_chart(score_df.set_index('hand_number'), use_container_width=True)
            
            # Hand history
            st.subheader("📜 Hand Log")
            hands_df = analytics.get_game_hands_df(game['id'])
            if not hands_df.empty:
                st.dataframe(hands_df, use_container_width=True, hide_index=True)
            
            # Edit hand section - only show when checkbox is checked
            hands = db.get_hands(game['id'])
            if st.checkbox("✏️ Edit or Add Hand", key=f"show_edit_{game['id']}"):
                all_players = game['team1_players'] + game['team2_players']
                
                # Build options: existing hands + add new option
                hand_options = {f"Hand {h['hand_number']} - {h['caller_name']} called {h['call_value']}": h['id'] for h in hands}
                options_list = ["➕ Add New Hand"] + list(hand_options.keys())
                
                selected_option = st.selectbox(
                    "Select hand to edit or add new",
                    options=options_list,
                    key=f"edit_select_{game['id']}"
                )
                
                if selected_option == "➕ Add New Hand":
                    # Add new hand form
                    with st.form(key=f"add_hand_form_{game['id']}"):
                        st.markdown(f"**Adding Hand #{len(hands) + 1}**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_caller = st.selectbox("Caller", all_players, key=f"new_caller_{game['id']}")
                            
                            new_call_value = st.selectbox("What Was Called", COMMON_CALL_VALUES + ["Other"], key=f"new_call_{game['id']}")
                            if new_call_value == "Other":
                                new_call_value = st.text_input("Enter call value", key=f"new_call_other_{game['id']}")
                        
                        with col2:
                            new_points = st.number_input("Points Scored by Caller", min_value=0, value=0, key=f"new_points_{game['id']}")
                            
                            new_notes = st.text_input("Notes (optional)", key=f"new_notes_{game['id']}")
                        
                        if st.form_submit_button("➕ Add Hand", use_container_width=True, type="primary"):
                            if not new_call_value:
                                st.error("Please select or enter a call value!")
                            else:
                                # Determine caller team
                                if new_caller in game['team1_players']:
                                    caller_team = "team1"
                                else:
                                    caller_team = "team2"
                                
                                # Parse call value to determine if it's a euchre
                                # Special calls have specific point requirements
                                if new_call_value == "Partner Best":
                                    # For Partner Best, input is TRICKS (0-8), not points
                                    # Must get all 8 tricks to succeed
                                    tricks_gotten = new_points  # Input is tricks, not points
                                    is_euchre = tricks_gotten < 8
                                    if is_euchre:
                                        other_team_points = 8 - tricks_gotten
                                        euchre_penalty = 16  # Caller loses 16 points
                                    else:
                                        other_team_points = 0
                                        euchre_penalty = 0
                                    # Record the actual points (tricks * 2 for success, or penalty for euchre)
                                    points_to_record = euchre_penalty if is_euchre else 16
                                elif new_call_value == "Alone":
                                    # For Alone, input is also TRICKS (0-8)
                                    tricks_gotten = new_points
                                    is_euchre = tricks_gotten < 8
                                    if is_euchre:
                                        other_team_points = 8 - tricks_gotten
                                        euchre_penalty = 8  # Caller loses 8 points
                                    else:
                                        other_team_points = 0
                                        euchre_penalty = 0
                                    points_to_record = euchre_penalty if is_euchre else 8
                                else:
                                    try:
                                        call_value_int = int(new_call_value)
                                    except ValueError:
                                        # Unknown call type, default to requiring the points entered
                                        call_value_int = new_points  # No euchre detection
                                    
                                    # Detect euchre: if points scored < call value
                                    is_euchre = new_points < call_value_int
                                    
                                    if is_euchre:
                                        # Other team gets (8 - points_scored)
                                        other_team_points = 8 - new_points
                                        euchre_penalty = call_value_int  # Caller loses what they called
                                    else:
                                        other_team_points = 0
                                        euchre_penalty = 0
                                    
                                    # For euchre, pass the penalty as points_scored (what caller loses)
                                    # For normal hands, pass the actual points scored
                                    points_to_record = euchre_penalty if is_euchre else new_points
                                
                                db.add_hand(
                                    game_id=game['id'],
                                    caller_name=new_caller,
                                    caller_team=caller_team,
                                    call_value=new_call_value,
                                    points_scored=points_to_record,
                                    is_euchre=is_euchre,
                                    other_team_points=other_team_points,
                                    notes=new_notes if new_notes else None,
                                    auto_finish=False  # Don't auto-finish since we're editing a finished game
                                )
                                st.success(f"✅ Hand #{len(hands) + 1} added!")
                                st.rerun()
                
                else:
                    # Edit existing hand
                    selected_hand_id = hand_options[selected_option]
                    selected_hand = db.get_hand(selected_hand_id)
                    
                    if selected_hand:
                        with st.form(key=f"edit_hand_form_{game['id']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Find current caller index
                                caller_idx = all_players.index(selected_hand['caller_name']) if selected_hand['caller_name'] in all_players else 0
                                edit_caller = st.selectbox("Caller", all_players, index=caller_idx, key=f"edit_caller_{game['id']}")
                                
                                # For call value
                                call_options = COMMON_CALL_VALUES + ["Other"]
                                if selected_hand['call_value'] in call_options:
                                    call_idx = call_options.index(selected_hand['call_value'])
                                    edit_call_value = st.selectbox("What Was Called", call_options, index=call_idx, key=f"edit_call_{game['id']}")
                                else:
                                    edit_call_value = st.selectbox("What Was Called", call_options, index=len(call_options)-1, key=f"edit_call_{game['id']}")  # "Other"
                                if edit_call_value == "Other":
                                    edit_call_value = st.text_input("Enter call value", value=selected_hand['call_value'], key=f"edit_call_other_{game['id']}")
                            
                            with col2:
                                edit_points = st.number_input("Points Scored by Caller", min_value=0, value=selected_hand['points_scored'], key=f"edit_points_{game['id']}")
                                
                                edit_notes = st.text_input("Notes (optional)", value=selected_hand['notes'] or '', key=f"edit_notes_{game['id']}")
                            
                            if st.form_submit_button("💾 Update Hand", use_container_width=True):
                                if not edit_call_value:
                                    st.error("Please select or enter a call value!")
                                else:
                                    # Determine caller team
                                    if edit_caller in game['team1_players']:
                                        edit_caller_team = "team1"
                                    else:
                                        edit_caller_team = "team2"
                                    
                                    # Parse call value to determine if it's a euchre
                                    # Special calls have specific point requirements
                                    if edit_call_value == "Partner Best":
                                        # For Partner Best, input is TRICKS (0-8), not points
                                        # Must get all 8 tricks to succeed
                                        tricks_gotten = edit_points  # Input is tricks, not points
                                        is_euchre = tricks_gotten < 8
                                        if is_euchre:
                                            other_team_points = 8 - tricks_gotten
                                            euchre_penalty = 16  # Caller loses 16 points
                                        else:
                                            other_team_points = 0
                                            euchre_penalty = 0
                                        # Record the actual points (tricks * 2 for success, or penalty for euchre)
                                        points_to_record = euchre_penalty if is_euchre else 16
                                    elif edit_call_value == "Alone":
                                        # For Alone, input is also TRICKS (0-8)
                                        tricks_gotten = edit_points
                                        is_euchre = tricks_gotten < 8
                                        if is_euchre:
                                            other_team_points = 8 - tricks_gotten
                                            euchre_penalty = 8  # Caller loses 8 points
                                        else:
                                            other_team_points = 0
                                            euchre_penalty = 0
                                        points_to_record = euchre_penalty if is_euchre else 8
                                    else:
                                        try:
                                            call_value_int = int(edit_call_value)
                                        except ValueError:
                                            # Unknown call type, default to requiring the points entered
                                            call_value_int = edit_points  # No euchre detection
                                        
                                        # Detect euchre: if points scored < call value
                                        is_euchre = edit_points < call_value_int
                                        
                                        if is_euchre:
                                            # Other team gets (8 - points_scored)
                                            other_team_points = 8 - edit_points
                                            euchre_penalty = call_value_int  # Caller loses what they called
                                        else:
                                            other_team_points = 0
                                            euchre_penalty = 0
                                        
                                        # For euchre, pass the penalty as points_scored (what caller loses)
                                        # For normal hands, pass the actual points scored
                                        points_to_record = euchre_penalty if is_euchre else edit_points
                                    
                                    success = db.update_hand(
                                        hand_id=selected_hand_id,
                                        game_id=game['id'],
                                        caller_name=edit_caller,
                                        caller_team=edit_caller_team,
                                        call_value=edit_call_value,
                                        points_scored=points_to_record,
                                        is_euchre=is_euchre,
                                        other_team_points=other_team_points,
                                        notes=edit_notes if edit_notes else None
                                    )
                                    
                                    if success:
                                        st.success("✅ Hand updated! Scores recalculated.")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to update hand.")
            
            # Call breakdown
            st.subheader("📊 Call Breakdown")
            call_df = analytics.get_game_call_breakdown(game['id'])
            if not call_df.empty:
                st.dataframe(call_df, use_container_width=True, hide_index=True)
            
            # Delete option
            if st.button(f"🗑️ Delete Game", key=f"del_{game['id']}"):
                confirm_delete_dialog(game['id'])


def statistics_page():
    """Display overall statistics."""
    st.markdown("""
    <div class="page-header">
        <h2>📊 Statistics</h2>
    </div>
    """, unsafe_allow_html=True)

    # Overall stats
    stats = analytics.get_all_games_stats()

    st.subheader("📈 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🎮 Total Games", stats['total_games'])
    with col2:
        st.metric("▶️ Active", stats['active_games'])
    with col3:
        st.metric("🏆 Finished", stats['finished_games'])
    with col4:
        st.metric("🃏 Total Hands", stats['total_hands'])
    with col5:
        st.metric("💥 Total Euchres", stats['total_euchres'])

    if stats['total_games'] == 0:
        st.info("Play some games to see statistics!")
        return
    
    st.divider()
    
    # Most common call
    most_common = analytics.get_most_common_call()
    if most_common:
        st.subheader("🎯 Most Common Call")
        st.metric("", most_common)
    
    st.divider()
    
    # Call value statistics
    st.subheader("📞 Call Value Statistics")
    call_stats = analytics.get_call_value_stats()
    if not call_stats.empty:
        st.dataframe(call_stats, use_container_width=True, hide_index=True)
        
        # Bar chart of call counts
        st.bar_chart(call_stats.set_index('Call')['Count'])
    
    st.divider()
    
    # Player statistics
    st.subheader("👤 Player Statistics")
    player_stats = analytics.get_player_stats()
    if not player_stats.empty:
        st.dataframe(player_stats, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Partnership statistics
    st.subheader("🤝 Partnership Statistics")
    st.caption("See which player pairs perform best together!")
    partnership_stats = analytics.get_partnership_stats()
    if not partnership_stats.empty:
        st.dataframe(partnership_stats, use_container_width=True, hide_index=True)
    else:
        st.info("Play more games to see partnership statistics!")
    
    st.divider()
    
    # Team statistics
    st.subheader("👥 Team Statistics")
    team_stats = analytics.get_team_stats()
    if not team_stats.empty:
        st.dataframe(team_stats, use_container_width=True, hide_index=True)


# Route to appropriate page
if page == "🏠 Home":
    home_page()
elif page == "➕ New Game":
    new_game_page()
elif page == "🎮 Active Games":
    active_games_page()
elif page == "🏆 Finished Games":
    finished_games_page()
elif page == "📊 Statistics":
    statistics_page()
