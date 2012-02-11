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
