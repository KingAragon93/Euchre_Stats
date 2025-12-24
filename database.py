"""
Database layer for Euchre Stats application.
Handles SQLite persistence for games and hands.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = "euchre_stats.db"


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database with required tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Games table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team1_name TEXT NOT NULL,
                team2_name TEXT NOT NULL,
                team1_players TEXT NOT NULL,
                team2_players TEXT NOT NULL,
                team1_score INTEGER DEFAULT 0,
                team2_score INTEGER DEFAULT 0,
                target_score INTEGER DEFAULT 32,
                status TEXT DEFAULT 'active',
                winner TEXT,
                created_at TEXT NOT NULL,
                finished_at TEXT
            )
        """)
        
        # Hands table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                hand_number INTEGER NOT NULL,
                caller_name TEXT NOT NULL,
                caller_team TEXT NOT NULL,
                call_value TEXT NOT NULL,
                points_scored INTEGER NOT NULL,
                is_euchre INTEGER DEFAULT 0,
                other_team_points INTEGER DEFAULT 0,
                team1_delta INTEGER NOT NULL,
                team2_delta INTEGER NOT NULL,
                team1_cumulative INTEGER NOT NULL,
                team2_cumulative INTEGER NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        """)
        
        conn.commit()


def create_game(
    team1_name: str,
    team2_name: str,
    team1_players: List[str],
    team2_players: List[str],
    target_score: int = 32
) -> int:
    """Create a new game and return its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO games (
                team1_name, team2_name, team1_players, team2_players,
                target_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            team1_name,
            team2_name,
            json.dumps(team1_players),
            json.dumps(team2_players),
            target_score,
            datetime.now().isoformat()
        ))
        conn.commit()
        return cursor.lastrowid


def get_game(game_id: int) -> Optional[Dict[str, Any]]:
    """Get a game by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
        row = cursor.fetchone()
        if row:
            game = dict(row)
            game['team1_players'] = json.loads(game['team1_players'])
            game['team2_players'] = json.loads(game['team2_players'])
            return game
        return None


def get_active_games() -> List[Dict[str, Any]]:
    """Get all active games."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM games WHERE status = 'active'
            ORDER BY created_at DESC
        """)
        games = []
        for row in cursor.fetchall():
            game = dict(row)
            game['team1_players'] = json.loads(game['team1_players'])
            game['team2_players'] = json.loads(game['team2_players'])
            games.append(game)
        return games


def get_finished_games() -> List[Dict[str, Any]]:
    """Get all finished games."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM games WHERE status = 'finished'
            ORDER BY finished_at DESC
        """)
        games = []
        for row in cursor.fetchall():
            game = dict(row)
            game['team1_players'] = json.loads(game['team1_players'])
            game['team2_players'] = json.loads(game['team2_players'])
            games.append(game)
        return games


def get_all_games() -> List[Dict[str, Any]]:
    """Get all games."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM games ORDER BY created_at DESC")
        games = []
        for row in cursor.fetchall():
            game = dict(row)
            game['team1_players'] = json.loads(game['team1_players'])
            game['team2_players'] = json.loads(game['team2_players'])
            games.append(game)
        return games


def update_game_scores(game_id: int, team1_score: int, team2_score: int):
    """Update game scores."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE games SET team1_score = ?, team2_score = ?
            WHERE id = ?
        """, (team1_score, team2_score, game_id))
        conn.commit()


def finish_game(game_id: int, winner: str):
    """Mark a game as finished."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE games SET status = 'finished', winner = ?, finished_at = ?
            WHERE id = ?
        """, (winner, datetime.now().isoformat(), game_id))
        conn.commit()


