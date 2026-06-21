"""
theme.py — Two-theme system for Euchre Stats.

Each theme is a self-contained dict of every UI string the app needs plus the
CSS overrides for the visual style. The currently-selected theme lives in
st.session_state['theme'] and defaults to 'game_of_thrones' so existing
sessions don't see a sudden change.

Add a new theme by defining a new dict with the same keys as GAME_OF_THRONES
and STANDARD, then register it in THEMES. Every public call site goes through
`t(key, **format_kwargs)` which handles both lookup and `.format()` formatting.

Routing keys (NAV_HOME / NAV_NEW_GAME / NAV_ACTIVE / NAV_FINISHED / NAV_STATS)
are STABLE internal identifiers — never compared to user-facing strings —
so theme changes can't break navigation. The displayed sidebar labels are
read from the active theme.
"""
from __future__ import annotations

from typing import Optional

import streamlit as st


# === Stable internal routing keys ===
NAV_HOME = 'home'
NAV_NEW_GAME = 'new_game'
NAV_ACTIVE = 'active'
NAV_FINISHED = 'finished'
NAV_STATS = 'stats'

NAV_KEYS = [NAV_HOME, NAV_NEW_GAME, NAV_ACTIVE, NAV_FINISHED, NAV_STATS]


# === Game of Thrones × Mediterranean theme ===

