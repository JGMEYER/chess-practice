# Board colors (matching chess.com style)
LIGHT_SQUARE = (240, 217, 181)  # #F0D9B5 - tan
DARK_SQUARE = (181, 136, 99)  # #B58863 - brown
BACKGROUND = (48, 46, 43)  # #302E2B - dark gray
SIDEBAR_BACKGROUND = (60, 58, 55)  # #3C3A37 - lighter gray for sidebar
MENU_BAR_BORDER = (74, 72, 69)  # #4A4845 - subtle border below menu bar
HIGHLIGHT = (205, 210, 106)  # #CDD26A - yellow (for future use)
LABEL_COLOR = (134, 133, 126)  # #86857E - gray

# Selection colors
SELECTED_SQUARE = (244, 246, 128)  # Bright yellow for selected piece
VALID_MOVE_DOT = (128, 128, 128, 128)  # Semi-transparent gray dot

# Last move highlight colors (muted blue-green tint on light/dark squares)
LAST_MOVE_LIGHT = (205, 210, 184)  # Light square with subtle blue-green tint
LAST_MOVE_DARK = (148, 157, 132)  # Dark square with subtle blue-green tint

# Check highlight colors (orange/amber tint for king in check, not checkmate)
CHECK_LIGHT = (240, 200, 150)  # Light square with amber tint
CHECK_DARK = (210, 160, 100)  # Dark square with amber tint

# Checkmate highlight colors (red tint for defeated king)
CHECKMATE_LIGHT = (235, 160, 140)  # Light square with red tint
CHECKMATE_DARK = (200, 120, 100)  # Dark square with red tint

# Board dimensions
SQUARE_SIZE = 80
BOARD_SIZE = 8
LABEL_MARGIN = 24  # Space for rank/file labels
MENU_BUTTON_HEIGHT = 30  # Height of menu buttons
MENU_BAR_PADDING = 10  # Padding below menu bar
MENU_BAR_HEIGHT = MENU_BUTTON_HEIGHT + MENU_BAR_PADDING  # Total menu bar area

# Sidebar dimensions
SIDEBAR_WIDTH = 216
CONTROL_BUTTON_SIZE = 40
CONTROL_ICON_SIZE = 32  # Smaller than button to show button background/hover states
CONTROL_BUTTON_SPACING = 10

# Calculated dimensions
BOARD_PIXEL_SIZE = SQUARE_SIZE * BOARD_SIZE  # 640px
WINDOW_WIDTH = BOARD_PIXEL_SIZE + LABEL_MARGIN + SIDEBAR_WIDTH  # 864px
WINDOW_HEIGHT = BOARD_PIXEL_SIZE + LABEL_MARGIN + MENU_BAR_HEIGHT  # 694px
WINDOW_SIZE = BOARD_PIXEL_SIZE + LABEL_MARGIN  # 664px (deprecated, kept for compatibility)

# Board position (offset from window origin)
BOARD_OFFSET_X = LABEL_MARGIN
BOARD_OFFSET_Y = MENU_BAR_HEIGHT

# Sidebar position
SIDEBAR_X = BOARD_PIXEL_SIZE + LABEL_MARGIN  # 664px
SIDEBAR_Y = MENU_BAR_HEIGHT  # 30px

# Captured pieces display
CAPTURED_PIECE_SIZE = 24
CAPTURED_ROW_SPACING = 30  # Vertical space between rows
SIDEBAR_BOTTOM = SIDEBAR_Y + BOARD_PIXEL_SIZE  # Bottom of sidebar
CAPTURED_ROW_Y_BOTTOM = SIDEBAR_BOTTOM - 10 - CAPTURED_PIECE_SIZE  # Bottom row
CAPTURED_ROW_Y_TOP = CAPTURED_ROW_Y_BOTTOM - CAPTURED_ROW_SPACING  # Top row
CAPTURED_ROW_X = SIDEBAR_X + 10
CAPTURED_GROUP_GAP = 7  # Base separation between different piece types

# Opening name display
OPENING_NAME_Y = SIDEBAR_Y + 55  # Below control buttons
OPENING_NAME_X = SIDEBAR_X + 10  # Left margin in sidebar
OPENING_NAME_MAX_WIDTH = SIDEBAR_WIDTH - 20  # 10px margin on each side

# Move list display
MOVE_LIST_TOP_Y = SIDEBAR_Y + 70  # Below opening name
MOVE_LIST_BOTTOM_Y = CAPTURED_ROW_Y_TOP - 15  # Above captured pieces with padding
MOVE_LIST_HEIGHT = MOVE_LIST_BOTTOM_Y - MOVE_LIST_TOP_Y
MOVE_LIST_LINE_HEIGHT = 18
MOVE_NUMBER_WIDTH = 28
MOVE_COLUMN_WIDTH = 48