def delete_game(game_id: int):
    """Delete a game and all its hands."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hands WHERE game_id = ?", (game_id,))
        cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()


def add_hand(
    game_id: int,
    caller_name: str,
    caller_team: str,
    call_value: str,
    points_scored: int,
    is_euchre: bool,
    other_team_points: int,
    notes: Optional[str] = None
) -> int:
    """Add a hand to a game and update scores. Returns hand ID."""
    game = get_game(game_id)
    if not game:
        raise ValueError(f"Game {game_id} not found")
    
    # Get current hand number
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(MAX(hand_number), 0) as max_hand
            FROM hands WHERE game_id = ?
        """, (game_id,))
        hand_number = cursor.fetchone()['max_hand'] + 1
    
    # Calculate deltas based on caller team and euchre status
    if is_euchre:
        # Caller's team LOSES points, other team gains
        if caller_team == "team1":
            team1_delta = -points_scored
            team2_delta = other_team_points
        else:
            team1_delta = other_team_points
            team2_delta = -points_scored
    else:
        # Caller's team gains points
        if caller_team == "team1":
            team1_delta = points_scored
            team2_delta = 0
        else:
            team1_delta = 0
            team2_delta = points_scored
    
    # Calculate cumulative scores
    team1_cumulative = game['team1_score'] + team1_delta
    team2_cumulative = game['team2_score'] + team2_delta
    
    # Insert hand
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hands (
                game_id, hand_number, caller_name, caller_team, call_value,
                points_scored, is_euchre, other_team_points,
                team1_delta, team2_delta, team1_cumulative, team2_cumulative,
                notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game_id, hand_number, caller_name, caller_team, call_value,
            points_scored, 1 if is_euchre else 0, other_team_points,
            team1_delta, team2_delta, team1_cumulative, team2_cumulative,
            notes, datetime.now().isoformat()
        ))
        conn.commit()
        hand_id = cursor.lastrowid
    
    # Update game scores
    update_game_scores(game_id, team1_cumulative, team2_cumulative)
    
    # Check if game should be finished
    target = game['target_score']
    if team1_cumulative >= target:
        finish_game(game_id, game['team1_name'])
    elif team2_cumulative >= target:
        finish_game(game_id, game['team2_name'])
    
    return hand_id


def get_hands(game_id: int) -> List[Dict[str, Any]]:
    """Get all hands for a game in order."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM hands WHERE game_id = ?
            ORDER BY hand_number ASC
        """, (game_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_all_hands() -> List[Dict[str, Any]]:
    """Get all hands across all games."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hands ORDER BY game_id, hand_number")
        return [dict(row) for row in cursor.fetchall()]


def delete_last_hand(game_id: int) -> bool:
    """Delete the last hand from a game and recalculate scores. Returns True if deleted."""
    hands = get_hands(game_id)
    if not hands:
        return False
    
    last_hand = hands[-1]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hands WHERE id = ?", (last_hand['id'],))
        conn.commit()
    
    # Recalculate game scores
    if len(hands) > 1:
        prev_hand = hands[-2]
        new_team1_score = prev_hand['team1_cumulative']
        new_team2_score = prev_hand['team2_cumulative']
    else:
        new_team1_score = 0
        new_team2_score = 0
    
    update_game_scores(game_id, new_team1_score, new_team2_score)
    
    # Reactivate game if it was finished
    game = get_game(game_id)
    if game['status'] == 'finished':
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE games SET status = 'active', winner = NULL, finished_at = NULL
                WHERE id = ?
            """, (game_id,))
            conn.commit()
    
    return True


def get_all_players() -> List[str]:
    """Get a list of all unique player names."""
    games = get_all_games()
    players = set()
    for game in games:
        players.update(game['team1_players'])
        players.update(game['team2_players'])
    return sorted(list(players))


def get_player_team_mapping() -> Dict[int, Dict[str, str]]:
    """Get mapping of game_id -> player_name -> team_name."""
    games = get_all_games()
    mapping = {}
    for game in games:
        game_mapping = {}
        for player in game['team1_players']:
            game_mapping[player] = game['team1_name']
        for player in game['team2_players']:
            game_mapping[player] = game['team2_name']
        mapping[game['id']] = game_mapping
    return mapping
