# Board colors (matching chess.com style)
LIGHT_SQUARE = (240, 217, 181)  # #F0D9B5 - tan
DARK_SQUARE = (181, 136, 99)  # #B58863 - brown
BACKGROUND = (48, 46, 43)  # #302E2B - dark gray
HIGHLIGHT = (205, 210, 106)  # #CDD26A - yellow (for future use)
LABEL_COLOR = (134, 133, 126)  # #86857E - gray

# Selection colors
SELECTED_SQUARE = (244, 246, 128)  # Bright yellow for selected piece
VALID_MOVE_DOT = (128, 128, 128, 128)  # Semi-transparent gray dot

# Board dimensions
SQUARE_SIZE = 80
BOARD_SIZE = 8
LABEL_MARGIN = 24  # Space for rank/file labels

# Calculated dimensions
BOARD_PIXEL_SIZE = SQUARE_SIZE * BOARD_SIZE  # 640px
WINDOW_SIZE = BOARD_PIXEL_SIZE + LABEL_MARGIN  # 664px

# Board position (offset from window origin)
BOARD_OFFSET_X = LABEL_MARGIN
BOARD_OFFSET_Y = 0
