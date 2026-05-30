"""
insights.py — Color commentary for the Maester's Herald.

After every Nth hand, the herald can interject with a factoid about the
caller — their tendencies, their success rate on this call, streaks in the
current saga, lifetime milestones, lead changes, and so on.

Each fact generator takes a HandContext and returns either a natural-language
string suitable for TTS, or None if no notable observation applies. The picker
runs all generators, filters out recently-spoken duplicates, and returns one
chosen at random.

Generators must be defensive: never raise. The picker swallows exceptions
from individual generators so one buggy fact can't silence the herald.
"""
from __future__ import annotations

import random
from typing import Callable, List, Optional, Set, Tuple

import pandas as pd

import database_firestore as db


class HandContext:
    """Bundle of state describing a single just-inscribed hand."""

    def __init__(self, game: dict, hand: dict, prior_hands: list, all_hands_df: pd.DataFrame):
        self.game = game
        self.hand = hand
        self.prior_hands = prior_hands  # hands in this saga BEFORE the current one
        self.all_hands_df = all_hands_df  # includes the current hand

    @property
    def player(self) -> str:
        return self.hand['caller_name']

    @property
    def call(self) -> str:
        return self.hand['call_value']

    @property
    def is_euchre(self) -> bool:
        return bool(self.hand['is_euchre'])

    @property
    def points(self) -> int:
        return int(self.hand['points_scored'])

    @property
    def caller_team_key(self) -> str:
        return self.hand['caller_team']

    @property
    def caller_team_name(self) -> str:
        return self.game['team1_name'] if self.caller_team_key == 'team1' else self.game['team2_name']

    @property
    def opponent_team_name(self) -> str:
        return self.game['team2_name'] if self.caller_team_key == 'team1' else self.game['team1_name']

    @property
    def team1_score(self) -> int:
        return int(self.hand['team1_cumulative'])

    @property
    def team2_score(self) -> int:
        return int(self.hand['team2_cumulative'])


# ---------- helpers ----------

def _player_hands(df: pd.DataFrame, player: str) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df['caller_name'] == player]


def _pct(numerator: float, denominator: float) -> int:
    if denominator <= 0:
        return 0
    return int(round(numerator / denominator * 100))


def _ordinal(n: int) -> str:
    words = {
        1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
        6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
    }
    return words.get(n, f"{n}th")


def _leader_team_name(game: dict, t1: int, t2: int) -> Optional[str]:
    if t1 > t2:
        return game['team1_name']
    if t2 > t1:
        return game['team2_name']
    return None


# ---------- fact generators ----------

def fact_favorite_call(ctx: HandContext) -> Optional[str]:
    """Player's most-frequent call across all sagas."""
    ph = _player_hands(ctx.all_hands_df, ctx.player)
    if len(ph) < 5:
        return None
    counts = ph['call_value'].value_counts()
    fav = counts.index[0]
    pct = _pct(counts.iloc[0], len(ph))
    if pct < 30:
        return None
    if str(fav) == str(ctx.call):
        return f"{ctx.player} calls {fav}, as they do {pct} percent of the time."
    return f"{ctx.player}'s most-favored call across the realm is {fav}, made {pct} percent of the time."


def fact_career_call_success(ctx: HandContext) -> Optional[str]:
    """Success or euchre rate on the call they just made, across all sagas."""
    ph = _player_hands(ctx.all_hands_df, ctx.player)
    matches = ph[ph['call_value'] == ctx.call]
    if len(matches) < 3:
        return None
    success = int((~matches['is_euchre'].astype(bool)).sum())
    success_pct = _pct(success, len(matches))
    if success_pct >= 70:
        return f"{ctx.player} succeeds {success_pct} percent of the time on a call of {ctx.call}."
    if success_pct <= 40:
        return f"{ctx.player} gets euchred {100 - success_pct} percent of the time when calling {ctx.call}."
    return None


def fact_game_streak(ctx: HandContext) -> Optional[str]:
    """Current streak of successful or euchred calls in this saga."""
    prior_player = [h for h in ctx.prior_hands if h['caller_name'] == ctx.player]
    if not prior_player:
        return None
    streak = 1
    for h in reversed(prior_player):
        if bool(h['is_euchre']) == ctx.is_euchre:
            streak += 1
        else:
            break
    if streak < 2:
        return None
    descriptor = "euchres" if ctx.is_euchre else "successful calls"
    return f"That's {ctx.player}'s {_ordinal(streak)} {descriptor.rstrip('s')} in a row this saga."


