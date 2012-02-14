# Misc utils I don't know where else to put


def list_scenes(get_initial_state):
    """List the scenes in the state"""
    state = get_initial_state()
    print 'Available scenes are : '
    for scene in state.scenes:
        print '    ', scene
    print 'Available details are : '
    for detail in state.detail_views:
        print '    ', detail


def draw_rect_image(surface, color, rect, thickness):
    """Draw a rectangle with lines thickness wide"""
    # top
    surface.fill(color, (rect.left, rect.top, rect.width, thickness))
    # bottom
    surface.fill(color, (rect.left, rect.bottom - thickness, rect.width,
        thickness))
    # left
    surface.fill(color, (rect.left, rect.top, thickness, rect.height))
    # right
    surface.fill(color, (rect.right - thickness, rect.top, thickness,
        rect.height))
