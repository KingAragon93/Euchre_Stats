"""
Data models for Euchre Stats application.
Provides dataclasses and helper types.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Hand:
    """Represents a single hand in a game."""
    id: int
    game_id: int
    hand_number: int
    caller_name: str
    caller_team: str  # "team1" or "team2"
    call_value: str
    points_scored: int
    is_euchre: bool
    other_team_points: int
    team1_delta: int
    team2_delta: int
    team1_cumulative: int
    team2_cumulative: int
    notes: Optional[str]
    created_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Hand':
        """Create Hand from dictionary (database row)."""
        return cls(
            id=data['id'],
            game_id=data['game_id'],
            hand_number=data['hand_number'],
            caller_name=data['caller_name'],
            caller_team=data['caller_team'],
            call_value=data['call_value'],
            points_scored=data['points_scored'],
            is_euchre=bool(data['is_euchre']),
            other_team_points=data['other_team_points'],
            team1_delta=data['team1_delta'],
            team2_delta=data['team2_delta'],
            team1_cumulative=data['team1_cumulative'],
            team2_cumulative=data['team2_cumulative'],
            notes=data['notes'],
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class Game:
    """Represents a Euchre game."""
    id: int
    team1_name: str
    team2_name: str
    team1_players: List[str]
    team2_players: List[str]
    team1_score: int
    team2_score: int
    target_score: int
    status: str  # "active" or "finished"
    winner: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]
    hands: List[Hand] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict, hands: List[Hand] = None) -> 'Game':
        """Create Game from dictionary (database row)."""
        return cls(
            id=data['id'],
            team1_name=data['team1_name'],
            team2_name=data['team2_name'],
            team1_players=data['team1_players'],
            team2_players=data['team2_players'],
            team1_score=data['team1_score'],
            team2_score=data['team2_score'],
            target_score=data['target_score'],
            status=data['status'],
            winner=data['winner'],
            created_at=datetime.fromisoformat(data['created_at']),
            finished_at=datetime.fromisoformat(data['finished_at']) if data['finished_at'] else None,
            hands=hands or []
        )
    
    @property
    def is_active(self) -> bool:
        return self.status == 'active'
    
    @property
    def is_finished(self) -> bool:
        return self.status == 'finished'
    
    def get_all_players(self) -> List[str]:
        """Get all players in the game."""
        return self.team1_players + self.team2_players
    
    def get_player_team(self, player_name: str) -> Optional[str]:
        """Get which team a player is on."""
        if player_name in self.team1_players:
            return "team1"
        elif player_name in self.team2_players:
            return "team2"
        return None
    
    def get_team_name(self, team_key: str) -> str:
        """Get team name from team key (team1/team2)."""
        if team_key == "team1":
            return self.team1_name
        return self.team2_name


# Common call values for quick selection (3-8 for house rules)
COMMON_CALL_VALUES = [
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "Partner Best",
    "Alone",
]

# Default euchre penalty points per call type
DEFAULT_EUCHRE_PENALTIES = {
    "Partner Best": 1,
    "Alone": 2,
}