GAME_OF_THRONES = {
    'display_name': '⚔️ Game of Thrones',

    # Page-level
    'page_title': "The Maester's Ledger — Euchre Chronicle",
    'page_icon': '🏰',

    # Sidebar
    'sidebar_title': "### 🏰 The Maester's Ledger",
    'sidebar_tagline': "*When you play the game of cards, you win — or you are euchred.*",
    'sidebar_nav_label': 'Navigate',
    'sidebar_voice_toggle': "🔊 Herald's Voice",
    'sidebar_voice_help': "Have a herald proclaim the score after each hand is inscribed.",
    'sidebar_commentary': "🗣 Herald Commentary",
    'sidebar_commentary_help': (
        "How often the herald interjects with a factoid about the caller — "
        "their tendencies, success rate on this call, streaks, lead changes, "
        "lifetime milestones, and more. If no notable fact applies, the "
        "herald falls back to a stat-flavored recap of the hand."
    ),

    # Nav labels (display only — routing uses NAV_KEYS)
    'nav_home': '🏰 The Great Hall',
    'nav_new_game': '⚔️ Raise the Banners',
    'nav_active': '🐉 Active Campaigns',
    'nav_finished': '📜 Hall of Victories',
    'nav_stats': "🦅 The Maester's Ledger",

    # === Home page ===
    'home_h1': '🏰 The Great Hall',
    'home_subtitle': '"In the game of cards, you win — or you are euchred." Chronicle thy battles upon the green table.',
    'home_metric_total': '⚔️ Total Sagas',
    'home_metric_active': '🐉 Campaigns Afoot',
    'home_metric_finished': '📜 Victories Recorded',
    'home_metric_hands': '🃏 Hands Played',
    'home_quick_header': '👑 Hand of the King',
    'home_btn_new': '⚔️ Raise the Banners',
    'home_btn_continue': '🐉 Return to Campaign ({n} afoot)',
    'home_recent_header': '🦅 Recent Sagas',
    'home_began': '🕯️ **Began:** {time}',
    'home_status': '**Status:** {status}',
    'home_target': '**Target:** {target} points',
    'home_victor': '**Victor:** {winner} 👑',
    'home_no_games': 'No sagas yet, my lord. Raise thy banners to begin the chronicle.',

    # === New Game page ===
    'newgame_h2': '⚔️ Raise the Banners',
    'newgame_team1_subheader': '🛡️ First House',
    'newgame_team2_subheader': '🛡️ Rival House',
    'newgame_team_name_label': 'Name of the House',
    'newgame_team1_default': 'House 1',
    'newgame_team2_default': 'House 2',
    'newgame_players_label': 'Sworn swords (one per line)',
    'newgame_team1_placeholder': 'Eddard\nRobert\nJaime',
    'newgame_team2_placeholder': 'Tyrion\nCersei\nDaenerys',
    'newgame_terms_subheader': '📜 Terms of Battle',
    'newgame_target_label': 'Points needed for victory',
    'newgame_btn_start': '⚔️ Raise the Banners',
    'newgame_err_no_players': 'Each House must field at least one sworn sword!',
    'newgame_err_no_names': 'Each House must bear a name!',
    'newgame_success': '🐉 The banners are raised! Saga {id} begins.',

    # === Active Games page ===
    'active_h2': '🐉 Active Campaigns',
    'active_empty_info': 'No campaigns afoot, my lord. Raise thy banners to march to war.',
    'active_btn_new': '⚔️ Raise the Banners',
    'active_select_label': 'Choose thy saga',
    'active_not_found': 'Saga not found in the chronicle.',
    'active_began': '🕯️ **Saga began:** {time}',
    'active_score_header': '👑 Standing of the Houses',
    'active_target_caption': '⚔️ Victory at: {target} points',
    'active_log_header': '📜 Record Thy Hand',
    'active_caller_label': 'Who calls the trump?',
    'active_house_info': '🛡️ House: {name}',
    'active_house_unassigned': '🛡️ House: Unassigned',
    'active_call_label': 'The call made',
    'active_points_label': 'Points won by caller',
    'active_notes_label': "Scribe's notes (optional)",
    'active_btn_inscribe': '📜 Inscribe Hand',
    'active_err_no_caller': 'Name the caller before inscribing the hand!',
    'active_err_no_call': 'A call must be made!',
    'active_euchre_msg': "🔥 By the Old Gods — euchred! The caller loses {pts}, the rival House claims {other}.",
    'active_logged_msg': '📜 The hand is inscribed.',
    'active_chronicle_header': '📜 Chronicle of Hands',
    'active_btn_undo': '↩️ Recant Last Hand',
    'active_undo_msg': 'The last hand is struck from the chronicle.',
    'active_no_hands': 'No hands yet inscribed in this saga.',
    'active_tides_header': '📈 Tides of Battle',
    'active_btn_burn': '🔥 Burn this Saga',

    # End-of-game confirmation (the "would end the game" prompt)
    'endgame_warning': '👑 **The saga ends here!** This hand seals the conquest.',
    'endgame_claim': '**{winner}** claims victory with **{ws} — {ls}**',
    'endgame_btn_crown': '👑 Crown the Victor',
    'endgame_btn_cancel': '↩️ Stay Thy Hand',

    # === Celebration view ===
    'celebration_h2': '👑 Victory!',
    'celebration_subtitle': 'The saga is ended. The chronicle is sealed.',
    'celebration_winner_banner': '👑 {winner} Reigns Supreme 👑',
    'celebration_summary_header': '📜 Saga Summary',
    'celebration_metric_hands': 'Hands',
    'celebration_metric_euchres': 'Euchres',
    'celebration_metric_mvp': 'MVP',
    'celebration_metric_mighty': 'Mightiest Hand',
    'celebration_mighty_delta': '{name} • call of {call}',
    'celebration_rivalry_header': '⚔️ Rivalry Record',
    'celebration_rivalry_caption': 'These two houses have now met {n} times upon the green table.',
    'celebration_rivalry_wins': '{name} wins',
    'celebration_rivalry_avg': 'avg {avg} pts/saga',
    'celebration_btn_rematch': '⚔️ Rematch',
    'celebration_btn_hall': '📜 Hall of Victories',
    'celebration_btn_done': '✓ Done',

    # === Finished Games / Hall of Victories ===
    'finished_h2': '📜 Hall of Victories',
    'finished_empty': 'The Hall stands empty. No victories yet recorded, my lord.',
    'finished_winner_banner': '👑 {winner} Reigns Supreme 👑',
    'finished_began': '🕯️ **Began:** {time}',
    'finished_concluded': '⚔️ **Concluded:** {time}',
    'finished_sworn': '**Sworn swords:**',
    'finished_player_bullet': '  ⚔️ {name}',
    'finished_tides_header': '📈 Tides of Battle',
    'finished_chronicle_header': '📜 Chronicle of Hands',
    'finished_amend_checkbox': '✒️ Amend the Chronicle',
    'finished_amend_select': 'Select hand to amend or add anew',
    'finished_inscribe_new_option': '➕ Inscribe New Hand',
    'finished_adding_hand': '**Inscribing Hand #{n}**',
    'finished_btn_inscribe_new': '📜 Inscribe Hand',
    'finished_inscribe_success': '📜 Hand #{n} inscribed in the chronicle!',
    'finished_btn_amend': '💾 Amend the Hand',
    'finished_amend_success': '✒️ The chronicle is amended. The tally is recast.',
    'finished_amend_failure': '⚠️ The amendment failed, my lord.',
    'finished_calls_header': '⚔️ Calls of the Saga',
    'finished_btn_rematch': '⚔️ Rematch',
    'finished_rematch_help': 'Raise the banners again — same houses, same sworn swords, target {target} points.',
    'finished_btn_burn': '🔥 Burn this Saga',

    # Delete dialog
    'dialog_delete_title': 'Strike from the Chronicle?',
    'dialog_delete_warning': "Erase this saga from the Maester's ledger? The deed cannot be undone.",
    'dialog_btn_burn': '🔥 Burn It',
    'dialog_btn_cancel': 'Stay Thy Hand',
    'dialog_delete_success': 'The saga is struck from record.',

    # === Statistics page ===
    'stats_h2': "🦅 The Maester's Ledger",
    'stats_scroll_header': '📜 The Scroll of Records',
    'stats_metric_total': '⚔️ Total Sagas',
    'stats_metric_afoot': '🐉 Afoot',
    'stats_metric_concluded': '👑 Concluded',
    'stats_metric_hands': '🃏 Hands Played',
    'stats_metric_euchres': '🔥 Euchres',
    'stats_empty': 'Play some sagas, my lord, and the ledger shall fill.',
    'stats_favored_header': '🎯 Favoured Call of the Realm',
    'stats_calls_header': '⚔️ Tally of Calls',
    'stats_knights_header': '👤 Knights of the Realm',
    'stats_partnerships_header': '🤝 Sworn Partnerships',
    'stats_partnerships_caption': 'Which sworn brothers ride best together into battle?',
    'stats_partnerships_empty': 'Wage more campaigns to see which partnerships endure, my lord.',
    'stats_houses_header': '🛡️ The Great Houses',

    # === End-of-game spoken recap — phrase templates used by insights.end_of_game_summary ===
    'recap_winner': 'Victory! {winner} triumphs over {loser}, {ws} to {ls}.',
    'recap_length': 'The saga ran {n} hands.',
    'recap_mvp_net': '{name} led all callers with {net} net points across {count} calls.',
    'recap_mvp_zero': '{name} called {count} times for a net of zero.',
    'recap_mighty_final': "The mightiest hand was {name}'s call of {call}, worth {pts} points.",
    'recap_mighty_earlier': "Earlier in the saga, {name}'s call of {call} brought the mightiest hand at {pts} points.",
    'recap_euchres': '{n} hands ended in euchres.',
    'recap_comeback': 'At one point, {winner} trailed by {deficit} before fighting back.',

    # === CSS — the medieval banner style ===
    'css': """
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
        --aegean: #3a7a8f;
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
            radial-gradient(at 100% 100%, rgba(58,122,143,0.06) 0%, transparent 50%);
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

    @keyframes torchlight {
        0%, 100% { box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 4px 16px rgba(0,0,0,0.6), 0 0 24px rgba(212,175,55,0.2); }
        50%      { box-shadow: 0 0 0 1px rgba(0,0,0,0.5), 0 4px 16px rgba(0,0,0,0.6), 0 0 40px rgba(240,200,73,0.45); }
    }
    .winner-banner { animation: torchlight 3.5s ease-in-out infinite; }
</style>
""",
}


