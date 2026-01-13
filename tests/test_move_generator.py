import pytest

from chess import Board, Color
from chess.pieces import Knight, Rook
from chess.move_generator import MoveGenerator
from chess.game_state import GameState


@pytest.fixture
def move_gen():
    return MoveGenerator()


@pytest.fixture
def empty_board():
    return Board()


@pytest.fixture
def game_state():
    return GameState()


class TestKnightMoves:
    """Tests for knight move generation."""

    def test_knight_moves_from_center(self, move_gen, empty_board, game_state):
        """Knight in center should have 8 possible moves."""
        knight = Knight(Color.WHITE)
        empty_board.set_piece(4, 4, knight)  # e5

        moves = move_gen.get_possible_moves(empty_board, knight, game_state)

        assert len(moves) == 8
        expected = [
            (6, 5), (6, 3),  # Right 2, up/down 1
            (2, 5), (2, 3),  # Left 2, up/down 1
            (5, 6), (5, 2),  # Right 1, up/down 2
            (3, 6), (3, 2),  # Left 1, up/down 2
        ]
        assert set(moves) == set(expected)

    def test_knight_moves_from_corner(self, move_gen, empty_board, game_state):
        """Knight in corner should have 2 possible moves."""
        knight = Knight(Color.WHITE)
        empty_board.set_piece(0, 0, knight)  # a1

        moves = move_gen.get_possible_moves(empty_board, knight, game_state)

        assert len(moves) == 2
        expected = [(2, 1), (1, 2)]
        assert set(moves) == set(expected)

    def test_knight_blocked_by_friendly(self, move_gen, empty_board, game_state):
        """Knight cannot land on friendly piece."""
        knight = Knight(Color.WHITE)
        friendly_rook = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, knight)
        empty_board.set_piece(6, 5, friendly_rook)  # Block one destination

        moves = move_gen.get_possible_moves(empty_board, knight, game_state)

        assert len(moves) == 7
        assert (6, 5) not in moves

    def test_knight_can_capture_enemy(self, move_gen, empty_board, game_state):
        """Knight can capture enemy piece."""
        knight = Knight(Color.WHITE)
        enemy_rook = Rook(Color.BLACK)
        empty_board.set_piece(4, 4, knight)
        empty_board.set_piece(6, 5, enemy_rook)

        moves = move_gen.get_possible_moves(empty_board, knight, game_state)

        assert len(moves) == 8
        assert (6, 5) in moves  # Can capture


class TestRookMoves:
    """Tests for rook move generation."""

    def test_rook_moves_on_empty_board(self, move_gen, empty_board, game_state):
        """Rook on empty board should have 14 possible moves."""
        rook = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, rook)  # e5

        moves = move_gen.get_possible_moves(empty_board, rook, game_state)

        # 7 squares in each direction (horizontal + vertical) = 14 total
        assert len(moves) == 14

    def test_rook_blocked_by_friendly(self, move_gen, empty_board, game_state):
        """Rook stops before friendly piece."""
        rook = Rook(Color.WHITE)
        friendly = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, rook)
        empty_board.set_piece(4, 6, friendly)  # Block upward

        moves = move_gen.get_possible_moves(empty_board, rook, game_state)

        # Can move to rank 5, but not 6 or 7
        assert (4, 5) in moves
        assert (4, 6) not in moves
        assert (4, 7) not in moves

    def test_rook_captures_enemy(self, move_gen, empty_board, game_state):
        """Rook can capture enemy but stops there."""
        rook = Rook(Color.WHITE)
        enemy = Rook(Color.BLACK)
        empty_board.set_piece(4, 4, rook)
        empty_board.set_piece(4, 6, enemy)  # Enemy upward

        moves = move_gen.get_possible_moves(empty_board, rook, game_state)

        # Can move to rank 5 and capture on 6, but not 7
        assert (4, 5) in moves
        assert (4, 6) in moves  # Can capture
        assert (4, 7) not in moves  # Can't go past

    def test_rook_blocked_multiple_directions(self, move_gen, empty_board, game_state):
        """Rook blocked in multiple directions."""
        rook = Rook(Color.WHITE)
        empty_board.set_piece(4, 4, rook)
        empty_board.set_piece(4, 5, Rook(Color.WHITE))  # Block up
        empty_board.set_piece(4, 3, Rook(Color.WHITE))  # Block down
        empty_board.set_piece(5, 4, Rook(Color.WHITE))  # Block right
        empty_board.set_piece(3, 4, Rook(Color.WHITE))  # Block left

        moves = move_gen.get_possible_moves(empty_board, rook, game_state)

        assert len(moves) == 0


