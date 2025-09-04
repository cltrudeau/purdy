# zoo.py
from purdy.content import Code
from purdy.tui.apps import app_factory, BoxSpec, RowSpec, simple, split

# =============================================================================

CONTENT = """This is some babbling text which will appear in a bunch of different colours. I'll just keep typing for a while. That should be enough I would think, yes?  """

app = split(20, relative_height_top=3, auto_scroll_bottom=True)
top = app.top
bottom = app.bottom

top.append("123")
bottom.append("abc")
top.wait()

top.append("\n456")
bottom.replace("def")
top.wait()

(bottom
    .replace("")
    .append("A")
    .pause(1)
    .append("\nB")
    .pause(1)
    .append("\nC")
    .pause(1)
    .append("\nD")
    .pause(1)
    .append("\nE")
    .pause(1)
    .wait()
)

top.append("\nfin")
bottom.append("\nished")


#(app.top
#    .append_cell(self.box1, "123\n")
#    .append_cell(self.box2, "abc\n")
#    .wait_cell()
#
#    .append_cell(self.box1, "456\n")
#    .replace_cell(self.box2, "def\n")
#    .wait_cell()
#
#    .curtain_cell(self.box1, "789\n", self.overlay, self.effect_holder)
#    .replace_cell(self.box2, "")
#    .append_cell(self.box2, "A\n")
#    .pause_cell(1)
#    .append_cell(self.box2, "B\n")
#    .pause_cell(1)
#    .append_cell(self.box2, "C\n")
#    .pause_cell(1)
#    .append_cell(self.box2, "D\n")
#    .pause_cell(1)
#    .append_cell(self.box2, "E\n")
#    .wait_cell()
#
#    .append_cell(self.box1, "fin\n")
#    .append_cell(self.box2, "ished\n")
#)
#
#app.top.content = "[blue]" + 7 * CONTENT + "[/]"
#app.bottom.content = "[red]" + 7 * CONTENT + "[/]"

app.run()