# === Standard fun-but-normal theme ===

STANDARD = {
    'display_name': '🎲 Standard',

    'page_title': 'Euchre Stats',
    'page_icon': '🃏',

    'sidebar_title': '### 🃏 Euchre Stats',
    'sidebar_tagline': '*Track your hands. Win the night.*',
    'sidebar_nav_label': 'Navigate',
    'sidebar_voice_toggle': '🔊 Announcer Voice',
    'sidebar_voice_help': 'Have an announcer read the score after each hand.',
    'sidebar_commentary': '🗣 Color Commentary',
    'sidebar_commentary_help': (
        "How often the announcer adds a fact about the caller — their "
        "favorite call, success rate, current streak, lead changes, lifetime "
        "milestones, and more. Falls back to a simple recap when nothing's "
        "notable."
    ),

    'nav_home': '🏠 Home',
    'nav_new_game': '➕ New Game',
    'nav_active': '🎮 Active Games',
    'nav_finished': '🏆 Finished Games',
    'nav_stats': '📊 Statistics',

    # === Home page ===
    'home_h1': '🏠 Home',
    'home_subtitle': 'Track, visualize, and analyze your Euchre games.',
    'home_metric_total': '🎮 Total Games',
    'home_metric_active': '▶️ In Progress',
    'home_metric_finished': '🏆 Finished',
    'home_metric_hands': '🃏 Hands Played',
    'home_quick_header': '⚡ Quick Actions',
    'home_btn_new': '➕ Start New Game',
    'home_btn_continue': '🎮 Continue Game ({n} in progress)',
    'home_recent_header': '🕒 Recent Games',
    'home_began': '🕐 **Started:** {time}',
    'home_status': '**Status:** {status}',
    'home_target': '**Target:** {target} points',
    'home_victor': '**Winner:** {winner} 🏆',
    'home_no_games': "No games yet. Start one to begin tracking.",

    # === New Game page ===
    'newgame_h2': '➕ New Game',
    'newgame_team1_subheader': '🅰️ Team One',
    'newgame_team2_subheader': '🅱️ Team Two',
    'newgame_team_name_label': 'Team name',
    'newgame_team1_default': 'Team 1',
    'newgame_team2_default': 'Team 2',
    'newgame_players_label': 'Players (one per line)',
    'newgame_team1_placeholder': 'Alice\nBob\nCharlie',
    'newgame_team2_placeholder': 'Dave\nEve\nFrank',
    'newgame_terms_subheader': '🎯 Game Settings',
    'newgame_target_label': 'Points to win',
    'newgame_btn_start': '🎮 Start Game',
    'newgame_err_no_players': 'Each team needs at least one player!',
    'newgame_err_no_names': 'Each team needs a name!',
    'newgame_success': "🎮 Game on! Game {id} started.",

    # === Active Games page ===
    'active_h2': '🎮 Active Games',
    'active_empty_info': "No games in progress. Start a new one!",
    'active_btn_new': '➕ Start New Game',
    'active_select_label': 'Choose a game',
    'active_not_found': 'Game not found.',
    'active_began': '🕐 **Started:** {time}',
    'active_score_header': '📊 Current Score',
    'active_target_caption': '🎯 First to: {target} points',
    'active_log_header': '📝 Log Hand',
    'active_caller_label': 'Who called it?',
    'active_house_info': '🅰️ Team: {name}',
    'active_house_unassigned': '🅰️ Team: Unassigned',
    'active_call_label': 'What was called',
    'active_points_label': 'Points won by caller',
    'active_notes_label': 'Notes (optional)',
    'active_btn_inscribe': '✅ Log Hand',
    'active_err_no_caller': 'Pick a caller first!',
    'active_err_no_call': 'Pick a call value!',
    'active_euchre_msg': '💥 Euchred! Caller loses {pts}, other team gets {other}.',
    'active_logged_msg': '✅ Hand logged.',
    'active_chronicle_header': '📜 Hand History',
    'active_btn_undo': '↩️ Undo Last Hand',
    'active_undo_msg': 'Last hand undone.',
    'active_no_hands': 'No hands yet. Log the first one above.',
    'active_tides_header': '📈 Score Over Time',
    'active_btn_burn': '🗑️ Delete Game',

    # End-of-game confirmation
    'endgame_warning': '🏁 **Game point!** This hand ends the game.',
    'endgame_claim': '**{winner}** wins **{ws} — {ls}**',
    'endgame_btn_crown': '🏆 Finish Game',
    'endgame_btn_cancel': '↩️ Cancel',

    # === Celebration view ===
    'celebration_h2': '🏆 Winner!',
    'celebration_subtitle': 'Game over. Final stats below.',
    'celebration_winner_banner': '🏆 {winner} Wins! 🏆',
    'celebration_summary_header': '📊 Game Summary',
    'celebration_metric_hands': 'Hands',
    'celebration_metric_euchres': 'Euchres',
    'celebration_metric_mvp': 'MVP',
    'celebration_metric_mighty': 'Biggest Hand',
    'celebration_mighty_delta': '{name} • called {call}',
    'celebration_rivalry_header': '⚔️ Head-to-Head',
    'celebration_rivalry_caption': "These two teams have now played {n} games against each other.",
    'celebration_rivalry_wins': '{name} wins',
    'celebration_rivalry_avg': 'avg {avg} pts/game',
    'celebration_btn_rematch': '🔁 Rematch',
    'celebration_btn_hall': '🏆 Finished Games',
    'celebration_btn_done': '✓ Done',

    # === Finished Games ===
    'finished_h2': '🏆 Finished Games',
    'finished_empty': 'No finished games yet.',
    'finished_winner_banner': '🏆 {winner} Wins! 🏆',
    'finished_began': '🕐 **Started:** {time}',
    'finished_concluded': '🏁 **Finished:** {time}',
    'finished_sworn': '**Players:**',
    'finished_player_bullet': '  • {name}',
    'finished_tides_header': '📈 Score Progression',
    'finished_chronicle_header': '📜 Hand Log',
    'finished_amend_checkbox': '✏️ Edit or Add Hand',
    'finished_amend_select': 'Select hand to edit or add new',
    'finished_inscribe_new_option': '➕ Add New Hand',
    'finished_adding_hand': '**Adding Hand #{n}**',
    'finished_btn_inscribe_new': '➕ Add Hand',
    'finished_inscribe_success': '✅ Hand #{n} added.',
    'finished_btn_amend': '💾 Update Hand',
    'finished_amend_success': '✅ Hand updated. Scores recalculated.',
    'finished_amend_failure': '❌ Failed to update hand.',
    'finished_calls_header': '📊 Call Breakdown',
    'finished_btn_rematch': '🔁 Rematch',
    'finished_rematch_help': 'Play again with the same teams and target {target} points.',
    'finished_btn_burn': '🗑️ Delete Game',

    # Delete dialog
    'dialog_delete_title': 'Delete this game?',
    'dialog_delete_warning': "This will permanently delete the game and its hands. Can't undo.",
    'dialog_btn_burn': '🗑️ Delete',
    'dialog_btn_cancel': 'Cancel',
    'dialog_delete_success': 'Game deleted.',

    # === Statistics page ===
    'stats_h2': '📊 Statistics',
    'stats_scroll_header': '📈 Overview',
    'stats_metric_total': '🎮 Total Games',
    'stats_metric_afoot': '▶️ In Progress',
    'stats_metric_concluded': '🏆 Finished',
    'stats_metric_hands': '🃏 Total Hands',
    'stats_metric_euchres': '💥 Total Euchres',
    'stats_empty': "Play some games to see stats.",
    'stats_favored_header': '🎯 Most Common Call',
    'stats_calls_header': '📞 Call Value Stats',
    'stats_knights_header': '👤 Player Stats',
    'stats_partnerships_header': '🤝 Partnership Stats',
    'stats_partnerships_caption': 'Which player pairs perform best together?',
    'stats_partnerships_empty': 'Play more games to see partnership stats.',
    'stats_houses_header': '👥 Team Stats',

    # === End-of-game spoken recap ===
    'recap_winner': 'Winner! {winner} beat {loser}, {ws} to {ls}.',
    'recap_length': 'The game ran {n} hands.',
    'recap_mvp_net': '{name} was top scorer with {net} net points across {count} calls.',
    'recap_mvp_zero': '{name} called {count} times for a net of zero.',
    'recap_mighty_final': "The biggest hand was {name}'s call of {call}, worth {pts} points.",
    'recap_mighty_earlier': "Earlier in the game, {name}'s call of {call} was the biggest hand at {pts} points.",
    'recap_euchres': '{n} hands ended in euchres.',
    'recap_comeback': 'At one point, {winner} trailed by {deficit} before fighting back.',

    # === CSS — modern clean card style (no overrides — lets config.toml shine) ===
    'css': """
<style>
    /* Modern clean theme leans on Streamlit's native styling with the
       config.toml dark palette. Only the bespoke .winner-banner and
       .page-header / .team-score / .score-display get explicit rules
       since the app uses them as unsafe-HTML. */

    .page-header {
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        background: var(--secondary-background-color, #161922);
        border-radius: 12px;
        border-left: 4px solid var(--primary-color, #6366f1);
    }
    .page-header h1, .page-header h2 { margin: 0 !important; }
    .page-header p {
        margin: 0.4rem 0 0 0 !important;
        opacity: 0.75;
        font-size: 0.95rem;
    }

    .winner-banner {
        background: linear-gradient(135deg, #6366f1, #14b8a6);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.6rem;
        font-weight: 600;
        margin: 1rem 0;
        color: white !important;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 24px rgba(99,102,241,0.25);
    }

    .team-score {
        padding: 1.25rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        background: #161922;
        border: 1px solid #2a2f3d;
    }
    .team-score h3 { margin: 0 !important; font-weight: 600; }
    .team-score.team-accent { border-left: 4px solid #6366f1; }
    .team-score.team-secondary { border-left: 4px solid #14b8a6; }

    .score-display {
        font-size: 2.75rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: -0.02em;
        margin: 0.5rem 0 0 0 !important;
    }
</style>
""",
}


