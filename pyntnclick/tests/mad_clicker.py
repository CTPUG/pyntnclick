from pyntnclick.tests.game_logic_utils import GameLogicTestCase


class MadClickerTestCase(GameLogicTestCase):
    "Provide a 'mad clicker' test to expose potential undefined behaviour"

    def check_result_obj(self, obj):
        """Check that the obj is the sort of result obj/seq we expect"""
        if obj is None:
            return True
        if hasattr(obj, 'process'):
            return True
        return False

    def check_result(self, obj):
        """Check that the obj is the sort of result obj/seq we expect"""
        # We do it this way, because we don't allow seqs to contain seqs
        if not self.check_result_obj(obj):
            for subobj in obj:
                if not self.check_result_obj(subobj):
                    return False
        return True

    def _format_item(self, item):
        return "%s (%s)" % (item.name, item)

    def _format_thing(self, thing):
        if not hasattr(thing, 'current_interact'):
            return self._format_item(thing)
        interact_name = None
        if thing.current_interact and thing.interacts:
            for name in thing.interacts:
                if thing.interacts[name] == thing.current_interact:
                    interact_name = name
                    break
        if interact_name:
            return "%s:%s (%s %s)" % (thing.name, interact_name,
                    thing, thing.current_interact)
        elif thing.current_interact:
            return "%s:<no name found> (%s %s)" % (thing.name, thing,
                    thing.current_interact)
        else:
            return "%s:<no interact> (%s %s)" % (thing.name, thing)

    def format_error(self, thing, item, exception):
        if not item:
            msg = ("Unexpected result for interact with no item for %s"
                    % self._format_thing(thing))
        else:
            msg = ("Unexpected result for interact with item %s with %s" %
                    (self._format_item(item), self._format_thing(thing)))
        if exception:
            return "Exception raised %s:\nTest failed: %s" % (exception, msg)
        return msg

    def do_thing(self, thing, item):
        try:
            if item:
                # We're interacting with an item in the inventory
                self.state.add_inventory_item(item.name)
            self.assertEqual(self.check_result(thing.interact(item)), True,
                self.format_error(thing, item, None))
        except self.failureException:
            raise
        except Exception, details:
            raise self.failureException(self.format_error(thing, item,
                details))
        self.clear_inventory()
        self.clear_event_queue()

    def do_item(self, item, item2):
        try:
            self.state.add_inventory_item(item.name)
            if item2:
                self.state.add_inventory_item(item2.name)
            self.assertEqual(self.check_result(item.interact(item2)), True,
                self.format_error(item, item2, None))
        except self.failureException:
            raise
        except Exception, details:
            raise self.failureException(self.format_error(item, item2,
                details))
        self.clear_inventory()
        self.clear_event_queue()

    def do_mad_clicker(self):
        """Implement frantic clicking behaviour"""
        for scene in self.state.scenes.values():
            self.state.data.set_current_scene(scene.name)
            for thing in scene.things.values():
                for interact_name in thing.interacts:
                    thing._set_interact(interact_name)
                    self.do_thing(thing, None)
                    for item in self.state.items.values():
                        self.do_thing(thing, item)
        for detail in self.state.detail_views.values():
            for thing in detail.things.values():
                for interact_name in thing.interacts:
                    thing._set_interact(interact_name)
                    self.do_thing(thing, None)
                    for item in self.state.items.values():
                        self.do_thing(thing, item)
        for item in self.state.items.values():
            self.do_item(item, None)
            for item2 in self.state.items.values():
                self.do_item(item, item2)
