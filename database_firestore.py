"""
Database layer for Euchre Stats application.
Uses Google Firestore for multi-user concurrent access.
"""

import json
import streamlit as st
from datetime import datetime
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from google.oauth2 import service_account

# Firestore configuration
FIRESTORE_PROJECT = "unified-welder-465502-t0"
FIRESTORE_DATABASE = "scherpeuchre"

# Firestore client (cached)
_db = None


def get_firestore_client():
    """
    Get authenticated Firestore client.
    Supports Streamlit secrets and environment-based auth.
    """
    global _db
    if _db is not None:
        return _db
    
    try:
        # Method 1: Try Streamlit secrets first (for Streamlit Cloud)
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            credentials_info = st.secrets['gcp_service_account']
            # Convert to dict if it's a Streamlit secrets object
            if hasattr(credentials_info, 'to_dict'):
                credentials_info = credentials_info.to_dict()
            elif not isinstance(credentials_info, dict):
                credentials_info = dict(credentials_info)
            
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )
            _db = firestore.Client(
                credentials=credentials, 
                project=FIRESTORE_PROJECT,
                database=FIRESTORE_DATABASE
            )
            return _db
    except Exception as e:
        pass  # Fall through to default auth
    
    try:
        # Method 2: Default credentials (local dev with gcloud auth)
        _db = firestore.Client(project=FIRESTORE_PROJECT, database=FIRESTORE_DATABASE)
        return _db
    except Exception as e:
        st.error(f"Failed to connect to Firestore: {e}")
        st.info("""
        **To use Firestore, configure authentication:**
        
        **For Streamlit Cloud:**
        Add your service account JSON to `.streamlit/secrets.toml` under `[gcp_service_account]`
        
        **For local development:**
        Run `gcloud auth application-default login`
        """)
        return None


def init_database():
    """Initialize Firestore connection. Creates collections if needed."""
    db = get_firestore_client()
    if db:
        # Firestore auto-creates collections on first write
        # Just verify connection works
        try:
            # Try to access the games collection
            db.collection('games').limit(1).get()
        except Exception as e:
            st.warning(f"Firestore connection test failed: {e}")


def create_game(
    team1_name: str,
    team2_name: str,
    team1_players: List[str],
    team2_players: List[str],
    target_score: int = 32
) -> str:
    """Create a new game and return its ID."""
    db = get_firestore_client()
    if not db:
        raise Exception("Firestore not connected")
    
    game_data = {
        'team1_name': team1_name,
        'team2_name': team2_name,
        'team1_players': team1_players,
        'team2_players': team2_players,
        'team1_score': 0,
        'team2_score': 0,
        'target_score': target_score,
        'status': 'active',
        'winner': None,
        'created_at': datetime.now().isoformat(),
        'finished_at': None
    }
    
    # Add document and get auto-generated ID
    doc_ref = db.collection('games').add(game_data)
    return doc_ref[1].id


def get_game(game_id: str) -> Optional[Dict[str, Any]]:
    """Get a game by ID."""
    db = get_firestore_client()
    if not db:
        return None
    
    doc = db.collection('games').document(game_id).get()
    if doc.exists:
        game = doc.to_dict()
        game['id'] = doc.id
        return game
    return None


def get_active_games() -> List[Dict[str, Any]]:
    """Get all active games."""
    db = get_firestore_client()
    if not db:
        return []
    
    games = []
    # Simple query without order_by to avoid requiring composite index
    docs = db.collection('games').where('status', '==', 'active').stream()
    for doc in docs:
        game = doc.to_dict()
        game['id'] = doc.id
        games.append(game)
    # Sort in Python instead
    games.sort(key=lambda g: g.get('created_at', ''), reverse=True)
    return games


def get_finished_games() -> List[Dict[str, Any]]:
    """Get all finished games."""
    db = get_firestore_client()
    if not db:
        return []
    
    games = []
    # Simple query without order_by to avoid requiring composite index
    docs = db.collection('games').where('status', '==', 'finished').stream()
    for doc in docs:
        game = doc.to_dict()
        game['id'] = doc.id
        games.append(game)
    # Sort in Python instead
    games.sort(key=lambda g: g.get('created_at', ''), reverse=True)
    return games


def get_all_games() -> List[Dict[str, Any]]:
    """Get all games."""
    db = get_firestore_client()
    if not db:
        return []
    
    games = []
    docs = db.collection('games').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    for doc in docs:
        game = doc.to_dict()
        game['id'] = doc.id
        games.append(game)
    return games