class TestPawnMoves:
    """Tests for pawn move generation."""

    def test_white_pawn_single_move(self, move_gen, empty_board, game_state):
        """White pawn can move one square forward."""
        from chess.pieces import Pawn
        pawn = Pawn(Color.WHITE)
        empty_board.set_piece(4, 3, pawn)  # e4

        moves = move_gen.get_possible_moves(empty_board, pawn, game_state)

        assert (4, 4) in moves  # e5

    def test_white_pawn_double_move_from_start(self, move_gen, empty_board, game_state):
        """White pawn can move two squares from starting rank."""
        from chess.pieces import Pawn
        pawn = Pawn(Color.WHITE)
        empty_board.set_piece(4, 1, pawn)  # e2

        moves = move_gen.get_possible_moves(empty_board, pawn, game_state)

        assert (4, 2) in moves  # e3
        assert (4, 3) in moves  # e4

    def test_black_pawn_double_move_from_start(self, move_gen, empty_board, game_state):
        """Black pawn can move two squares from starting rank."""
        from chess.pieces import Pawn
        pawn = Pawn(Color.BLACK)
        empty_board.set_piece(4, 6, pawn)  # e7

        moves = move_gen.get_possible_moves(empty_board, pawn, game_state)

        assert (4, 5) in moves  # e6
        assert (4, 4) in moves  # e5

    def test_pawn_cannot_double_move_after_leaving_start(self, move_gen, empty_board, game_state):
        """Pawn cannot move two squares if not on starting rank."""
        from chess.pieces import Pawn
        pawn = Pawn(Color.WHITE)
        empty_board.set_piece(4, 2, pawn)  # e3 (not starting rank)

        moves = move_gen.get_possible_moves(empty_board, pawn, game_state)

        assert (4, 3) in moves  # e4 - single move ok
        assert (4, 4) not in moves  # e5 - no double move

    def test_pawn_blocked_by_piece_in_front(self, move_gen, empty_board, game_state):
        """Pawn cannot move if blocked by piece directly in front."""
        from chess.pieces import Pawn
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)
        empty_board.set_piece(4, 3, white_pawn)  # e4
        empty_board.set_piece(4, 4, black_pawn)  # e5 - blocking

        moves = move_gen.get_possible_moves(empty_board, white_pawn, game_state)

        assert (4, 4) not in moves  # Blocked
        assert (4, 5) not in moves  # Can't jump

    def test_pawn_cannot_jump_over_piece_on_double_move(self, move_gen, empty_board, game_state):
        """Pawn cannot jump over a piece when moving two squares."""
        from chess.pieces import Pawn
        white_pawn = Pawn(Color.WHITE)
        blocking_pawn = Pawn(Color.BLACK)
        empty_board.set_piece(4, 1, white_pawn)  # e2
        empty_board.set_piece(4, 2, blocking_pawn)  # e3 - blocking intermediate square

        moves = move_gen.get_possible_moves(empty_board, white_pawn, game_state)

        assert (4, 2) not in moves  # Blocked by piece
        assert (4, 3) not in moves  # Cannot jump over piece

    def test_black_pawn_cannot_jump_over_piece_on_double_move(self, move_gen, empty_board, game_state):
        """Black pawn cannot jump over a piece when moving two squares."""
        from chess.pieces import Pawn
        black_pawn = Pawn(Color.BLACK)
        blocking_pawn = Pawn(Color.WHITE)
        empty_board.set_piece(4, 6, black_pawn)  # e7
        empty_board.set_piece(4, 5, blocking_pawn)  # e6 - blocking intermediate square

        moves = move_gen.get_possible_moves(empty_board, black_pawn, game_state)

        assert (4, 5) not in moves  # Blocked by piece
        assert (4, 4) not in moves  # Cannot jump over piece

    def test_pawn_can_capture_diagonally(self, move_gen, empty_board, game_state):
        """Pawn can capture enemy pieces diagonally."""
        from chess.pieces import Pawn
        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)
        empty_board.set_piece(4, 3, white_pawn)  # e4
        empty_board.set_piece(5, 4, black_pawn)  # f5 - capturable

        moves = move_gen.get_possible_moves(empty_board, white_pawn, game_state)

        assert (5, 4) in moves  # Can capture

    def test_pawn_cannot_capture_friendly_diagonally(self, move_gen, empty_board, game_state):
        """Pawn cannot capture friendly pieces diagonally."""
        from chess.pieces import Pawn
        white_pawn1 = Pawn(Color.WHITE)
        white_pawn2 = Pawn(Color.WHITE)
        empty_board.set_piece(4, 3, white_pawn1)  # e4
        empty_board.set_piece(5, 4, white_pawn2)  # f5 - friendly

        moves = move_gen.get_possible_moves(empty_board, white_pawn1, game_state)

        assert (5, 4) not in moves  # Cannot capture friendly


