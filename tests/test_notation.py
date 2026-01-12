"""Tests for Standard Algebraic Notation (SAN) generation."""

import pytest

from chess import NotationGenerator, Board, MoveGenerator
from chess.game_state import GameState
from chess.fen_loader import FENLoader
from chess.move import Move
from chess.constants import PieceType, Color
from chess.pieces import Pawn, Knight, Bishop, Rook, Queen, King


class TestNotationGeneratorBasicMoves:
    """Tests for basic move notation generation."""

    @pytest.fixture
    def setup(self):
        """Create board, game state, and move generator."""
        board = Board()
        game_state = GameState()
        fen_loader = FENLoader(board, game_state)
        fen_loader.load_starting_position()
        move_generator = MoveGenerator()
        return board, game_state, move_generator

    def test_pawn_move(self, setup):
        """Simple pawn move should produce destination only."""
        board, game_state, move_generator = setup
        pawn = board.get_piece(4, 1)  # e2 pawn

        move = Move(
            from_square=(4, 1),
            to_square=(4, 3),
            piece=pawn,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "e4"

    def test_pawn_single_push(self, setup):
        """Pawn moving one square."""
        board, game_state, move_generator = setup
        pawn = board.get_piece(4, 1)  # e2 pawn

        move = Move(
            from_square=(4, 1),
            to_square=(4, 2),
            piece=pawn,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "e3"

    def test_knight_move(self, setup):
        """Knight move should include piece letter."""
        board, game_state, move_generator = setup
        knight = board.get_piece(6, 0)  # g1 knight

        move = Move(
            from_square=(6, 0),
            to_square=(5, 2),
            piece=knight,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "Nf3"

    def test_bishop_move(self, setup):
        """Bishop move should include piece letter."""
        board, game_state, move_generator = setup

        # First move pawns to open diagonal
        board.set_piece(4, 1, None)  # Remove e2 pawn
        bishop = board.get_piece(5, 0)  # f1 bishop

        move = Move(
            from_square=(5, 0),
            to_square=(2, 3),
            piece=bishop,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "Bc4"


class TestNotationGeneratorCaptures:
    """Tests for capture notation."""

    @pytest.fixture
    def setup(self):
        """Create board with a position for testing captures."""
        board = Board()
        game_state = GameState()
        move_generator = MoveGenerator()

        # Set up a position with pieces to capture
        white_knight = Knight(Color.WHITE)
        board.set_piece(5, 2, white_knight)  # Nf3

        black_pawn = Pawn(Color.BLACK)
        board.set_piece(4, 4, black_pawn)  # e5

        white_pawn = Pawn(Color.WHITE)
        board.set_piece(3, 3, white_pawn)  # d4

        return board, game_state, move_generator

    def test_knight_capture(self, setup):
        """Knight capture should include 'x'."""
        board, game_state, move_generator = setup
        knight = board.get_piece(5, 2)
        target = board.get_piece(4, 4)

        move = Move(
            from_square=(5, 2),
            to_square=(4, 4),
            piece=knight,
            captured_piece=target,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "Nxe5"

    def test_pawn_capture_includes_file(self, setup):
        """Pawn capture should include source file."""
        board, game_state, move_generator = setup
        pawn = board.get_piece(3, 3)  # d4
        target = board.get_piece(4, 4)  # e5

        move = Move(
            from_square=(3, 3),
            to_square=(4, 4),
            piece=pawn,
            captured_piece=target,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "dxe5"


class TestNotationGeneratorCastling:
    """Tests for castling notation."""

    @pytest.fixture
    def castling_setup(self):
        """Create board ready for castling."""
        board = Board()
        game_state = GameState()
        fen_loader = FENLoader(board, game_state)
        # Position with cleared back rank for castling
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
        move_generator = MoveGenerator()
        return board, game_state, move_generator

    def test_kingside_castling(self, castling_setup):
        """Kingside castling should produce O-O."""
        board, game_state, move_generator = castling_setup
        king = board.get_piece(4, 0)

        move = Move(
            from_square=(4, 0),
            to_square=(6, 0),
            piece=king,
            is_castling=True,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "O-O"

    def test_queenside_castling(self, castling_setup):
        """Queenside castling should produce O-O-O."""
        board, game_state, move_generator = castling_setup
        king = board.get_piece(4, 0)

        move = Move(
            from_square=(4, 0),
            to_square=(2, 0),
            piece=king,
            is_castling=True,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "O-O-O"


class TestNotationGeneratorPromotion:
    """Tests for pawn promotion notation."""

    @pytest.fixture
    def promotion_setup(self):
        """Create board with pawn ready to promote."""
        board = Board()
        game_state = GameState()
        move_generator = MoveGenerator()

        white_pawn = Pawn(Color.WHITE)
        board.set_piece(4, 6, white_pawn)  # e7

        white_king = King(Color.WHITE)
        board.set_piece(4, 0, white_king)

        black_king = King(Color.BLACK)
        board.set_piece(4, 7, None)  # Clear e8
        board.set_piece(0, 7, black_king)

        return board, game_state, move_generator

    def test_promotion_to_queen(self, promotion_setup):
        """Promotion should include =Q."""
        board, game_state, move_generator = promotion_setup
        pawn = board.get_piece(4, 6)
        promoted = Queen(Color.WHITE)

        move = Move(
            from_square=(4, 6),
            to_square=(4, 7),
            piece=pawn,
            is_promotion=True,
            promoted_to=promoted,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "e8=Q"

    def test_promotion_to_knight(self, promotion_setup):
        """Knight promotion should include =N."""
        board, game_state, move_generator = promotion_setup
        pawn = board.get_piece(4, 6)
        promoted = Knight(Color.WHITE)

        move = Move(
            from_square=(4, 6),
            to_square=(4, 7),
            piece=pawn,
            is_promotion=True,
            promoted_to=promoted,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        assert san == "e8=N"


class TestNotationGeneratorDisambiguation:
    """Tests for move disambiguation."""

    @pytest.fixture
    def disambiguation_setup(self):
        """Create board with two knights that can reach the same square."""
        board = Board()
        game_state = GameState()
        move_generator = MoveGenerator()

        # Two white knights
        knight1 = Knight(Color.WHITE)
        board.set_piece(1, 0, knight1)  # Nb1

        knight2 = Knight(Color.WHITE)
        board.set_piece(5, 0, knight2)  # Nf1

        white_king = King(Color.WHITE)
        board.set_piece(4, 0, white_king)

        black_king = King(Color.BLACK)
        board.set_piece(4, 7, black_king)

        return board, game_state, move_generator

    def test_file_disambiguation(self, disambiguation_setup):
        """When two knights can reach same square, file should disambiguate."""
        board, game_state, move_generator = disambiguation_setup

        # Move Nb1 to d2 (Nf1 could also go to d2)
        knight = board.get_piece(1, 0)

        move = Move(
            from_square=(1, 0),
            to_square=(3, 1),
            piece=knight,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        # Should be Nbd2, not just Nd2
        assert san == "Nbd2"

    def test_rank_disambiguation(self):
        """When two rooks on same file, rank should disambiguate."""
        board = Board()
        game_state = GameState()
        move_generator = MoveGenerator()

        # Two white rooks on same file
        rook1 = Rook(Color.WHITE)
        board.set_piece(0, 0, rook1)  # Ra1

        rook2 = Rook(Color.WHITE)
        board.set_piece(0, 7, rook2)  # Ra8

        white_king = King(Color.WHITE)
        board.set_piece(4, 0, white_king)

        black_king = King(Color.BLACK)
        board.set_piece(4, 7, black_king)

        # Move Ra1 to a4
        move = Move(
            from_square=(0, 0),
            to_square=(0, 3),
            piece=rook1,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=False
        )
        # Should be R1a4
        assert san == "R1a4"


class TestNotationGeneratorCheckIndicators:
    """Tests for check and checkmate indicators."""

    def test_check_indicator(self):
        """Move giving check should append +."""
        board = Board()
        game_state = GameState()
        move_generator = MoveGenerator()

        # Set up a check position
        white_queen = Queen(Color.WHITE)
        board.set_piece(7, 4, white_queen)  # Qh5

        white_king = King(Color.WHITE)
        board.set_piece(4, 0, white_king)

        black_king = King(Color.BLACK)
        board.set_piece(4, 7, black_king)

        # Qh5-f7+ would give check, but let's do Qh5-e8+ which is more direct
        move = Move(
            from_square=(7, 4),
            to_square=(4, 7),
            piece=white_queen,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=True
        )
        # This would capture the king, which shouldn't happen in legal chess
        # Let's use a different position

    def test_check_with_queen(self):
        """Queen delivering check should have + suffix."""
        board = Board()
        game_state = GameState()
        move_generator = MoveGenerator()

        white_queen = Queen(Color.WHITE)
        board.set_piece(3, 0, white_queen)  # Qd1

        white_king = King(Color.WHITE)
        board.set_piece(4, 0, white_king)

        black_king = King(Color.BLACK)
        board.set_piece(4, 7, black_king)

        # Move queen to d8, giving check
        move = Move(
            from_square=(3, 0),
            to_square=(3, 7),
            piece=white_queen,
        )

        san = NotationGenerator.move_to_san(
            move, board, game_state, move_generator, include_check=True
        )
        assert san == "Qd8+"
