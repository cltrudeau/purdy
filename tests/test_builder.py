import inspect
from unittest import TestCase

from purdy.builder import ActionsBuilder
from purdy import actions

class TestBuilderCoverage(TestCase):
    def test_builder_coverage(self):
        ### Checks the ActionsBuilder has a method for each of the actions in
        # the actions module

        # Introspection finds imports as well as classes, the following lists
        # are used to cull the imports from the result
        ignore_functions = ['init', 'iter', 'createcode', 'addaction',
            'switchtocodebox', 'new', 'subclasshook']
        ignore_actions = ['code', 'codepart', 'typewriterstep',
            'typewriterbase', 'codeline', 'pause']

        # create a list of the named actions by introspecting the actions
        # module, removing anything in the ignore list
        action_names = set([name.lower() for name, _ in \
            inspect.getmembers(actions, inspect.isclass)])
        action_names.difference_update(set(ignore_actions))

        # build a list of the functions in the ActionsBuilder, removing
        # anything in the ignore list
        function_names = set([name.replace('_', '') for name, _ in \
            inspect.getmembers(ActionsBuilder, inspect.isfunction)])
        function_names.difference_update(set(ignore_functions))

        self.assertEqual(action_names, function_names)