class TestEnPassant:
    """Tests for en passant move generation."""

    def test_en_passant_available(self, move_gen, empty_board, game_state):
        """Pawn can capture en passant when available."""
        from chess.pieces import Pawn
        from chess.move import Move

        white_pawn = Pawn(Color.WHITE)
        black_pawn = Pawn(Color.BLACK)
        empty_board.set_piece(4, 4, white_pawn)  # e5
        empty_board.set_piece(5, 4, black_pawn)  # f5

        # Simulate black just moved f7-f5 (set up en passant target)
        # The target is the square the pawn passed over (f6), but we store the pawn position
        game_state._initial_en_passant_target = (5, 4)  # f5 - where the pawn is

        # Actually, current_en_passant_target returns from move history or initial
        # Let's create a move that sets up en passant properly
        # We need to simulate that black's last move was f7-f5, creating en passant opportunity
        black_pawn_for_move = Pawn(Color.BLACK)
        move = Move(
            from_square=(5, 6),
            to_square=(5, 4),
            piece=black_pawn_for_move,
            current_en_passant_target=(5, 4),  # f5
        )
        game_state.move_history.append(move)
        game_state.current_turn = Color.WHITE  # It's white's turn now

        moves = move_gen.get_possible_moves(empty_board, white_pawn, game_state)

        # White can capture en passant on f6
        assert (5, 5) in moves


class TestCastling:
    """Tests for castling move generation."""

    def test_kingside_castling_available(self, move_gen, game_state):
        """King can castle kingside when path is clear."""
        from chess import Board
        from chess.fen_loader import FENLoader

        board = Board()
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        king = board.get_piece(4, 0)  # e1
        moves = move_gen.get_legal_moves(board, king, game_state)

        assert (6, 0) in moves  # g1 - kingside castling

    def test_queenside_castling_available(self, move_gen, game_state):
        """King can castle queenside when path is clear."""
        from chess import Board
        from chess.fen_loader import FENLoader

        board = Board()
        fen_loader = FENLoader(board, game_state)
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")

        king = board.get_piece(4, 0)  # e1
        moves = move_gen.get_legal_moves(board, king, game_state)

        assert (2, 0) in moves  # c1 - queenside castling

    def test_cannot_castle_through_pieces(self, move_gen, game_state):
        """King cannot castle if pieces block the path."""
        from chess import Board
        from chess.fen_loader import FENLoader

        board = Board()
        fen_loader = FENLoader(board, game_state)
        # Bishop on f1 blocks kingside castling
        fen_loader.load("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3KB1R w KQkq - 0 1")

        king = board.get_piece(4, 0)  # e1
        moves = move_gen.get_legal_moves(board, king, game_state)

        assert (6, 0) not in moves  # Cannot castle kingside

    def test_cannot_castle_out_of_check(self, move_gen, game_state):
        """King cannot castle while in check."""
        from chess import Board
        from chess.fen_loader import FENLoader

        board = Board()
        fen_loader = FENLoader(board, game_state)
        # Black rook on e8 gives check
        fen_loader.load("4r3/8/8/8/8/8/8/R3K2R w KQ - 0 1")

        king = board.get_piece(4, 0)  # e1
        moves = move_gen.get_legal_moves(board, king, game_state)

        assert (6, 0) not in moves  # Cannot castle kingside
        assert (2, 0) not in moves  # Cannot castle queenside

    def test_cannot_castle_through_check(self, move_gen, game_state):
        """King cannot castle through attacked squares."""
        from chess import Board
        from chess.fen_loader import FENLoader

        board = Board()
        fen_loader = FENLoader(board, game_state)
        # Black rook on f8 attacks f1, blocking kingside castling
        fen_loader.load("5r2/8/8/8/8/8/8/R3K2R w KQ - 0 1")

        king = board.get_piece(4, 0)  # e1
        moves = move_gen.get_legal_moves(board, king, game_state)

        assert (6, 0) not in moves  # Cannot castle through f1


