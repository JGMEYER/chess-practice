"""Trie visualization component for opening book display."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from chess.patterns.openings import TrieNode


# Layout constants
HORIZONTAL_SPACING = 140
VERTICAL_SPACING = 60  # Increased from 50 for better spacing in focus mode
NODE_RADIUS = 18
PAN_SPEED_MULTIPLIER = 2.5  # Makes panning feel more responsive

# Color constants
NODE_COLOR = (80, 80, 80)
NODE_PATH_COLOR = (100, 160, 100)
NODE_SELECTED_COLOR = (100, 150, 200)
NODE_HOVER_COLOR = (100, 100, 120)

# Active node (current position in game)
NODE_ACTIVE_COLOR = (120, 180, 120)
NODE_ACTIVE_BORDER = (180, 255, 180)

# Faded path colors (for undone/future moves) - more muted/gray
NODE_PATH_FADED_COLOR = (65, 80, 65)
NODE_PATH_FADED_BORDER = (85, 105, 85)
EDGE_PATH_FADED_COLOR = (65, 80, 65)

NODE_PATH_BORDER = (140, 200, 140)
NODE_SELECTED_BORDER = (200, 220, 255)

EDGE_COLOR = (60, 60, 60)
EDGE_PATH_COLOR = (100, 160, 100)

TEXT_COLOR = (180, 180, 180)
TEXT_PATH_COLOR = (255, 255, 255)
TEXT_PATH_FADED_COLOR = (200, 200, 200)

# Focus mode colors (available next moves from active node)
NODE_AVAILABLE_COLOR = (200, 170, 80)
NODE_AVAILABLE_BORDER = (230, 200, 100)
EDGE_AVAILABLE_COLOR = (180, 150, 60)
TEXT_AVAILABLE_COLOR = (255, 240, 200)


@dataclass(eq=False)
class TrieLayoutNode:
    """A node in the laid-out trie with position information."""

    san: str | None  # None for root node
    trie_node: TrieNode
    x: float  # World X coordinate
    y: float  # World Y coordinate
    depth: int  # Distance from root (root = 0)
    parent: TrieLayoutNode | None
    children: list[TrieLayoutNode] = field(default_factory=list)
    path_index: int | None = None  # Index in current path (None if not on path)


@dataclass
class Viewport:
    """Manages pan and zoom for the trie visualization."""

    offset_x: float = 0.0  # Center X in world coordinates
    offset_y: float = 0.0  # Center Y in world coordinates
    zoom: float = 1.0

    MIN_ZOOM = 0.3
    MAX_ZOOM = 2.0

    def world_to_screen(
        self, wx: float, wy: float, rect: pygame.Rect
    ) -> tuple[int, int]:
        """Convert world coordinates to screen coordinates within rect."""
        # Center of rect in screen coordinates
        center_x = rect.centerx
        center_y = rect.centery

        # Apply zoom and offset
        screen_x = center_x + (wx - self.offset_x) * self.zoom
        screen_y = center_y + (wy - self.offset_y) * self.zoom

        return (int(screen_x), int(screen_y))

    def screen_to_world(
        self, sx: int, sy: int, rect: pygame.Rect
    ) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        center_x = rect.centerx
        center_y = rect.centery

        # Reverse the transform
        wx = (sx - center_x) / self.zoom + self.offset_x
        wy = (sy - center_y) / self.zoom + self.offset_y

        return (wx, wy)

    def clamp_zoom(self) -> None:
        """Ensure zoom stays within bounds."""
        self.zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom))


class TrieLayout:
    """Computes and caches the 2D layout of trie nodes."""

    def __init__(self) -> None:
        self._root: TrieLayoutNode | None = None
        self._all_nodes: list[TrieLayoutNode] = []
        self._min_x: float = 0.0
        self._max_x: float = 0.0
        self._min_y: float = 0.0
        self._max_y: float = 0.0

    @property
    def root(self) -> TrieLayoutNode | None:
        return self._root

    def get_all_nodes(self) -> list[TrieLayoutNode]:
        return self._all_nodes

    def get_bounds(self) -> tuple[float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y)."""
        return (self._min_x, self._min_y, self._max_x, self._max_y)

    def compute_layout(self, trie_root: TrieNode) -> TrieLayoutNode:
        """Compute 2D layout for the entire trie (left-to-right orientation)."""
        self._all_nodes = []

        # Phase 1: Create layout tree structure
        self._root = self._create_layout_tree(trie_root, depth=0, parent=None)

        # Phase 2: Assign Y positions using layered algorithm (siblings spread vertically)
        next_y_at_depth: dict[int, float] = {}
        self._assign_y_positions_spread(self._root, next_y_at_depth)

        # Phase 3: Center parents over children (post-order)
        self._center_parents_vertical(self._root)

        # Phase 4: Resolve any overlaps
        self._resolve_overlaps_vertical()

        # Phase 5: Assign X based on depth (horizontal traversal: left = root)
        self._assign_x_positions_by_depth(self._root)

        # Phase 6: Normalize and compute bounds
        self._normalize_positions()

        return self._root

    def _create_layout_tree(
        self, trie_node: TrieNode, depth: int, parent: TrieLayoutNode | None
    ) -> TrieLayoutNode:
        """Recursively create layout nodes from trie nodes."""
        # For root, san is None
        san = None if parent is None else self._get_san_from_parent(parent, trie_node)

        layout_node = TrieLayoutNode(
            san=san,
            trie_node=trie_node,
            x=0.0,
            y=0.0,
            depth=depth,
            parent=parent,
        )
        self._all_nodes.append(layout_node)

        # Sort children by SAN for consistent ordering
        sorted_children = sorted(trie_node.children.items(), key=lambda x: x[0])

        for child_san, child_trie_node in sorted_children:
            child_layout = self._create_layout_tree_with_san(
                child_trie_node, child_san, depth + 1, layout_node
            )
            layout_node.children.append(child_layout)

        return layout_node

    def _create_layout_tree_with_san(
        self, trie_node: TrieNode, san: str, depth: int, parent: TrieLayoutNode
    ) -> TrieLayoutNode:
        """Create layout node with known SAN."""
        layout_node = TrieLayoutNode(
            san=san,
            trie_node=trie_node,
            x=0.0,
            y=0.0,
            depth=depth,
            parent=parent,
        )
        self._all_nodes.append(layout_node)

        sorted_children = sorted(trie_node.children.items(), key=lambda x: x[0])

        for child_san, child_trie_node in sorted_children:
            child_layout = self._create_layout_tree_with_san(
                child_trie_node, child_san, depth + 1, layout_node
            )
            layout_node.children.append(child_layout)

        return layout_node

    def _get_san_from_parent(
        self, parent: TrieLayoutNode, child_trie: TrieNode
    ) -> str | None:
        """Find the SAN that leads from parent to child."""
        for san, trie_node in parent.trie_node.children.items():
            if trie_node is child_trie:
                return san
        return None

    def _assign_y_positions_spread(
        self, node: TrieLayoutNode, next_y: dict[int, float]
    ) -> None:
        """Assign initial Y positions (post-order traversal) - siblings spread vertically."""
        # First, process all children
        for child in node.children:
            self._assign_y_positions_spread(child, next_y)

        if node.children:
            # Parent: center over children (vertically)
            top_child = node.children[0]
            bottom_child = node.children[-1]
            node.y = (top_child.y + bottom_child.y) / 2
        else:
            # Leaf: use next available position at this depth
            node.y = next_y.get(node.depth, 0.0)

        # Update next available Y for this depth
        next_y[node.depth] = max(
            next_y.get(node.depth, 0.0), node.y + VERTICAL_SPACING
        )

    def _center_parents_vertical(self, node: TrieLayoutNode) -> None:
        """Center parents over their children vertically (post-order)."""
        for child in node.children:
            self._center_parents_vertical(child)

        if node.children:
            top_child = node.children[0]
            bottom_child = node.children[-1]
            node.y = (top_child.y + bottom_child.y) / 2

    def _resolve_overlaps_vertical(self) -> None:
        """Resolve any node overlaps at the same depth (vertical spacing)."""
        # Group nodes by depth
        by_depth: dict[int, list[TrieLayoutNode]] = {}
        for node in self._all_nodes:
            if node.depth not in by_depth:
                by_depth[node.depth] = []
            by_depth[node.depth].append(node)

        # For each depth, sort by y and ensure minimum spacing
        for depth in sorted(by_depth.keys()):
            nodes = sorted(by_depth[depth], key=lambda n: n.y)
            for i in range(1, len(nodes)):
                prev = nodes[i - 1]
                curr = nodes[i]
                min_y = prev.y + VERTICAL_SPACING
                if curr.y < min_y:
                    # Shift this node and its subtree
                    shift = min_y - curr.y
                    self._shift_subtree_vertical(curr, shift)

    def _shift_subtree_vertical(self, node: TrieLayoutNode, shift: float) -> None:
        """Shift a node and all its descendants vertically."""
        node.y += shift
        for child in node.children:
            self._shift_subtree_vertical(child, shift)

    def _assign_x_positions_by_depth(self, node: TrieLayoutNode) -> None:
        """Assign X positions based on depth (left-to-right orientation)."""
        node.x = node.depth * HORIZONTAL_SPACING
        for child in node.children:
            self._assign_x_positions_by_depth(child)

    def _normalize_positions(self) -> None:
        """Normalize so min_x = 0, compute bounds."""
        if not self._all_nodes:
            return

        self._min_x = min(n.x for n in self._all_nodes)
        self._max_x = max(n.x for n in self._all_nodes)
        self._min_y = min(n.y for n in self._all_nodes)
        self._max_y = max(n.y for n in self._all_nodes)

        # Shift all nodes so min_x = 0
        for node in self._all_nodes:
            node.x -= self._min_x

        # Update bounds
        self._max_x -= self._min_x
        self._min_x = 0.0