def fact_career_milestone(ctx: HandContext) -> Optional[str]:
    """Total calls across all sagas hits a round number."""
    if ctx.all_hands_df.empty:
        return None
    total = int((ctx.all_hands_df['caller_name'] == ctx.player).sum())
    if total >= 100 and total % 100 == 0:
        return f"A century of calls for {ctx.player}, who now stands at {total} across the realm."
    if total >= 25 and total % 25 == 0:
        return f"That brings {ctx.player} to {total} calls across the realm."
    return None


def fact_lead_change(ctx: HandContext) -> Optional[str]:
    """Did the leading team change with this hand?"""
    if not ctx.prior_hands:
        return None
    prev = ctx.prior_hands[-1]
    prev_lead = _leader_team_name(ctx.game, int(prev['team1_cumulative']), int(prev['team2_cumulative']))
    new_lead = _leader_team_name(ctx.game, ctx.team1_score, ctx.team2_score)
    if new_lead is None or prev_lead == new_lead:
        return None
    return f"With that, {new_lead} seizes the lead."


def fact_close_to_victory(ctx: HandContext) -> Optional[str]:
    """One of the teams is within striking distance of the target."""
    target = int(ctx.game.get('target_score') or 0)
    if target <= 0:
        return None
    t1_gap = target - ctx.team1_score
    t2_gap = target - ctx.team2_score
    closest = min(t1_gap, t2_gap)
    if 1 <= closest <= 5:
        team = ctx.game['team1_name'] if t1_gap < t2_gap else ctx.game['team2_name']
        plural = "" if closest == 1 else "s"
        return f"Only {closest} point{plural} stand between {team} and victory."
    return None


def fact_personal_best(ctx: HandContext) -> Optional[str]:
    """Did this hand match or beat the player's highest single-hand take?"""
    if ctx.is_euchre or ctx.points <= 0:
        return None
    ph = _player_hands(ctx.all_hands_df, ctx.player)
    successes = ph[~ph['is_euchre'].astype(bool)]
    if len(successes) < 4:
        return None
    best = int(successes['points_scored'].max())
    if ctx.points == best and best > 0:
        return f"{ctx.player} matches their personal best of {best} points on a single hand."
    return None


def fact_partnership_record(ctx: HandContext) -> Optional[str]:
    """Win-rate of caller paired with one of their teammates in finished sagas."""
    team_players = ctx.game.get(f"{ctx.caller_team_key}_players") or []
    teammates = [p for p in team_players if p != ctx.player]
    if not teammates:
        return None
    partner = random.choice(teammates)

    games = db.get_all_games()
    paired = 0
    won = 0
    for g in games:
        if g.get('status') != 'finished':
            continue
        for tk in ('team1', 'team2'):
            players = g.get(f"{tk}_players") or []
            if ctx.player in players and partner in players:
                paired += 1
                if g.get('winner') == g.get(f"{tk}_name"):
                    won += 1
    if paired < 3:
        return None
    pct = _pct(won, paired)
    return f"{ctx.player} and {partner} have won {pct} percent of the sagas they've fought together."


def fact_lifetime_net_points(ctx: HandContext) -> Optional[str]:
    """Caller's lifetime net points across all sagas, surfaced at round numbers."""
    ph = _player_hands(ctx.all_hands_df, ctx.player)
    if ph.empty:
        return None
    pts = ph['points_scored'].astype(int)
    eu = ph['is_euchre'].astype(bool)
    net = int(pts[~eu].sum() - pts[eu].sum())
    if abs(net) >= 50 and abs(net) % 50 == 0:
        sign = "" if net >= 0 else "negative "
        return f"{ctx.player}'s lifetime tally now stands at {sign}{abs(net)} net points across the realm."
    return None


def fact_this_call_this_saga(ctx: HandContext) -> Optional[str]:
    """Count of this exact call by this player so far this saga."""
    count = sum(
        1 for h in ctx.prior_hands
        if h['caller_name'] == ctx.player and str(h['call_value']) == str(ctx.call)
    ) + 1
    if count >= 3:
        return f"{ctx.player} has called {ctx.call} {count} times this saga alone."
    return None


