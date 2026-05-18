"""
Euchre Stats - A Streamlit app for tracking and analyzing Euchre games.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
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


def queue_announcement(team1_name: str, team1_score: int, team2_name: str, team2_score: int):
    """Stash a score announcement to be spoken on the next rerun."""
    st.session_state['speak_text'] = (
        f"{team1_name}, {team1_score}. {team2_name}, {team2_score}."
    )


def check_and_speak():
    """If a score announcement is queued and the herald is enabled, speak it."""
    text = st.session_state.pop('speak_text', None)
    if not text or not st.session_state.get('herald_voice', True):
        return
    payload = json.dumps(text)
    components.html(
        f"""
        <script>
        (function() {{
            try {{
                if (!('speechSynthesis' in window)) return;
                const utter = new SpeechSynthesisUtterance({payload});
                utter.lang = 'en-US';
                utter.rate = 0.95;
                utter.pitch = 1.0;
                utter.volume = 1.0;
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utter);
            }} catch (e) {{
                console.error('Herald error:', e);
            }}
        }})();
        </script>
        """,
        height=0,
    )

# Initialize database connection
db.init_database()

# Page config
st.set_page_config(
    page_title="The Maester's Ledger — Euchre Chronicle",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mediterranean × Game of Thrones theme — stone keep meets the Aegean
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap');

    :root {
        --bg: #1a1410;
        --bg-2: #221912;
        --surface: #2a2018;
        --surface-2: #3a2e22;
        --border: #5a4a35;
        --border-bright: #7a6442;
        --terracotta: #c66a3d;
        --terracotta-bright: #e08550;
        --aegean: #3a7a8f;
        --aegean-bright: #4d9ab2;
        --gold: #d4af37;
        --gold-bright: #f0c849;
        --crimson: #8b1e2d;
        --text: #e8dcc4;
        --text-muted: #9a8a72;
    }

    .stApp {
        background-color: var(--bg);
        background-image:
            radial-gradient(at 0% 0%, rgba(198,106,61,0.06) 0%, transparent 50%),
            radial-gradient(at 100% 100%, rgba(58,122,143,0.06) 0%, transparent 50%),
            url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' seed='3'/><feColorMatrix values='0 0 0 0 0.1  0 0 0 0 0.07  0 0 0 0 0.05  0 0 0 0.5 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
    }

    h1, h2, h3 {
        font-family: 'Cinzel', 'Trajan Pro', serif !important;
        letter-spacing: 0.03em !important;
        color: var(--gold) !important;
        text-shadow: 0 2px 0 rgba(0,0,0,0.5);
    }

    body, p, .stMarkdown, [data-testid="stMarkdownContainer"] {
        font-family: 'EB Garamond', 'Georgia', serif !important;
    }

    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
        background: linear-gradient(180deg, var(--surface-2) 0%, var(--surface) 100%) !important;
        border: 1px solid var(--border-bright) !important;
        border-bottom: 2px solid var(--border) !important;
        color: var(--gold) !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        border-radius: 2px !important;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.5);
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, var(--terracotta) 0%, #a55530 100%) !important;
        border-color: var(--gold-bright) !important;
        color: #fff8e0 !important;
        text-shadow: 0 0 8px rgba(240,200,73,0.6);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, var(--terracotta) 0%, #a55530 100%) !important;
        border-color: var(--gold) !important;
        color: #fff8e0 !important;
    }

    .score-display {
        font-family: 'Cinzel', serif !important;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        color: var(--gold) !important;
        text-shadow: 0 0 12px rgba(212,175,55,0.4), 0 2px 0 rgba(0,0,0,0.5);
        margin: 0.5rem 0 0 0 !important;
    }

    .team-score {
        padding: 1.5rem 1rem 2rem 1rem;
        text-align: center;
        margin: 0.5rem 0;
        background: linear-gradient(180deg, var(--surface) 0%, var(--bg-2) 100%);
        border: 1px solid var(--border);
        position: relative;
        clip-path: polygon(0 0, 100% 0, 100% calc(100% - 18px), 50% 100%, 0 calc(100% - 18px));
    }

    .team-score::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, transparent, var(--gold), transparent);
    }

    .team-score h3 {
        font-family: 'Cinzel', serif !important;
        color: var(--text) !important;
        margin: 0 !important;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        font-size: 1.1rem;
    }

    .team-score.team-accent { border-top: 2px solid var(--terracotta); }
    .team-score.team-secondary { border-top: 2px solid var(--aegean); }

    .winner-banner {
        background: linear-gradient(180deg, var(--crimson) 0%, #5a1420 100%);
        padding: 1.5rem;
        border: 2px solid var(--gold);
        border-radius: 0;
        text-align: center;
        font-family: 'Cinzel', serif !important;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 1rem 0;
        color: var(--gold-bright) !important;
        text-shadow: 0 2px 8px rgba(0,0,0,0.7), 0 0 16px rgba(212,175,55,0.4);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 4px 16px rgba(0,0,0,0.6);
    }

    .page-header {
        padding: 1.5rem 3rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(180deg, var(--surface) 0%, var(--bg-2) 100%);
        border-top: 3px solid var(--gold);
        border-bottom: 3px solid var(--gold);
        position: relative;
        text-align: center;
    }

    .page-header::before, .page-header::after {
        content: '⚔';
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.4rem;
        color: var(--gold);
        opacity: 0.85;
    }

    .page-header::before { left: 1rem; }
    .page-header::after { right: 1rem; transform: translateY(-50%) scaleX(-1); }

    .page-header h1, .page-header h2 {
        margin: 0 !important;
        color: var(--gold) !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.6);
    }

    .page-header p {
        color: var(--text-muted) !important;
        font-family: 'EB Garamond', serif !important;
        font-style: italic;
        font-size: 1.05rem;
        margin: 0.5rem 0 0 0 !important;
    }

    .game-time {
        font-size: 0.95rem;
        color: var(--text-muted);
        font-family: 'EB Garamond', serif;
        font-style: italic;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-2) 0%, var(--bg) 100%);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Cinzel', serif !important;
        color: var(--gold) !important;
        text-align: center;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        padding: 0.75rem;
        border-radius: 2px;
        border-left: 3px solid var(--terracotta);
    }

    [data-testid="stMetricValue"] {
        font-family: 'Cinzel', serif !important;
        color: var(--gold) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-family: 'EB Garamond', serif !important;
    }

    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        font-family: 'EB Garamond', serif !important;
    }

    hr { border-color: var(--border) !important; opacity: 0.6; }

    /* Subtle torchlight flicker on the winner banner */
    @keyframes torchlight {
        0%, 100% { box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 4px 16px rgba(0,0,0,0.6), 0 0 24px rgba(212,175,55,0.2); }
        50%      { box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 4px 16px rgba(0,0,0,0.6), 0 0 40px rgba(240,200,73,0.45); }
    }
    .winner-banner { animation: torchlight 3.5s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

# Sidebar — the maester's nameplate
st.sidebar.markdown("### 🏰 The Maester's Ledger")
st.sidebar.caption("*When you play the game of cards, you win — or you are euchred.*")
st.sidebar.markdown("---")

# Navigation options
nav_options = [
    "🏰 The Great Hall",
    "⚔️ Raise the Banners",
    "🐉 Active Campaigns",
    "📜 Hall of Victories",
    "🦅 The Maester's Ledger",
]

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

# Herald's Voice — read the score aloud after each hand
st.sidebar.toggle(
    "🔊 Herald's Voice",
    value=st.session_state.get('herald_voice', True),
    key='herald_voice',
    help="Have a herald proclaim the score after each hand is inscribed.",
)


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
        <h1>🏰 The Great Hall</h1>
        <p>"In the game of cards, you win — or you are euchred." Chronicle thy battles upon the green table.</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats
    stats = analytics.get_all_games_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚔️ Total Sagas", stats['total_games'])
    with col2:
        st.metric("🐉 Campaigns Afoot", stats['active_games'])
    with col3:
        st.metric("📜 Victories Recorded", stats['finished_games'])
    with col4:
        st.metric("🃏 Hands Played", stats['total_hands'])

    st.divider()

    # Quick actions
    st.subheader("👑 Hand of the King")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚔️ Raise the Banners", use_container_width=True):
            st.session_state['nav_to'] = "⚔️ Raise the Banners"
            st.rerun()
    with col2:
        active = db.get_active_games()
        if active:
            if st.button(f"🐉 Return to Campaign ({len(active)} afoot)", use_container_width=True):
                st.session_state['nav_to'] = "🐉 Active Campaigns"
                st.rerun()

    # Recent games
    st.subheader("🦅 Recent Sagas")
    games = db.get_all_games()[:5]
    if games:
        for game in games:
            status_emoji = "🐉" if game['status'] == 'active' else "🏆"
            game_time = format_game_time(game['created_at'])
            with st.expander(f"{status_emoji} {game['team1_name']} vs {game['team2_name']} ({game['team1_score']}-{game['team2_score']}) — {game_time}"):
                st.markdown(f"🕯️ **Began:** {game_time}")
                st.write(f"**Status:** {game['status'].title()}")
                st.write(f"**Target:** {game['target_score']} points")
                if game['winner']:
                    st.write(f"**Victor:** {game['winner']} 👑")
    else:
        st.info("No sagas yet, my lord. Raise thy banners to begin the chronicle.")


def new_game_page():
    """Create a new game."""
    st.markdown("""
    <div class="page-header">
        <h2>⚔️ Raise the Banners</h2>
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_game_form"):
        st.subheader("🛡️ First House")
        team1_name = st.text_input("Name of the House", value="House 1")
        team1_players_str = st.text_area(
            "Sworn swords (one per line)",
            placeholder="Eddard\nRobert\nJaime"
        )

        st.subheader("🛡️ Rival House")
        team2_name = st.text_input("Name of the House", value="House 2", key="team2_name")
        team2_players_str = st.text_area(
            "Sworn swords (one per line)",
            placeholder="Tyrion\nCersei\nDaenerys"
        )

        st.subheader("📜 Terms of Battle")
        target_score = st.number_input("Points needed for victory", min_value=1, value=32)

        submitted = st.form_submit_button("⚔️ Raise the Banners", use_container_width=True)

        if submitted:
            team1_players = [p.strip() for p in team1_players_str.strip().split('\n') if p.strip()]
            team2_players = [p.strip() for p in team2_players_str.strip().split('\n') if p.strip()]

            if not team1_players or not team2_players:
                st.error("Each House must field at least one sworn sword!")
            elif not team1_name or not team2_name:
                st.error("Each House must bear a name!")
            else:
                game_id = db.create_game(
                    team1_name=team1_name,
                    team2_name=team2_name,
                    team1_players=team1_players,
                    team2_players=team2_players,
                    target_score=target_score
                )
                st.success(f"🐉 The banners are raised! Saga {game_id} begins.")
                st.session_state['active_game_id'] = game_id
                st.session_state['nav_to'] = "🐉 Active Campaigns"
                st.rerun()