def update_game_scores(game_id: str, team1_score: int, team2_score: int):
    """Update game scores."""
    db = get_firestore_client()
    if not db:
        return
    
    db.collection('games').document(game_id).update({
        'team1_score': team1_score,
        'team2_score': team2_score
    })


def finish_game(game_id: str, winner: str):
    """Mark a game as finished."""
    db = get_firestore_client()
    if not db:
        return
    
    db.collection('games').document(game_id).update({
        'status': 'finished',
        'winner': winner,
        'finished_at': datetime.now().isoformat()
    })


def delete_game(game_id: str):
    """Delete a game and all its hands."""
    db = get_firestore_client()
    if not db:
        return
    
    # Delete all hands for this game
    hands = db.collection('hands').where('game_id', '==', game_id).stream()
    for hand in hands:
        hand.reference.delete()
    
    # Delete the game
    db.collection('games').document(game_id).delete()


def add_hand(
    game_id: str,
    caller_name: str,
    caller_team: str,
    call_value: str,
    points_scored: int,
    is_euchre: bool,
    other_team_points: int,
    notes: Optional[str] = None
) -> str:
    """Add a hand to a game and update scores. Returns hand ID."""
    db = get_firestore_client()
    if not db:
        raise Exception("Firestore not connected")
    
    game = get_game(game_id)
    if not game:
        raise ValueError(f"Game {game_id} not found")
    
    # Get current hand number
    hands = get_hands(game_id)
    hand_number = len(hands) + 1
    
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
    
    # Create hand document
    hand_data = {
        'game_id': game_id,
        'hand_number': hand_number,
        'caller_name': caller_name,
        'caller_team': caller_team,
        'call_value': call_value,
        'points_scored': points_scored,
        'is_euchre': is_euchre,
        'other_team_points': other_team_points,
        'team1_delta': team1_delta,
        'team2_delta': team2_delta,
        'team1_cumulative': team1_cumulative,
        'team2_cumulative': team2_cumulative,
        'notes': notes,
        'created_at': datetime.now().isoformat()
    }
    
    doc_ref = db.collection('hands').add(hand_data)
    hand_id = doc_ref[1].id
    
    # Update game scores
    update_game_scores(game_id, team1_cumulative, team2_cumulative)
    
    # Check if game should be finished
    target = game['target_score']
    if team1_cumulative >= target:
        finish_game(game_id, game['team1_name'])
    elif team2_cumulative >= target:
        finish_game(game_id, game['team2_name'])
    
    return hand_id


def get_hands(game_id: str) -> List[Dict[str, Any]]:
    """Get all hands for a game in order."""
    db = get_firestore_client()
    if not db:
        return []
    
    hands = []
    # Simple query without order_by to avoid requiring composite index
    docs = db.collection('hands').where('game_id', '==', game_id).stream()
    for doc in docs:
        hand = doc.to_dict()
        hand['id'] = doc.id
        hands.append(hand)
    # Sort in Python instead
    hands.sort(key=lambda h: h.get('hand_number', 0))
    return hands


def get_all_hands() -> List[Dict[str, Any]]:
    """Get all hands across all games."""
    db = get_firestore_client()
    if not db:
        return []
    
    hands = []
    docs = db.collection('hands').order_by('game_id').stream()
    for doc in docs:
        hand = doc.to_dict()
        hand['id'] = doc.id
        hands.append(hand)
    return hands


def delete_last_hand(game_id: str) -> bool:
    """Delete the last hand from a game and recalculate scores. Returns True if deleted."""
    db = get_firestore_client()
    if not db:
        return False
    
    hands = get_hands(game_id)
    if not hands:
        return False
    
    last_hand = hands[-1]
    
    # Delete the hand
    db.collection('hands').document(last_hand['id']).delete()
    
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
        db.collection('games').document(game_id).update({
            'status': 'active',
            'winner': None,
            'finished_at': None
        })
    
    return True


def get_all_players() -> List[str]:
    """Get a list of all unique player names."""
    games = get_all_games()
    players = set()
    for game in games:
        players.update(game['team1_players'])
        players.update(game['team2_players'])
    return sorted(list(players))


def get_player_team_mapping() -> Dict[str, Dict[str, str]]:
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
