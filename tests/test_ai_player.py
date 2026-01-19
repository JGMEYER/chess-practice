"""Tests for AIPlayer skill-adjusted move selection."""

import pytest
from unittest.mock import Mock, patch

from chess.ai_player import AIPlayer


class TestEloToSigma:
    """Test Elo to noise sigma conversion."""

    def test_min_elo_gives_max_sigma(self):
        """At minimum Elo (300), noise should be maximum (400 cp)."""
        ai = Mock()
        ai.elo = AIPlayer.MIN_ELO
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO
        ai.MAX_SIGMA = AIPlayer.MAX_SIGMA

        sigma = AIPlayer._elo_to_sigma(ai, AIPlayer.MIN_ELO)
        assert sigma == AIPlayer.MAX_SIGMA

    def test_max_elo_gives_zero_sigma(self):
        """At maximum Elo (2000), noise should be zero."""
        ai = Mock()
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO
        ai.MAX_SIGMA = AIPlayer.MAX_SIGMA

        sigma = AIPlayer._elo_to_sigma(ai, AIPlayer.MAX_ELO)
        assert sigma == 0

    def test_mid_elo_gives_mid_sigma(self):
        """At midpoint Elo (1150), noise should be roughly half."""
        ai = Mock()
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO
        ai.MAX_SIGMA = AIPlayer.MAX_SIGMA

        mid_elo = (AIPlayer.MIN_ELO + AIPlayer.MAX_ELO) // 2
        sigma = AIPlayer._elo_to_sigma(ai, mid_elo)
        # Should be approximately half of MAX_SIGMA
        assert 180 < sigma < 220  # Allow some tolerance for integer rounding

    def test_elo_below_min_clamps_to_max_sigma(self):
        """Elo below minimum should clamp and give max sigma."""
        ai = Mock()
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO
        ai.MAX_SIGMA = AIPlayer.MAX_SIGMA

        sigma = AIPlayer._elo_to_sigma(ai, 100)  # Below MIN_ELO
        assert sigma == AIPlayer.MAX_SIGMA

    def test_elo_above_max_clamps_to_zero_sigma(self):
        """Elo above maximum should clamp and give zero sigma."""
        ai = Mock()
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO
        ai.MAX_SIGMA = AIPlayer.MAX_SIGMA

        sigma = AIPlayer._elo_to_sigma(ai, 2500)  # Above MAX_ELO
        assert sigma == 0


class TestSelectMoveBySkill:
    """Test skill-adjusted move selection."""

    def test_max_elo_always_picks_best_move(self):
        """At max Elo, should always return the top move."""
        ai = Mock()
        ai.elo = AIPlayer.MAX_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO

        top_moves = [
            {"Move": "e2e4", "Centipawn": 50, "Mate": None},
            {"Move": "d2d4", "Centipawn": 40, "Mate": None},
            {"Move": "g1f3", "Centipawn": 30, "Mate": None},
        ]

        # At max Elo, should always pick best move
        move = AIPlayer._select_move_by_skill(ai, top_moves)
        assert move == "e2e4"

    def test_handles_mate_scores(self):
        """Should correctly handle mate-in-N scores."""
        ai = Mock()
        ai.elo = AIPlayer.MAX_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO

        top_moves = [
            {"Move": "d8h4", "Centipawn": None, "Mate": 2},  # Mate in 2 - winning
            {"Move": "e2e4", "Centipawn": 50, "Mate": None},
            {"Move": "d2d4", "Centipawn": 40, "Mate": None},
        ]

        move = AIPlayer._select_move_by_skill(ai, top_moves)
        assert move == "d8h4"  # Should pick the mating move

    def test_fallback_when_no_candidates(self):
        """Should fall back to first move if scoring fails."""
        ai = Mock()
        ai.elo = AIPlayer.MAX_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO

        # Edge case: moves with no evaluation
        top_moves = [
            {"Move": "e2e4", "Centipawn": None, "Mate": None},
        ]

        move = AIPlayer._select_move_by_skill(ai, top_moves)
        assert move == "e2e4"


class TestSetElo:
    """Test Elo setting and clamping."""

    def test_set_elo_clamps_to_min(self):
        """Setting Elo below minimum should clamp."""
        ai = Mock()
        ai.elo = 1000
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO

        AIPlayer.set_elo(ai, 100)
        assert ai.elo == AIPlayer.MIN_ELO

    def test_set_elo_clamps_to_max(self):
        """Setting Elo above maximum should clamp."""
        ai = Mock()
        ai.elo = 1000
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO

        AIPlayer.set_elo(ai, 3000)
        assert ai.elo == AIPlayer.MAX_ELO

    def test_set_elo_valid_value(self):
        """Setting valid Elo should work."""
        ai = Mock()
        ai.elo = 1000
        ai.MIN_ELO = AIPlayer.MIN_ELO
        ai.MAX_ELO = AIPlayer.MAX_ELO

        AIPlayer.set_elo(ai, 1500)
        assert ai.elo == 1500