def active_games_page():
    """View and manage active games."""
    # Check if we need to scroll to top (after logging a hand)
    check_scroll_to_top()
    
    # Show success message if set
    if 'show_success' in st.session_state:
        st.success(st.session_state['show_success'])
        del st.session_state['show_success']
    
    @st.dialog("Strike from the Chronicle?")
    def confirm_delete_dialog(game_id):
        st.write("Erase this saga from the Maester's ledger? The deed cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔥 Burn It", type="primary", use_container_width=True):
                db.delete_game(game_id)
                st.session_state.pop('active_game_id', None)
                st.success("The saga is struck from record.")
                st.rerun()
        with col2:
            if st.button("Stay Thy Hand", use_container_width=True):
                st.rerun()

    st.markdown("""
    <div class="page-header">
        <h2>🐉 Active Campaigns</h2>
    </div>
    """, unsafe_allow_html=True)

    games = db.get_active_games()

    if not games:
        st.info("No campaigns afoot, my lord. Raise thy banners to march to war.")
        if st.button("⚔️ Raise the Banners"):
            st.session_state['nav_to'] = "⚔️ Raise the Banners"
            st.rerun()
        return

    # Saga selector with time
    game_options = {}
    for g in games:
        game_time = format_game_time(g['created_at'])
        label = f"{g['team1_name']} vs {g['team2_name']} ({g['team1_score']}-{g['team2_score']}) — {game_time}"
        game_options[label] = g['id']
    
    # Use session state to pre-select game if set
    default_idx = 0
    if 'active_game_id' in st.session_state:
        for i, g in enumerate(games):
            if g['id'] == st.session_state['active_game_id']:
                default_idx = i
                break
    
    selected_game_name = st.selectbox("Choose thy saga", list(game_options.keys()), index=default_idx)
    game_id = game_options[selected_game_name]
    game = db.get_game(game_id)
    if not game:
        st.error("Saga not found in the chronicle.")
        st.stop()

    # Store for next time
    st.session_state['active_game_id'] = game_id

    # Display game start time
    game_time = format_game_time(game['created_at'])
    st.markdown(f"🕯️ **Saga began:** {game_time}")

    # Display current score
    st.subheader("👑 Standing of the Houses")
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
    
    st.caption(f"⚔️ Victory at: {game['target_score']} points")
    
    st.divider()
    
    # Check if there's a pending game-ending hand to confirm
    if 'pending_game_end' in st.session_state and st.session_state['pending_game_end'] is not None:
        pending = st.session_state['pending_game_end']
        
        # Only show if it's for the current saga
        if pending['game_id'] == game_id:
            st.warning(f"👑 **The saga ends here!** This hand seals the conquest.")
            st.markdown(f"**{pending['winner']}** claims victory with **{pending['winning_score']} — {pending['losing_score']}**")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("👑 Crown the Victor", use_container_width=True, type="primary"):
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
                    queue_announcement(
                        game['team1_name'], pending.get('new_team1_score', game['team1_score']),
                        game['team2_name'], pending.get('new_team2_score', game['team2_score']),
                    )
                    st.session_state['pending_game_end'] = None
                    st.session_state['form_key'] = st.session_state.get('form_key', 0) + 1
                    st.session_state['caller_index'] = 0  # Reset caller to unassigned
                    st.balloons()
                    st.success(f"👑 The saga is ended. {pending['winner']} reigns supreme!")
                    st.session_state['nav_to'] = "📜 Hall of Victories"
                    st.rerun()

            with col2:
                if st.button("↩️ Stay Thy Hand", use_container_width=True):
                    st.session_state['pending_game_end'] = None
                    st.rerun()

            st.divider()

    # Log new hand
    st.subheader("📜 Record Thy Hand")
    
    all_players = game['team1_players'] + game['team2_players']
    caller_options = ["Unassigned"] + all_players
    
    if 'caller_index' not in st.session_state:
        st.session_state['caller_index'] = 0
    
    selected_caller = st.selectbox("Who calls the trump?", caller_options, index=st.session_state['caller_index'], key=f"caller_select_{st.session_state.get('form_key', 0)}")

    if selected_caller != "Unassigned":
        if selected_caller in game['team1_players']:
            selected_team = "team1"
            selected_team_name = game['team1_name']
        else:
            selected_team = "team2"
            selected_team_name = game['team2_name']
        st.info(f"🛡️ House: {selected_team_name}")
    else:
        selected_team = None
        st.info("🛡️ House: Unassigned")

    # Main hand entry form - use dynamic key to reset form after submission
    form_key = f"log_hand_form_{st.session_state.get('form_key', 0)}"
    with st.form(form_key, clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            call_value = st.selectbox("The call made", COMMON_CALL_VALUES + ["Other"])
            if call_value == "Other":
                call_value = st.text_input("Enter call value")

        with col2:
            points_scored = st.number_input("Points won by caller", min_value=0, value=0)

        notes = st.text_input("Scribe's notes (optional)")

        submitted = st.form_submit_button("📜 Inscribe Hand", use_container_width=True)

        if submitted:
            if selected_caller == "Unassigned":
                st.error("Name the caller before inscribing the hand!")
            elif not call_value:
                st.error("A call must be made!")
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
                        'losing_score': losing_score,
                        'new_team1_score': new_team1_score,
                        'new_team2_score': new_team2_score,
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
                        st.session_state['show_success'] = f"🔥 By the Old Gods — euchred! The caller loses {points_to_record}, the rival House claims {other_team_points}."
                    else:
                        st.session_state['show_success'] = "📜 The hand is inscribed."
                    queue_announcement(
                        game['team1_name'], new_team1_score,
                        game['team2_name'], new_team2_score,
                    )
                    trigger_scroll_to_top()
                    st.rerun()

    st.divider()

    # Hand history
    st.subheader("📜 Chronicle of Hands")
    hands_df = analytics.get_game_hands_df(game_id)
    if not hands_df.empty:
        st.dataframe(hands_df, use_container_width=True, hide_index=True)

        if st.button("↩️ Recant Last Hand"):
            if db.delete_last_hand(game_id):
                st.success("The last hand is struck from the chronicle.")
                st.rerun()
    else:
        st.info("No hands yet inscribed in this saga.")

    st.divider()

    # Score chart
    st.subheader("📈 Tides of Battle")
    score_df = analytics.get_game_score_history(game_id)
    if len(score_df) > 1:
        st.line_chart(
            score_df.set_index('hand_number'),
            use_container_width=True
        )
    
    st.divider()
    
    # Saga actions
    col1, col2 = st.columns(2)
    with col2:
        if st.button("🔥 Burn this Saga", type="secondary"):
            confirm_delete_dialog(game_id)


def finished_games_page():
    """View finished games."""

    @st.dialog("Strike from the Chronicle?")
    def confirm_delete_dialog(game_id):
        st.write("Erase this saga from the Maester's ledger? The deed cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔥 Burn It", type="primary", use_container_width=True):
                db.delete_game(game_id)
                st.success("The saga is struck from record.")
                st.rerun()
        with col2:
            if st.button("Stay Thy Hand", use_container_width=True):
                st.rerun()

    st.markdown("""
    <div class="page-header">
        <h2>📜 Hall of Victories</h2>
    </div>
    """, unsafe_allow_html=True)

    games = db.get_finished_games()

    if not games:
        st.info("The Hall stands empty. No victories yet recorded, my lord.")
        return

    for game in games:
        game_time = format_game_time(game['created_at'])
        with st.expander(f"👑 {game['winner']} — {game['team1_name']} vs {game['team2_name']} ({game['team1_score']}-{game['team2_score']}) — {game_time}"):
            st.markdown(f"🕯️ **Began:** {game_time}")
            if game['finished_at']:
                st.markdown(f"⚔️ **Concluded:** {format_game_time(game['finished_at'])}")

            # Winner banner
            st.markdown(f"""
            <div class="winner-banner">
                👑 {game['winner']} Reigns Supreme 👑
            </div>
            """, unsafe_allow_html=True)

            # Final score
            col1, col2 = st.columns(2)
            with col1:
                st.metric(game['team1_name'], game['team1_score'])
                st.write("**Sworn swords:**")
                for p in game['team1_players']:
                    st.write(f"  ⚔️ {p}")
            with col2:
                st.metric(game['team2_name'], game['team2_score'])
                st.write("**Sworn swords:**")
                for p in game['team2_players']:
                    st.write(f"  ⚔️ {p}")

            st.divider()

            # Score chart
            st.subheader("📈 Tides of Battle")
            score_df = analytics.get_game_score_history(game['id'])
            if len(score_df) > 1:
                st.line_chart(score_df.set_index('hand_number'), use_container_width=True)

            # Hand history
            st.subheader("📜 Chronicle of Hands")
            hands_df = analytics.get_game_hands_df(game['id'])
            if not hands_df.empty:
                st.dataframe(hands_df, use_container_width=True, hide_index=True)
            
            # Edit hand section - only show when checkbox is checked
            hands = db.get_hands(game['id'])
            if st.checkbox("✒️ Amend the Chronicle", key=f"show_edit_{game['id']}"):
                all_players = game['team1_players'] + game['team2_players']

                hand_options = {f"Hand {h['hand_number']} — {h['caller_name']} called {h['call_value']}": h['id'] for h in hands}
                options_list = ["➕ Inscribe New Hand"] + list(hand_options.keys())

                selected_option = st.selectbox(
                    "Select hand to amend or add anew",
                    options=options_list,
                    key=f"edit_select_{game['id']}"
                )

                if selected_option == "➕ Inscribe New Hand":
                    with st.form(key=f"add_hand_form_{game['id']}"):
                        st.markdown(f"**Inscribing Hand #{len(hands) + 1}**")
                        col1, col2 = st.columns(2)

                        with col1:
                            new_caller = st.selectbox("Who calls the trump?", all_players, key=f"new_caller_{game['id']}")

                            new_call_value = st.selectbox("The call made", COMMON_CALL_VALUES + ["Other"], key=f"new_call_{game['id']}")
                            if new_call_value == "Other":
                                new_call_value = st.text_input("Enter call value", key=f"new_call_other_{game['id']}")

                        with col2:
                            new_points = st.number_input("Points won by caller", min_value=0, value=0, key=f"new_points_{game['id']}")

                            new_notes = st.text_input("Scribe's notes (optional)", key=f"new_notes_{game['id']}")

                        if st.form_submit_button("📜 Inscribe Hand", use_container_width=True, type="primary"):
                            if not new_call_value:
                                st.error("A call must be made!")
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
                                st.success(f"📜 Hand #{len(hands) + 1} inscribed in the chronicle!")
                                st.rerun()

                else:
                    selected_hand_id = hand_options[selected_option]
                    selected_hand = db.get_hand(selected_hand_id)

                    if selected_hand:
                        with st.form(key=f"edit_hand_form_{game['id']}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                caller_idx = all_players.index(selected_hand['caller_name']) if selected_hand['caller_name'] in all_players else 0
                                edit_caller = st.selectbox("Who calls the trump?", all_players, index=caller_idx, key=f"edit_caller_{game['id']}")

                                call_options = COMMON_CALL_VALUES + ["Other"]
                                if selected_hand['call_value'] in call_options:
                                    call_idx = call_options.index(selected_hand['call_value'])
                                    edit_call_value = st.selectbox("The call made", call_options, index=call_idx, key=f"edit_call_{game['id']}")
                                else:
                                    edit_call_value = st.selectbox("The call made", call_options, index=len(call_options)-1, key=f"edit_call_{game['id']}")
                                if edit_call_value == "Other":
                                    edit_call_value = st.text_input("Enter call value", value=selected_hand['call_value'], key=f"edit_call_other_{game['id']}")

                            with col2:
                                edit_points = st.number_input("Points won by caller", min_value=0, value=selected_hand['points_scored'], key=f"edit_points_{game['id']}")

                                edit_notes = st.text_input("Scribe's notes (optional)", value=selected_hand['notes'] or '', key=f"edit_notes_{game['id']}")

                            if st.form_submit_button("💾 Amend the Hand", use_container_width=True):
                                if not edit_call_value:
                                    st.error("A call must be made!")
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
                                        st.success("✒️ The chronicle is amended. The tally is recast.")
                                        st.rerun()
                                    else:
                                        st.error("⚠️ The amendment failed, my lord.")

            # Call breakdown
            st.subheader("⚔️ Calls of the Saga")
            call_df = analytics.get_game_call_breakdown(game['id'])
            if not call_df.empty:
                st.dataframe(call_df, use_container_width=True, hide_index=True)

            if st.button(f"🔥 Burn this Saga", key=f"del_{game['id']}"):
                confirm_delete_dialog(game['id'])


def statistics_page():
    """Display overall statistics."""
    st.markdown("""
    <div class="page-header">
        <h2>🦅 The Maester's Ledger</h2>
    </div>
    """, unsafe_allow_html=True)

    stats = analytics.get_all_games_stats()

    st.subheader("📜 The Scroll of Records")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("⚔️ Total Sagas", stats['total_games'])
    with col2:
        st.metric("🐉 Afoot", stats['active_games'])
    with col3:
        st.metric("👑 Concluded", stats['finished_games'])
    with col4:
        st.metric("🃏 Hands Played", stats['total_hands'])
    with col5:
        st.metric("🔥 Euchres", stats['total_euchres'])

    if stats['total_games'] == 0:
        st.info("Play some sagas, my lord, and the ledger shall fill.")
        return

    st.divider()

    most_common = analytics.get_most_common_call()
    if most_common:
        st.subheader("🎯 Favoured Call of the Realm")
        st.metric("", most_common)

    st.divider()

    st.subheader("⚔️ Tally of Calls")
    call_stats = analytics.get_call_value_stats()
    if not call_stats.empty:
        st.dataframe(call_stats, use_container_width=True, hide_index=True)
        st.bar_chart(call_stats.set_index('Call')['Count'])

    st.divider()

    st.subheader("👤 Knights of the Realm")
    player_stats = analytics.get_player_stats()
    if not player_stats.empty:
        st.dataframe(player_stats, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🤝 Sworn Partnerships")
    st.caption("Which sworn brothers ride best together into battle?")
    partnership_stats = analytics.get_partnership_stats()
    if not partnership_stats.empty:
        st.dataframe(partnership_stats, use_container_width=True, hide_index=True)
    else:
        st.info("Wage more campaigns to see which partnerships endure, my lord.")

    st.divider()

    st.subheader("🛡️ The Great Houses")
    team_stats = analytics.get_team_stats()
    if not team_stats.empty:
        st.dataframe(team_stats, use_container_width=True, hide_index=True)


# Route to appropriate page
if page == "🏰 The Great Hall":
    home_page()
elif page == "⚔️ Raise the Banners":
    new_game_page()
elif page == "🐉 Active Campaigns":
    active_games_page()
elif page == "📜 Hall of Victories":
    finished_games_page()
elif page == "🦅 The Maester's Ledger":
    statistics_page()

# Fire any queued herald announcement after the page has rendered
check_and_speak()
