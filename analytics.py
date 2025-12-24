"""
Analytics module for Euchre Stats application.
Provides data analysis and chart generation using Pandas.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import database as db


def get_game_score_history(game_id: int) -> pd.DataFrame:
    """
    Get score history for a game as a DataFrame.
    Returns DataFrame with columns: hand_number, team1_score, team2_score
    Includes starting point at (0, 0, 0) for clean charts.
    """
    hands = db.get_hands(game_id)
    game = db.get_game(game_id)
    
    if not game:
        return pd.DataFrame()
    
    # Start with (0, 0) - the starting score
    data = [{
        'hand_number': 0,
        game['team1_name']: 0,
        game['team2_name']: 0
    }]
    
    for hand in hands:
        data.append({
            'hand_number': hand['hand_number'],
            game['team1_name']: hand['team1_cumulative'],
            game['team2_name']: hand['team2_cumulative']
        })
    
    return pd.DataFrame(data)


def get_game_hands_df(game_id: int) -> pd.DataFrame:
    """Get hands for a game as a formatted DataFrame."""
    hands = db.get_hands(game_id)
    game = db.get_game(game_id)
    
    if not hands or not game:
        return pd.DataFrame()
    
    data = []
    for hand in hands:
        team_name = game['team1_name'] if hand['caller_team'] == 'team1' else game['team2_name']
        
        # Format the result
        if hand['is_euchre']:
            result = f"❌ Euchred! Lost {hand['points_scored']}, other team +{hand['other_team_points']}"
        else:
            result = f"✅ +{hand['points_scored']}"
        
        data.append({
            'Hand': hand['hand_number'],
            'Caller': hand['caller_name'],
            'Team': team_name,
            'Called': hand['call_value'],
            'Result': result,
            f"{game['team1_name']}": hand['team1_cumulative'],
            f"{game['team2_name']}": hand['team2_cumulative'],
            'Notes': hand['notes'] or ''
        })
    
    return pd.DataFrame(data)


def get_game_call_breakdown(game_id: int) -> pd.DataFrame:
    """
    Get breakdown of calls for a game.
    Returns DataFrame with: call_value, count, total_points, avg_points, euchre_count, euchre_rate
    """
    hands = db.get_hands(game_id)
    
    if not hands:
        return pd.DataFrame()
    
    df = pd.DataFrame(hands)
    
    # Group by call value
    stats = []
    for call_value in df['call_value'].unique():
        call_hands = df[df['call_value'] == call_value]
        count = len(call_hands)
        
        # Calculate points (positive when not euchred, negative when euchred)
        total_points = 0
        for _, h in call_hands.iterrows():
            if h['is_euchre']:
                total_points -= h['points_scored']
            else:
                total_points += h['points_scored']
        
        euchre_count = call_hands['is_euchre'].sum()
        
        stats.append({
            'Call': call_value,
            'Count': count,
            'Total Points': total_points,
            'Avg Points': round(total_points / count, 2) if count > 0 else 0,
            'Euchres': euchre_count,
            'Euchre Rate': f"{(euchre_count / count * 100):.1f}%" if count > 0 else "0%"
        })
    
    return pd.DataFrame(stats).sort_values('Count', ascending=False)


def get_all_games_stats() -> Dict[str, Any]:
    """Get aggregate statistics across all games."""
    games = db.get_all_games()
    hands = db.get_all_hands()
    
    if not games:
        return {
            'total_games': 0,
            'active_games': 0,
            'finished_games': 0,
            'total_hands': 0,
            'total_euchres': 0,
        }
    
    df_hands = pd.DataFrame(hands) if hands else pd.DataFrame()
    
    stats = {
        'total_games': len(games),
        'active_games': len([g for g in games if g['status'] == 'active']),
        'finished_games': len([g for g in games if g['status'] == 'finished']),
        'total_hands': len(hands),
        'total_euchres': int(df_hands['is_euchre'].sum()) if len(df_hands) > 0 else 0,
    }
    
    return stats


def get_call_value_stats() -> pd.DataFrame:
    """
    Get statistics for each call value across all games.
    Returns DataFrame with: call_value, count, total_points, avg_points, euchre_count, euchre_rate
    """
    hands = db.get_all_hands()
    
    if not hands:
        return pd.DataFrame()
    
    df = pd.DataFrame(hands)
    
    stats = []
    for call_value in df['call_value'].unique():
        call_hands = df[df['call_value'] == call_value]
        count = len(call_hands)
        
        # Calculate net points (accounting for euchres)
        total_points = 0
        for _, h in call_hands.iterrows():
            if h['is_euchre']:
                total_points -= h['points_scored']
            else:
                total_points += h['points_scored']
        
        euchre_count = int(call_hands['is_euchre'].sum())
        
        stats.append({
            'Call': call_value,
            'Count': count,
            'Total Points': total_points,
            'Avg Points': round(total_points / count, 2) if count > 0 else 0,
            'Euchres': euchre_count,
            'Euchre Rate': f"{(euchre_count / count * 100):.1f}%" if count > 0 else "0%"
        })
    
    return pd.DataFrame(stats).sort_values('Count', ascending=False)


def get_player_stats() -> pd.DataFrame:
    """
    Get statistics for each player across all games.
    Returns DataFrame with: player, hands_called, points_scored, points_lost, net_points, euchres, euchre_rate
    """
    hands = db.get_all_hands()
    games = db.get_all_games()
    
    if not hands or not games:
        return pd.DataFrame()
    
    # Build player -> team mapping per game
    game_teams = {}
    for game in games:
        game_teams[game['id']] = {
            'team1_name': game['team1_name'],
            'team2_name': game['team2_name'],
        }
    
    df = pd.DataFrame(hands)
    
    stats = []
    for player in df['caller_name'].unique():
        player_hands = df[df['caller_name'] == player]
        hands_called = len(player_hands)
        
        points_scored = 0
        points_lost = 0
        
        for _, h in player_hands.iterrows():
            if h['is_euchre']:
                points_lost += h['points_scored']
            else:
                points_scored += h['points_scored']
        
        euchre_count = int(player_hands['is_euchre'].sum())
        
        stats.append({
            'Player': player,
            'Hands Called': hands_called,
            'Points Scored': points_scored,
            'Points Lost': points_lost,
            'Net Points': points_scored - points_lost,
            'Euchres': euchre_count,
            'Euchre Rate': f"{(euchre_count / hands_called * 100):.1f}%" if hands_called > 0 else "0%"
        })
    
    return pd.DataFrame(stats).sort_values('Net Points', ascending=False)


def get_most_common_call() -> Optional[str]:
    """Get the most common call value across all games."""
    hands = db.get_all_hands()
    if not hands:
        return None
    
    df = pd.DataFrame(hands)
    return df['call_value'].mode().iloc[0] if len(df) > 0 else None


def get_team_stats() -> pd.DataFrame:
    """Get statistics for each team across all finished games."""
    games = db.get_finished_games()
    
    if not games:
        return pd.DataFrame()
    
    team_stats = {}
    
    for game in games:
        for team_key in ['team1', 'team2']:
            if team_key == 'team1':
                team_name = game['team1_name']
                score = game['team1_score']
                opponent_score = game['team2_score']
                won = game['winner'] == team_name
            else:
                team_name = game['team2_name']
                score = game['team2_score']
                opponent_score = game['team1_score']
                won = game['winner'] == team_name
            
            if team_name not in team_stats:
                team_stats[team_name] = {
                    'games': 0,
                    'wins': 0,
                    'total_points': 0,
                    'points_against': 0
                }
            
            team_stats[team_name]['games'] += 1
            team_stats[team_name]['wins'] += 1 if won else 0
            team_stats[team_name]['total_points'] += score
            team_stats[team_name]['points_against'] += opponent_score
    
    stats = []
    for team_name, data in team_stats.items():
        stats.append({
            'Team': team_name,
            'Games': data['games'],
            'Wins': data['wins'],
            'Losses': data['games'] - data['wins'],
            'Win Rate': f"{(data['wins'] / data['games'] * 100):.1f}%" if data['games'] > 0 else "0%",
            'Total Points': data['total_points'],
            'Points Against': data['points_against'],
            'Avg Points/Game': round(data['total_points'] / data['games'], 1) if data['games'] > 0 else 0
        })
    
    return pd.DataFrame(stats).sort_values('Wins', ascending=False)