def fact_realm_call_average(ctx: HandContext) -> Optional[str]:
    """Compare caller's per-call success rate to the realm's overall average."""
    ph = _player_hands(ctx.all_hands_df, ctx.player)
    if len(ph) < 8 or ctx.all_hands_df.empty:
        return None
    player_success = _pct((~ph['is_euchre'].astype(bool)).sum(), len(ph))
    realm_success = _pct((~ctx.all_hands_df['is_euchre'].astype(bool)).sum(), len(ctx.all_hands_df))
    diff = player_success - realm_success
    if diff >= 15:
        return f"{ctx.player} succeeds on calls {diff} points more often than the realm's average."
    if diff <= -15:
        return f"{ctx.player} is euchred {-diff} points more often than the realm's average."
    return None


def fact_call_recap(ctx: HandContext) -> Optional[str]:
    """Always-fires baseline. Used only as a last-resort fallback inside
    pick_fact_for_hand when no notable, threshold-based generator applies —
    so the herald always has *something* stat-flavored to say.

    NOT included in FACT_GENERATORS; the picker invokes it directly.
    """
    ph = _player_hands(ctx.all_hands_df, ctx.player)
    career = len(ph)
    saga = sum(1 for h in ctx.prior_hands if h['caller_name'] == ctx.player) + 1

    if ctx.is_euchre:
        if career >= 5:
            eu_pct = _pct(int(ph['is_euchre'].astype(bool).sum()), career)
            return (
                f"{ctx.player} is euchred — roughly {eu_pct} percent of "
                f"their career calls end this way."
            )
        return f"{ctx.player}'s call of {ctx.call} ends in a euchre."

    if career == 1:
        return f"{ctx.player}'s first call across the realm earns {ctx.points} points."
    if saga == 1:
        return f"{ctx.player}'s first call of the saga earns {ctx.points} points."
    return (
        f"{ctx.player}'s call of {ctx.call} earns {ctx.points} points — "
        f"their {_ordinal(saga)} call this saga."
    )


# ---------- picker ----------

FactFn = Callable[[HandContext], Optional[str]]

FACT_GENERATORS: List[FactFn] = [
    fact_favorite_call,
    fact_career_call_success,
    fact_game_streak,
    fact_career_milestone,
    fact_lead_change,
    fact_close_to_victory,
    fact_personal_best,
    fact_partnership_record,
    fact_lifetime_net_points,
    fact_this_call_this_saga,
    fact_realm_call_average,
]


def pick_fact_for_hand(
    game_id: str,
    recently_spoken_keys: Optional[Set[str]] = None,
) -> Optional[Tuple[str, str]]:
    """Return (generator_name, spoken_text) for an interesting fact about the
    most recent hand in `game_id`, or None if nothing notable applies. Pass
    the set of recently-spoken generator names to suppress immediate repeats.

    Falls back to fact_call_recap (an always-fires stat-flavored line) when
    none of the threshold-based generators apply, so the herald always has
    something to say. The recap generator is not bound by recently_spoken_keys.
    """
    if recently_spoken_keys is None:
        recently_spoken_keys = set()

    game = db.get_game(game_id)
    if not game:
        return None
    hands = db.get_hands(game_id)
    if not hands:
        return None

    latest = hands[-1]
    prior = hands[:-1]

    all_hands = db.get_all_hands() or []
    all_hands_df = pd.DataFrame(all_hands) if all_hands else pd.DataFrame()

    ctx = HandContext(game=game, hand=latest, prior_hands=prior, all_hands_df=all_hands_df)

    # First pass: notable generators, filtered to avoid immediate repeats
    candidates: List[Tuple[str, str]] = []
    for gen in FACT_GENERATORS:
        try:
            text = gen(ctx)
        except Exception:
            text = None  # never let a buggy generator break the herald
        if not text:
            continue
        key = gen.__name__
        if key in recently_spoken_keys:
            continue
        candidates.append((key, text))

    if candidates:
        return random.choice(candidates)

    # Second pass: relax the "recently spoken" filter — better to repeat than
    # be silent during long droughts of notable facts.
    relaxed: List[Tuple[str, str]] = []
    for gen in FACT_GENERATORS:
        try:
            text = gen(ctx)
        except Exception:
            text = None
        if text:
            relaxed.append((gen.__name__, text))
    if relaxed:
        return random.choice(relaxed)

    # Last resort: always-fires recap so the herald has something to say.
    try:
        recap = fact_call_recap(ctx)
        if recap:
            return ("fact_call_recap", recap)
    except Exception:
        pass
    return None