class TrieVisualization:
    """Renders the trie visualization with pan/zoom support."""

    def __init__(self, trie_root: TrieNode) -> None:
        self._layout = TrieLayout()
        self._layout.compute_layout(trie_root)
        self._viewport = Viewport()
        self._selected_node: TrieLayoutNode | None = None
        self._hovered_node: TrieLayoutNode | None = None
        self._current_path: list[TrieLayoutNode] = []
        self._current_move_count: int = 0  # Track current position for active node
        self._dragging = False
        self._drag_start: tuple[int, int] | None = None
        self._last_drag_pos: tuple[int, int] | None = None
        self._font: pygame.font.Font | None = None
        self._rect: pygame.Rect | None = None
        self._focus_mode = False
        self._focus_positions: dict[TrieLayoutNode, tuple[float, float]] = {}

        # Center on root initially
        if self._layout.root:
            self._viewport.offset_x = self._layout.root.x
            self._viewport.offset_y = self._layout.root.y

    @property
    def selected_node(self) -> TrieLayoutNode | None:
        return self._selected_node

    def select_current_position(self) -> None:
        """Select the node at the current active position."""
        if self._current_path and self._current_move_count < len(self._current_path):
            self._selected_node = self._current_path[self._current_move_count]

    def set_focus_mode(self, enabled: bool) -> None:
        """Enable/disable focus mode (show only path + available moves)."""
        self._focus_mode = enabled
        if enabled:
            self._compute_focus_layout()
        self.center_on_current_position()

    def _compute_focus_layout(self) -> None:
        """Compute compact positions for visible nodes in focus mode."""
        self._focus_positions = {}

        if not self._current_path:
            return

        # Layout path nodes in a horizontal line
        for i, node in enumerate(self._current_path):
            self._focus_positions[node] = (i * HORIZONTAL_SPACING, 0)

        # Layout available moves vertically from the active node
        active_node = self._get_active_node()
        if active_node:
            active_x = self._focus_positions.get(active_node, (0, 0))[0]
            available_moves = [
                child for child in active_node.children
                if child.path_index is None  # Not already on the path
            ]
            # Spread vertically, centered around the path (y=0)
            if available_moves:
                start_y = -(len(available_moves) - 1) * VERTICAL_SPACING / 2
                for i, child in enumerate(available_moves):
                    self._focus_positions[child] = (
                        active_x + HORIZONTAL_SPACING,
                        start_y + i * VERTICAL_SPACING,
                    )

    def _get_node_position(self, node: TrieLayoutNode) -> tuple[float, float]:
        """Get node position, using focus layout if in focus mode."""
        if self._focus_mode and node in self._focus_positions:
            return self._focus_positions[node]
        return (node.x, node.y)

    def _get_active_node(self) -> TrieLayoutNode | None:
        """Get the current active node (at current_move_count)."""
        if self._current_path and self._current_move_count < len(self._current_path):
            return self._current_path[self._current_move_count]
        return None

    def _is_visible_in_focus_mode(self, node: TrieLayoutNode) -> bool:
        """Check if node should be visible in focus mode."""
        # Always show nodes on the path
        if node.path_index is not None:
            return True
        # Show immediate children of the active node
        active_node = self._get_active_node()
        if active_node and node.parent == active_node:
            return True
        return False

    def _is_available_move(self, node: TrieLayoutNode) -> bool:
        """Check if node is an available next move (child of active, not on path)."""
        if node.path_index is not None:
            return False  # Already on path
        active_node = self._get_active_node()
        return active_node is not None and node.parent == active_node

    def update_current_path(
        self, san_history: list[str], current_move_count: int
    ) -> None:
        """
        Update which nodes are on the current game path.

        The full san_history represents all moves played (including redo-able ones).
        current_move_count indicates how many moves are "active" (not undone).

        Nodes with path_index <= current_move_count are on the active path.
        Nodes with path_index > current_move_count are on the "future" path (undone moves).
        """
        # Store current move count for active node detection
        self._current_move_count = current_move_count

        # Clear old path indices
        for node in self._layout.get_all_nodes():
            node.path_index = None

        self._current_path = []

        if self._layout.root is None:
            return

        # Start at root (always index 0)
        node = self._layout.root
        node.path_index = 0
        self._current_path.append(node)

        # Follow the FULL path (all moves in history, including redo-able ones)
        for i, san in enumerate(san_history):
            # Find child with this SAN
            child = None
            for c in node.children:
                if c.san == san:
                    child = c
                    break

            if child is None:
                break

            child.path_index = i + 1
            self._current_path.append(child)
            node = child

        # Recompute focus layout if focus mode is active
        if self._focus_mode:
            self._compute_focus_layout()

    def center_on_current_position(self) -> None:
        """Center viewport on the current active node (at current_move_count)."""
        if self._current_path and self._current_move_count < len(self._current_path):
            # Center on the active node, not the end of the path
            active_node = self._current_path[self._current_move_count]
            x, y = self._get_node_position(active_node)
            self._viewport.offset_x = x
            self._viewport.offset_y = y

    def center_on_root(self) -> None:
        """Center viewport on the root node."""
        if self._layout.root:
            x, y = self._get_node_position(self._layout.root)
            self._viewport.offset_x = x
            self._viewport.offset_y = y

    def process_event(
        self, event: pygame.event.Event, rect: pygame.Rect
    ) -> str | None:
        """
        Process mouse events for the visualization.

        Returns action string or None:
        - "trie_select" - node was selected
        - "trie_navigate:N" - navigate to move index N
        - None - no action needed
        """
        self._rect = rect

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos, rect)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            # Middle mouse button - always start panning
            return self._handle_middle_click(event.pos, rect)
        elif event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2):
            return self._handle_release()
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_motion(event.pos, rect)
        elif event.type == pygame.MOUSEWHEEL:
            return self._handle_scroll(event.y, rect)

        return None

    def update_hover(self, pos: tuple[int, int], rect: pygame.Rect) -> None:
        """Update hover state based on mouse position."""
        if not rect.collidepoint(pos):
            self._hovered_node = None
            return

        self._hovered_node = self._find_node_at_pos(pos, rect)

    def _start_pan(self, pos: tuple[int, int]) -> None:
        """Start panning from the given position."""
        self._dragging = True
        self._drag_start = pos
        self._last_drag_pos = pos

    def _handle_click(
        self, pos: tuple[int, int], rect: pygame.Rect
    ) -> str | None:
        """Handle left mouse button down."""
        if not rect.collidepoint(pos):
            return None

        clicked_node = self._find_node_at_pos(pos, rect)

        if clicked_node is None:
            # No node clicked - start panning
            self._start_pan(pos)
            return None

        if clicked_node == self._selected_node:
            # Second click on selected node
            if clicked_node.path_index is not None:
                # On current path - activate (navigate)
                return f"trie_navigate:{clicked_node.path_index}"
            # Not on path - deselect
            self._selected_node = None
            return None

        # First click - select
        self._selected_node = clicked_node
        return "trie_select"

    def _handle_middle_click(
        self, pos: tuple[int, int], rect: pygame.Rect
    ) -> str | None:
        """Handle middle mouse button - always start panning."""
        if not rect.collidepoint(pos):
            return None
        self._start_pan(pos)
        return None

    def _handle_release(self) -> str | None:
        """Handle mouse button up."""
        self._dragging = False
        self._drag_start = None
        self._last_drag_pos = None
        return None

    def _handle_motion(
        self, pos: tuple[int, int], rect: pygame.Rect
    ) -> str | None:
        """Handle mouse motion."""
        if self._dragging and self._last_drag_pos is not None:
            dx = pos[0] - self._last_drag_pos[0]
            dy = pos[1] - self._last_drag_pos[1]

            # Apply speed multiplier and scale by zoom for consistent feel
            speed = PAN_SPEED_MULTIPLIER / self._viewport.zoom
            self._viewport.offset_x -= dx * speed
            self._viewport.offset_y -= dy * speed

            self._last_drag_pos = pos

        return None

    def _handle_scroll(self, delta: int, rect: pygame.Rect) -> str | None:
        """Handle mouse wheel for zooming."""
        mouse_pos = pygame.mouse.get_pos()
        if not rect.collidepoint(mouse_pos):
            return None

        # Zoom toward mouse position
        zoom_factor = 1.1 if delta > 0 else 0.9
        old_zoom = self._viewport.zoom
        self._viewport.zoom *= zoom_factor
        self._viewport.clamp_zoom()

        # Adjust offset to zoom toward mouse position
        if self._viewport.zoom != old_zoom:
            # Get world position under mouse before zoom change
            world_x, world_y = self._viewport.screen_to_world(
                mouse_pos[0], mouse_pos[1], rect
            )
            # Recalculate with new zoom - this keeps the point under cursor stable
            # (The viewport.screen_to_world already accounts for current offset/zoom)

        return None

    def _find_node_at_pos(
        self, pos: tuple[int, int], rect: pygame.Rect
    ) -> TrieLayoutNode | None:
        """Find which node (if any) is at the given screen position."""
        for node in self._layout.get_all_nodes():
            # Skip nodes not visible in focus mode
            if self._focus_mode and not self._is_visible_in_focus_mode(node):
                continue

            node_x, node_y = self._get_node_position(node)
            screen_x, screen_y = self._viewport.world_to_screen(node_x, node_y, rect)
            radius = int(NODE_RADIUS * self._viewport.zoom)

            # Check if click is within node circle
            dx = pos[0] - screen_x
            dy = pos[1] - screen_y
            if dx * dx + dy * dy <= radius * radius:
                return node

        return None

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw the trie visualization within the given rect."""
        self._rect = rect

        # Initialize font if needed
        if self._font is None:
            self._font = pygame.font.Font(None, 16)

        # Clip to rect
        surface.set_clip(rect)

        # Draw background
        pygame.draw.rect(surface, (40, 40, 40), rect)

        # Draw edges first (so nodes appear on top)
        self._draw_edges(surface, rect)

        # Draw nodes
        self._draw_nodes(surface, rect)

        # Reset clip
        surface.set_clip(None)

    def _draw_edges(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw all edges between nodes."""
        for node in self._layout.get_all_nodes():
            if node.parent is not None:
                # Skip edges not visible in focus mode
                if self._focus_mode and not self._is_visible_in_focus_mode(node):
                    continue
                self._draw_edge(surface, node.parent, node, rect)

    def _draw_edge(
        self,
        surface: pygame.Surface,
        parent: TrieLayoutNode,
        child: TrieLayoutNode,
        rect: pygame.Rect,
    ) -> None:
        """Draw an edge from parent to child."""
        p_x, p_y = self._get_node_position(parent)
        c_x, c_y = self._get_node_position(child)
        p_sx, p_sy = self._viewport.world_to_screen(p_x, p_y, rect)
        c_sx, c_sy = self._viewport.world_to_screen(c_x, c_y, rect)

        # Check if edge is on the full path
        on_path = (
            parent.path_index is not None
            and child.path_index is not None
            and child.path_index == parent.path_index + 1
        )

        # Check if this is an available move edge (focus mode)
        is_available = self._focus_mode and self._is_available_move(child)

        if is_available:
            color = EDGE_AVAILABLE_COLOR
            width = 2
        elif on_path:
            # Check if this edge is on the active portion or future (undone) portion
            # Edge is "active" if the child is at or before current move count
            is_active = child.path_index <= self._current_move_count
            color = EDGE_PATH_COLOR if is_active else EDGE_PATH_FADED_COLOR
            width = 3
        else:
            color = EDGE_COLOR
            width = 1

        pygame.draw.line(surface, color, (p_sx, p_sy), (c_sx, c_sy), width)

    def _draw_nodes(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw all nodes."""
        # Draw non-path nodes first, then path nodes on top
        path_nodes = []
        available_nodes = []
        for node in self._layout.get_all_nodes():
            # Skip nodes not visible in focus mode
            if self._focus_mode and not self._is_visible_in_focus_mode(node):
                continue

            if node.path_index is not None:
                path_nodes.append(node)
            elif self._focus_mode and self._is_available_move(node):
                available_nodes.append(node)
            else:
                self._draw_node(surface, node, rect)

        # Draw available move nodes
        for node in available_nodes:
            self._draw_node(surface, node, rect)

        # Draw path nodes on top
        for node in path_nodes:
            self._draw_node(surface, node, rect)

        # Draw selected node last (on very top)
        if self._selected_node is not None and self._selected_node not in path_nodes:
            self._draw_node(surface, self._selected_node, rect)

    def _draw_node(
        self, surface: pygame.Surface, node: TrieLayoutNode, rect: pygame.Rect
    ) -> None:
        """Draw a single node."""
        node_x, node_y = self._get_node_position(node)
        screen_x, screen_y = self._viewport.world_to_screen(node_x, node_y, rect)
        radius = int(NODE_RADIUS * self._viewport.zoom)

        # Skip if completely outside rect (with margin for radius)
        if (
            screen_x + radius < rect.left
            or screen_x - radius > rect.right
            or screen_y + radius < rect.top
            or screen_y - radius > rect.bottom
        ):
            return

        # Determine node states
        is_selected = node == self._selected_node
        is_hovered = node == self._hovered_node
        is_on_path = node.path_index is not None
        is_active_node = is_on_path and node.path_index == self._current_move_count
        # Node is on "active" portion of path if index <= current move count
        is_on_active_path = is_on_path and node.path_index <= self._current_move_count
        # Node is on "future" portion of path (undone moves)
        is_on_future_path = is_on_path and node.path_index > self._current_move_count
        # Check if this is an available move (focus mode)
        is_available_move = self._focus_mode and self._is_available_move(node)

        # Base styling: path status determines base appearance (always visible)
        if is_available_move:
            # Available next move in focus mode - gold
            fill_color = NODE_AVAILABLE_COLOR
            border_color = NODE_AVAILABLE_BORDER
            border_width = 2
        elif is_active_node:
            # Active node (current position) - brightest green
            fill_color = NODE_ACTIVE_COLOR
            border_color = NODE_ACTIVE_BORDER
            border_width = 3
        elif is_on_future_path:
            # Future path (undone moves) - faded green
            fill_color = NODE_PATH_FADED_COLOR
            border_color = NODE_PATH_FADED_BORDER
            border_width = 2
        elif is_on_active_path:
            # On active path but not the current node
            fill_color = NODE_PATH_COLOR
            border_color = NODE_PATH_BORDER
            border_width = 2
        elif is_hovered:
            fill_color = NODE_HOVER_COLOR
            border_color = None
            border_width = 0
        else:
            fill_color = NODE_COLOR
            border_color = None
            border_width = 0

        # Draw node circle
        pygame.draw.circle(surface, fill_color, (screen_x, screen_y), radius)
        if border_color:
            pygame.draw.circle(
                surface, border_color, (screen_x, screen_y), radius, border_width
            )

        # Selection indicator: draw an outer ring (additive to path styling)
        if is_selected:
            selection_radius = radius + 4
            pygame.draw.circle(
                surface, NODE_SELECTED_BORDER, (screen_x, screen_y), selection_radius, 3
            )

        # Draw SAN label (if not root and zoom is sufficient)
        if node.san and self._viewport.zoom >= 0.5:
            if is_available_move:
                text_color = TEXT_AVAILABLE_COLOR
            elif is_on_future_path:
                text_color = TEXT_PATH_FADED_COLOR
            elif is_on_path:
                text_color = TEXT_PATH_COLOR
            else:
                text_color = TEXT_COLOR
            self._draw_text_centered(
                surface, node.san, screen_x, screen_y, text_color
            )

    def _draw_text_centered(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw text centered at the given position."""
        if self._font is None:
            return

        text_surface = self._font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
