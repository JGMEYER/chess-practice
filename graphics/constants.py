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

# Board dimensions
SQUARE_SIZE = 80
BOARD_SIZE = 8
LABEL_MARGIN = 24  # Space for rank/file labels
MENU_BUTTON_HEIGHT = 30  # Height of menu buttons
MENU_BAR_PADDING = 10  # Padding below menu bar
MENU_BAR_HEIGHT = MENU_BUTTON_HEIGHT + MENU_BAR_PADDING  # Total menu bar area

# Sidebar dimensions
SIDEBAR_WIDTH = 200
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
