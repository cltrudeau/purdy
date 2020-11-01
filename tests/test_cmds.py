import importlib, sys
from importlib.machinery import SourceFileLoader

from pathlib import Path
from unittest import TestCase

from waelstow import capture_stdout

from purdy.colour import COLOURIZERS

RTFColourizer = COLOURIZERS['rtf']

# =============================================================================

PAT_EXPECTED ="""\
[38;5;241m 10[0m [38;5;18m[48;5;237m>>> [0m[38;5;62m[1m[48;5;237m@decorated[0m
[38;5;241m 11[0m [38;5;18m[48;5;237m... [0m[38;5;3m[48;5;237mdef[0m[48;5;237m [0m[38;5;7m[48;5;237mthing[0m[48;5;237m([0m[38;5;7m[48;5;237ma[0m[48;5;237m,[0m[48;5;237m [0m[38;5;7m[48;5;237mb[0m[48;5;237m,[0m[48;5;237m [0m[38;5;7m[48;5;237mc[0m[48;5;237m)[0m[48;5;237m:[0m
[38;5;241m 12[0m [38;5;18m... [0m    [0m[38;5;3mpass[0m
"""

# Careful with this string, there are necessary trailing blanks on some lines!
PRAT_EXPECTED = """{\\rtf1\\ansi\\ansicpg1252
{\\fonttbl\\f0\\fnil\\fcharset0 RobotoMono-Regular;}

{\\colortbl;\\red255\\green255\\blue255;\\red143\\green89\\blue2;\\red32\\green72\\blue167;\\red206\\green92\\blue0;
\\red0\\green0\\blue0;\\red52\\green101\\blue164;\\red204\\green0\\blue0;\\red92\\green53\\blue204;\\red78\\green154\\blue6;
\\red0\\green0\\blue207;\\red239\\green41\\blue41;\\red164\\green0\\blue0;
\\red213\\green213\\blue213;\\red204\\green170\\blue34;}
\\f0\\fs28
\\cb14 
\\cf5  10 
\\cb13 \\cf2 >>> 
 \\cb14\\cb13 \\b \\cf8 @decorated
\\b0
 \\cb14\\
\\cf5  11 
\\cb13 \\cf2 ... 
 \\cb14\\cb13 \\b \\cf3 def
\\b0
 \\cb14\\cb13 \\cf0  
 \\cb14\\cb13 \\cf5 thing
 \\cb14\\cb13 \\b \\cf5 (
\\b0
 \\cb14\\cb13 \\cf5 a
 \\cb14\\cb13 \\b \\cf5 ,
\\b0
 \\cb14\\cb13 \\cf0  
 \\cb14\\cb13 \\cf5 b
 \\cb14\\cb13 \\b \\cf5 ,
\\b0
 \\cb14\\cb13 \\cf0  
 \\cb14\\cb13 \\cf5 c
 \\cb14\\cb13 \\b \\cf5 )
\\b0
 \\cb14\\cb13 \\b \\cf5 :
\\b0
 \\cb14\\
\\cf5  12 
\\cf2 ... 
\\cf0     
\\b \\cf3 pass
\\b0
\\
}
"""

# =============================================================================

def load_command(mod_name):
    test_file = Path(__file__).resolve()
    scripts = test_file.parent.parent / 'bin'
    scripts = scripts.resolve()
    filename = str(scripts / mod_name)

    # Load the file as if it were a module
    loader = SourceFileLoader(mod_name, filename)
    spec = importlib.util.spec_from_loader(mod_name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)

    return module

# =============================================================================

class TestCommands(TestCase):
    def test_pat(self):
        display_code = Path(__file__).parent / \
            '../extras/display_code/decorator.repl'
        display_code = str(display_code.resolve())
        sys.argv = ['pat', '--num', '10', '--highlight', '1-2', display_code]

        pat = load_command('pat')

        with capture_stdout() as captured:
            pat.main()

            # Get the output content and remove the ESC characters
            content = captured.getvalue()
            content = content.replace('\x1b', '')

        self.assertEqual(PAT_EXPECTED, content)

    def test_prat(self):
        RTFColourizer.reset_background_colour()

        display_code = Path(__file__).parent / \
            '../extras/display_code/decorator.repl'
        display_code = str(display_code.resolve())
        sys.argv = ['prat', '--num', '10', '--highlight', '1-2', 
            '--background', 'ccaa22', display_code]

        prat = load_command('prat')

        with capture_stdout() as captured:
            prat.main()

            # Get the output content and remove the ESC characters
            content = captured.getvalue()

        self.assertEqual(PRAT_EXPECTED, content)
