"""
Euchre Stats - A Streamlit app for tracking and analyzing Euchre games.
🎄 Christmas Edition! 🎄
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import database as db
import analytics
from models import COMMON_CALL_VALUES

# Initialize database
db.init_database()

# Page config
st.set_page_config(
    page_title="🎄 Euchre Stats - Christmas Edition",
    page_icon="🎄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Christmas-themed CSS
st.markdown("""
<style>
    /* Christmas color scheme */
    :root {
        --christmas-red: #c41e3a;
        --christmas-green: #165b33;
        --christmas-gold: #FFD700;
        --snow-white: #fffafa;
    }
    
    /* Snowfall animation */
    .snowflake {
        position: fixed;
        top: -10px;
        z-index: 9999;
        color: #fff;
        font-size: 1.5em;
        text-shadow: 0 0 5px #fff;
        animation: fall linear infinite;
        pointer-events: none;
    }
    
    @keyframes fall {
        to {
            transform: translateY(100vh) rotate(360deg);
        }
    }
    
    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #165b33, #1e7a45) !important;
        border: 2px solid #FFD700 !important;
        color: white !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #c41e3a, #e52b50) !important;
        border: 2px solid #FFD700 !important;
    }
    
    .score-display {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
    }
    
    .team-score {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
        border: 3px solid #FFD700;
    }
    
    .winner-banner {
        background: linear-gradient(135deg, #c41e3a, #165b33);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        border: 3px solid #FFD700;
        color: white;
    }
    
    .christmas-header {
        background: linear-gradient(135deg, #c41e3a, #165b33);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        border: 3px solid #FFD700;
        margin-bottom: 1rem;
    }
    
    .game-time {
        font-size: 0.85rem;
        color: #888;
        font-style: italic;
    }
    
    /* Sidebar Christmas styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #165b33 0%, #0d3d22 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>

<!-- Snowflakes -->
<div class="snowflakes" aria-hidden="true">
    <script>
        if (!document.getElementById('snowflake-style')) {
            const style = document.createElement('style');
            style.id = 'snowflake-style';
            const snowflakes = ['❄', '❅', '❆', '✻', '✼'];
            let css = '';
            for (let i = 0; i < 15; i++) {
                const left = Math.random() * 100;
                const delay = Math.random() * 10;
                const duration = 5 + Math.random() * 10;
                const size = 0.8 + Math.random() * 1.2;
                css += `.snowflake:nth-child(${i+1}) { left: ${left}%; animation-delay: ${delay}s; animation-duration: ${duration}s; font-size: ${size}em; }`;
            }
            style.textContent = css;
            document.head.appendChild(style);
        }
    </script>
</div>
""", unsafe_allow_html=True)

# Add snowflakes to the page
snowflakes_html = ''.join(['<div class="snowflake">❄</div>' for _ in range(15)])
st.markdown(f'<div style="position:fixed;width:100%;height:100%;pointer-events:none;z-index:9999;">{snowflakes_html}</div>', unsafe_allow_html=True)

# Sidebar navigation with Christmas theme
st.sidebar.markdown("### 🎄 Euchre Stats 🎄")
st.sidebar.markdown("*Christmas Edition*")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "➕ New Game", "🎮 Active Games", "🏆 Finished Games", "📊 Statistics"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("🎅 *Merry Christmas!* 🎁")


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
    <div class="christmas-header">
        <h1>🎄 Euchre Stats 🎄</h1>
        <p>Track, visualize, and analyze your Euchre games with custom house rules!</p>
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
    st.subheader("🎁 Quick Actions")
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
    st.subheader("🎄 Recent Games")
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
        st.info("🎁 No games yet. Start a new game to begin tracking!")


def new_game_page():
    """Create a new game."""
    st.markdown("""
    <div class="christmas-header">
        <h2>🎄 Start New Game 🎄</h2>
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
    st.markdown("""
    <div class="christmas-header">
        <h2>🎮 Active Games 🎄</h2>
    </div>
    """, unsafe_allow_html=True)
    
    games = db.get_active_games()
    
    if not games:
        st.info("🎁 No active games. Start a new game!")
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
    
    # Store for next time
    st.session_state['active_game_id'] = game_id
    
    # Display game start time
    game_time = format_game_time(game['created_at'])
    st.markdown(f"🕐 **Game Started:** {game_time}")
    
    # Display current score
    st.subheader("🎄 Current Score")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="team-score" style="background-color: #c41e3a;">
            <h3 style="color: white; margin: 0;">🎅 {game['team1_name']}</h3>
            <p class="score-display" style="color: white; margin: 0;">{game['team1_score']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="team-score" style="background-color: #165b33;">
            <h3 style="color: white; margin: 0;">🎄 {game['team2_name']}</h3>
            <p class="score-display" style="color: white; margin: 0;">{game['team2_score']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption(f"Target: {game['target_score']} points")
    
    st.divider()
    
    # Log new hand
    st.subheader("📝 Log Hand")
    
    all_players = game['team1_players'] + game['team2_players']
    
    # Initialize session state for euchre dialog
    if 'pending_hand' not in st.session_state:
        st.session_state['pending_hand'] = None
    
    # Check if we need to show euchre dialog
    if st.session_state['pending_hand'] is not None:
        pending = st.session_state['pending_hand']
        other_team = game['team2_name'] if pending['caller_team'] == 'team1' else game['team1_name']
        caller_team_name = game['team1_name'] if pending['caller_team'] == 'team1' else game['team2_name']
        
        st.warning(f"❄️ **Euchre Alert!** {pending['caller_name']} got euchred!")
        st.markdown(f"**{caller_team_name}** loses **{pending['points_scored']}** points (from calling {pending['call_value']})")
        st.markdown(f"**{other_team}** gets points. How many?")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            other_points = st.number_input(
                "Points for other team",
                min_value=1,
                value=pending['points_scored'],  # Default to same as call value
                key="euchre_points_input"
            )
        
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("✅ Confirm Euchre", use_container_width=True, type="primary"):
                db.add_hand(
                    game_id=game_id,
                    caller_name=pending['caller_name'],
                    caller_team=pending['caller_team'],
                    call_value=pending['call_value'],
                    points_scored=pending['points_scored'],
                    is_euchre=True,
                    other_team_points=other_points,
                    notes=pending['notes']
                )
                st.session_state['pending_hand'] = None
                st.success("🎄 Hand logged - Euchre recorded!")
                st.rerun()
        
        with col_cancel:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state['pending_hand'] = None
                st.rerun()
        
        st.divider()
    
    # Main hand entry form
    with st.form("log_hand_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            caller_name = st.selectbox("Caller", all_players)
            
            # Determine caller's team
            if caller_name in game['team1_players']:
                caller_team = "team1"
                caller_team_name = game['team1_name']
            else:
                caller_team = "team2"
                caller_team_name = game['team2_name']
            
            st.info(f"Team: {caller_team_name}")
        
        with col2:
            call_value = st.selectbox("What Was Called", COMMON_CALL_VALUES + ["Other"])
            if call_value == "Other":
                call_value = st.text_input("Enter call value")
        
        col3, col4 = st.columns(2)
        
        with col3:
            is_euchre = st.checkbox("❄️ Was it a Euchre?")
        
        with col4:
            if not is_euchre:
                points_scored = st.number_input("Points Scored by Caller", min_value=0, value=0)
            else:
                st.info("Points lost = call value")
                points_scored = 0  # Will be set from call value
        
        notes = st.text_input("Notes (optional)")
        
        submitted = st.form_submit_button("✅ Log Hand", use_container_width=True)
        
        if submitted:
            if not call_value:
                st.error("Please select or enter a call value!")
            elif is_euchre:
                # For euchre, points lost = call value (try to parse as int)
                try:
                    euchre_points_lost = int(call_value)
                except ValueError:
                    # For non-numeric calls like "Partner Best", default to 2
                    euchre_points_lost = 2
                
                # Store pending hand and show euchre dialog
                st.session_state['pending_hand'] = {
                    'caller_name': caller_name,
                    'caller_team': caller_team,
                    'call_value': call_value,
                    'points_scored': euchre_points_lost,  # Use call value as points lost
                    'notes': notes if notes else None
                }
                st.rerun()
            else:
                db.add_hand(
                    game_id=game_id,
                    caller_name=caller_name,
                    caller_team=caller_team,
                    call_value=call_value,
                    points_scored=points_scored,
                    is_euchre=False,
                    other_team_points=0,
                    notes=notes if notes else None
                )
                st.success("🎄 Hand logged!")
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
            if st.session_state.get('confirm_delete') == game_id:
                db.delete_game(game_id)
                st.session_state.pop('confirm_delete', None)
                st.session_state.pop('active_game_id', None)
                st.success("Game deleted!")
                st.rerun()
            else:
                st.session_state['confirm_delete'] = game_id
                st.warning("Click again to confirm deletion!")
                st.rerun()


def finished_games_page():
    """View finished games."""
    st.markdown("""
    <div class="christmas-header">
        <h2>🏆 Finished Games 🎄</h2>
    </div>
    """, unsafe_allow_html=True)
    
    games = db.get_finished_games()
    
    if not games:
        st.info("🎁 No finished games yet.")
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
                🎄 {game['winner']} Wins! 🎄
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
            
            # Call breakdown
            st.subheader("📊 Call Breakdown")
            call_df = analytics.get_game_call_breakdown(game['id'])
            if not call_df.empty:
                st.dataframe(call_df, use_container_width=True, hide_index=True)
            
            # Delete option
            if st.button(f"🗑️ Delete Game", key=f"del_{game['id']}"):
                db.delete_game(game['id'])
                st.success("Game deleted!")
                st.rerun()


def statistics_page():
    """Display overall statistics."""
    st.markdown("""
    <div class="christmas-header">
        <h2>📊 Statistics 🎄</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Overall stats
    stats = analytics.get_all_games_stats()
    
    st.subheader("🎄 Overview")
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
        st.metric("❄️ Total Euchres", stats['total_euchres'])
    
    if stats['total_games'] == 0:
        st.info("🎁 Play some games to see statistics!")
        return
    
    st.divider()
    
    # Most common call
    most_common = analytics.get_most_common_call()
    if most_common:
        st.subheader("🎯 Most Common Call")
        st.metric("", most_common)
    
    st.divider()
    
    # Call value statistics
    st.subheader("🎄 Call Value Statistics")
    call_stats = analytics.get_call_value_stats()
    if not call_stats.empty:
        st.dataframe(call_stats, use_container_width=True, hide_index=True)
        
        # Bar chart of call counts
        st.bar_chart(call_stats.set_index('Call')['Count'])
    
    st.divider()
    
    # Player statistics
    st.subheader("🎅 Player Statistics")
    player_stats = analytics.get_player_stats()
    if not player_stats.empty:
        st.dataframe(player_stats, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Team statistics
    st.subheader("🎁 Team Statistics")
    team_stats = analytics.get_team_stats()
    if not team_stats.empty:
        st.dataframe(team_stats, use_container_width=True, hide_index=True)


# Handle navigation from session state
if 'nav_to' in st.session_state:
    page = st.session_state['nav_to']
    del st.session_state['nav_to']

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
