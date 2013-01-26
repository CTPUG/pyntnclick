# Misc utils I don't know where else to put


def list_scenes(scene_module, scene_list):
    """List the scenes in the state"""
    print "Available scenes and details:"
    for scene in scene_list:
        scenemod = __import__('%s.%s' % (scene_module, scene),
                         fromlist=[scene])
        if scenemod.SCENES:
            print " * %s" % scene
        else:
            print " * %s (details only)" % scene
        for detailcls in getattr(scenemod, 'DETAIL_VIEWS', []):
            print "   - %s" % detailcls.NAME


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