THEMES = {
    'game_of_thrones': GAME_OF_THRONES,
    'standard': STANDARD,
}

DEFAULT_THEME = 'game_of_thrones'


def _read_theme_from_url() -> Optional[str]:
    """Read a `?theme=` value from the URL query params (if present and valid).
    Used to seed session_state on a fresh page load so the user's last
    theme choice survives browser refreshes."""
    try:
        params = st.query_params
        key = params.get('theme')
        if key in THEMES:
            return key
    except Exception:
        pass
    return None


def init_theme_from_url() -> None:
    """Call once near the top of the app (before the sidebar's theme picker)
    to make sure session_state['theme'] reflects the URL query param.
    Safe to call repeatedly — only writes when needed."""
    if 'theme' in st.session_state:
        return
    from_url = _read_theme_from_url()
    if from_url is not None:
        st.session_state['theme'] = from_url


def persist_theme_to_url(key: str) -> None:
    """Write the user's theme choice into the URL query params so a refresh
    keeps it. Streamlit will reflect this in the browser address bar."""
    try:
        st.query_params['theme'] = key
    except Exception:
        pass


def current_theme_key() -> str:
    """Currently-selected theme key, defaulting to DEFAULT_THEME."""
    return st.session_state.get('theme', DEFAULT_THEME)


def current_theme() -> dict:
    """Currently-selected theme dict."""
    return THEMES.get(current_theme_key(), THEMES[DEFAULT_THEME])


def t(key: str, **fmt) -> str:
    """Look up a themed string, formatting with kwargs if provided. If the key
    is missing from the active theme, fall back to the default theme — keeps
    the app working as new keys are added incrementally."""
    theme = current_theme()
    value = theme.get(key)
    if value is None:
        value = THEMES[DEFAULT_THEME].get(key, key)
    if fmt:
        try:
            return value.format(**fmt)
        except (KeyError, IndexError, ValueError):
            return value
    return value


# Mapping helpers used by sidebar nav and routing
def nav_label_to_key() -> dict:
    """Map current theme's nav labels → stable routing keys."""
    return {t(f'nav_{k}'): k for k in NAV_KEYS}


def nav_labels_in_order() -> list:
    """Nav labels in the canonical display order."""
    return [t(f'nav_{k}') for k in NAV_KEYS]