class TestCheckDetection:
    """Tests for check detection."""

    def test_is_in_check_by_rook(self, move_gen, empty_board):
        """Detect check from rook."""
        from chess.pieces import King
        white_king = King(Color.WHITE)
        black_rook = Rook(Color.BLACK)
        empty_board.set_piece(4, 0, white_king)  # e1
        empty_board.set_piece(4, 7, black_rook)  # e8 - attacking along file

        assert move_gen.is_in_check(empty_board, Color.WHITE) is True

    def test_is_in_check_by_knight(self, move_gen, empty_board):
        """Detect check from knight."""
        from chess.pieces import King
        white_king = King(Color.WHITE)
        black_knight = Knight(Color.BLACK)
        empty_board.set_piece(4, 0, white_king)  # e1
        empty_board.set_piece(5, 2, black_knight)  # f3 - attacking e1

        assert move_gen.is_in_check(empty_board, Color.WHITE) is True

    def test_not_in_check(self, move_gen, empty_board):
        """No check when king is safe."""
        from chess.pieces import King
        white_king = King(Color.WHITE)
        black_rook = Rook(Color.BLACK)
        empty_board.set_piece(4, 0, white_king)  # e1
        empty_board.set_piece(5, 7, black_rook)  # f8 - not attacking

        assert move_gen.is_in_check(empty_board, Color.WHITE) is False

    def test_move_blocked_when_would_leave_king_in_check(self, move_gen, empty_board, game_state):
        """Piece cannot move if it would leave king in check."""
        from chess.pieces import King

        white_king = King(Color.WHITE)
        white_rook = Rook(Color.WHITE)
        black_rook = Rook(Color.BLACK)

        empty_board.set_piece(4, 0, white_king)  # e1
        empty_board.set_piece(4, 3, white_rook)  # e4 - blocks check
        empty_board.set_piece(4, 7, black_rook)  # e8 - would give check if white rook moves

        moves = move_gen.get_legal_moves(empty_board, white_rook, game_state)

        # White rook can only move along the e-file (staying between king and attacker)
        for move in moves:
            assert move[0] == 4  # Must stay on e-file


class TestGetAllMoves:
    """Tests for getting all moves for a color."""

    def test_get_all_legal_moves_returns_pieces_with_moves(self, move_gen, empty_board, game_state):
        """get_all_legal_moves returns dict of pieces to their moves."""
        knight = Knight(Color.WHITE)
        rook = Rook(Color.WHITE)
        empty_board.set_piece(0, 0, knight)
        empty_board.set_piece(7, 7, rook)

        all_moves = move_gen.get_all_legal_moves(empty_board, Color.WHITE, game_state)

        assert knight in all_moves
        assert rook in all_moves
        assert len(all_moves[knight]) == 2  # Corner knight
        assert len(all_moves[rook]) == 14  # Open rook

    def test_get_all_legal_moves_ignores_other_color(self, move_gen, empty_board, game_state):
        """get_all_legal_moves only returns moves for specified color."""
        white_knight = Knight(Color.WHITE)
        black_knight = Knight(Color.BLACK)
        empty_board.set_piece(4, 4, white_knight)
        empty_board.set_piece(0, 0, black_knight)

        white_moves = move_gen.get_all_legal_moves(empty_board, Color.WHITE, game_state)

        assert white_knight in white_moves
        assert black_knight not in white_moves
