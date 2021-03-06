"""
Pylint macro for JEdit.
"""

# Searches the script path for a directory containing the string below to
# determine if it's the root workspace directory.
WORKSPACE_SUBSTRING = "_ws"

# Pylint executable
PYLINT = "/usr/local/python/bin/pylint"
PYLINT_FLAGS = "--rcfile=/fast/my_pylint_rc"

PEP8 = "/usr/local/python/bin/pep8"
PEP8_FLAGS = " "

###############################################################################
# Jython modules

from java.awt import Color
from java.awt import Dimension
from java.awt.event import MouseListener

from javax.swing import JComponent
from javax.swing import JMenuItem
from javax.swing.event import CaretListener

from org.gjt.sp.jedit import EBComponent # EB = EditBus
from org.gjt.sp.jedit import EditBus
from org.gjt.sp.jedit import Macros
from org.gjt.sp.jedit import jEdit
from org.gjt.sp.jedit.buffer import BufferListener
from org.gjt.sp.jedit.gui import DynamicContextMenuService;
from org.gjt.sp.jedit.msg import BufferUpdate
from org.gjt.sp.jedit.textarea import TextAreaExtension
from org.gjt.sp.jedit.textarea import TextAreaPainter
from org.gjt.sp.util import Log

###############################################################################
# Python modules

import os.path
import os
import re
import shlex
import subprocess
import threading

#------------------------------------------------------------------------------
def _search_for_workspace_path(path):
	"""
	Searches the path for the root workspace path, using the regular expression
	WORKSPACE_REGEX.
	"""

	# The pattern tries to match a string surrounded with slashes: /.+_ws.*/

	pattern = "/[^/]+" + WORKSPACE_SUBSTRING + "[^/]*/"

	regex = re.compile(pattern)

	match = regex.search(path)

	if match is None:
		return None

	# -1 to remove trailing '/'
	ws_dir = path[0 : match.end() - 1]

	return ws_dir

###############################################################################
class PyLintRunner(threading.Thread):
	"""
	A thread class for running pylint on the command line.  Using a thread
	allows the Java GUI loop to continue to run while the shell is running.
	"""

	def __init__(self, pylint_marco_obj, filename):

		threading.Thread.__init__(self)

		self._pylint_macro_obj = pylint_marco_obj
		self._filename = filename

	def run(self):

		Log.log(Log.DEBUG, self, "PyLintRunner::run()")

		# Create a PYTHONPATH variable to resolve imports.

		basename = os.path.basename(self._filename)
		script_dir = os.path.dirname(self._filename)

		ws_dir = _search_for_workspace_path(self._filename)

		Log.log(Log.DEBUG, self, "ws_dir = '%s'" % ws_dir)

		python_path = ""

		if ws_dir is not None:
			python_path = "%s:%s" % (ws_dir, script_dir)

		else:
			python_path = script_dir

		env = {"PYTHONPATH" : python_path}
		Log.log(Log.DEBUG, self, "using PYTHONPATH = '%s'" % python_path)

		#----------------------------------------------------------------------
		# Running Pylint

		cmd = '%s %s "%s"' % (PYLINT, PYLINT_FLAGS, self._filename)

		Log.log(Log.DEBUG, self, "running command:\n    %s" % cmd)

		stdout, stderr = _run_command(cmd, env)

		Log.log(Log.DEBUG, self, "stdout:\n%s" % stdout)
		Log.log(Log.DEBUG, self, "stderr:\n%s" % stderr)

		if len(stderr) > 0:
			Macros.error(
				view,
				"Error running pylint\nPYTHONPATH: %s\nCOMMAND: %s\n%s" % (
					python_path,
					cmd,
					stderr))

		lines = stdout.split("\n")

		#----------------------------------------------------------------------
		# Running PEP8

		if os.path.isfile(PEP8):

			cmd = '%s %s "%s"' % (PEP8, PEP8_FLAGS, self._filename)

			Log.log(Log.DEBUG, self, "running command:\n    %s" % cmd)

			stdout, stderr = _run_command(cmd, env)

			Log.log(Log.DEBUG, self, "stdout:\n%s" % stdout)
			Log.log(Log.DEBUG, self, "stderr:\n%s" % stderr)

			if len(stderr) > 0:
				Macros.error(
					view,
					"Error running pep8\nCOMMAND: %s\n%s" % (cmd, stderr))

			lines.extend(stdout.split("\n"))

		if len(lines) == 0:
			return

		for line in lines:

			tokens = line.split(":")
			n_tokens = len(tokens)

			#------------------------------------------------------------------
			# Handle pylint error

			# Ensure this is a Pylint code.
			if tokens[0] in ["E", "W", "C", "F", "R"]:

				# Grab the line & column numbers
				row, _ = [int(x) for x in tokens[1].split(",")]

				self._pylint_macro_obj.add_pylint_error(
					row, "PyLint: " + line.strip())

			# Handle alternative PyLint messages with specific error codes
			elif tokens[0].startswith(basename):

				row = int(tokens[1])

				# Strip off the "filename:line_number:"
				n = len(tokens[0]) + len(tokens[1]) + 2

				message = line[n:].strip()

				self._pylint_macro_obj.add_pylint_error(
					row, "PyLint: " + message)

			#------------------------------------------------------------------
			# PEP8 Messages
			elif tokens[0] == self._filename and n_tokens >= 4:
				row = int(tokens[1])

				line = ":".join(tokens[3:])
				line = line.strip()

				self._pylint_macro_obj.add_pylint_error(
					row, "PEP8: " + line)


###############################################################################
class PyLintGlobalErrorBar(JComponent):
	"""
	A verticle panel left of the vertical scrollbar that indicates where errors
	are located in the file.  Just a navagational aid.
	"""

	def __init__(self, width, height):
		"""
		Creates a new compenent.
		"""

		JComponent.__init__(self)

		d = Dimension(width, height)

		self.setMinimumSize(d)
		self.setPreferredSize(d)
		self.setSize(d)

		self._line_numbers = []
		self._total_lines = 0

	def clear_state(self):
		"""
		Clears the list of line number to draw.
		"""
		self._line_numbers = []

	def add_line(self, line_number):
		"""
		Adds a line number to draw, plus sets the total number of buffer lines.
		"""
		self._line_numbers.append(line_number)

	def set_total_buffer_lines(self, n):
		"""
		Sets the number of lines in the buffer, used to locate lines on the
		component.
		"""
		self._total_lines = float(n)

	def paint(self, gfx):
		"""
		Paints red rectangles corresponding to errors in the buffer.
		"""

		if self._total_lines <= 0.0:
			return

		d = self.getSize()
		width, height = d.width, d.height

		pixels_per_line = int(height / self._total_lines + 0.5)

		if pixels_per_line == 0:
			pixels_per_line = 1

		for line_number in self._line_numbers:

			y_start = int(height * line_number / self._total_lines + 0.5)

			gfx.setColor(Color.RED)
			gfx.fillRect(0, y_start, width, pixels_per_line)

###############################################################################
class PyLintMouseListener(MouseListener):
	"""
	A mouse listener that pops up a dialog with PyLint errors when a line
	is right-clicked.
	"""

	def __init__(self, py_lint_macro):
		"""init()"""
		self._py_lint_macro = py_lint_macro

	def mousePressed(self, event):
		"""
		MouseListener callback.
		"""

		if event.isPopupTrigger():
			return

		data = \
			self._py_lint_macro.get_error_message_from_event(event)

		if data is None:
			return

		message, buffer_line_number = data

		if message is None:
			return

		self._last_line_number = buffer_line_number

		Macros.message(view, message)

###############################################################################
class PyLintMacro(
		BufferListener,
		EBComponent,
		TextAreaExtension):
	"""
	A class that paints red boxes around PyLint errors.
	"""

	#--------------------------------------------------------------------------
	def __init__(self, edit_pane):
		"""
		init()
		"""

		TextAreaExtension.__init__(self)

		self._edit_pane = edit_pane
		self._text_area = self._edit_pane.getTextArea()
		self._buffer = self._text_area.getBuffer()
		self._errors = {}
		self._buffer_is_dirty = False

		# Add self to the edit_pane
		self._painter = self._text_area.getPainter()
		self._painter.addExtension(TextAreaPainter.HIGHEST_LAYER , self)

		self._mouse_listener = PyLintMouseListener(self)
		self._painter.addMouseListener(self._mouse_listener)

		# Attach self to the buffer
		self._buffer.addBufferListener(self)

		d = self._text_area.getSize()

		self._error_bar = PyLintGlobalErrorBar(10, d.height)
		self._error_bar.set_total_buffer_lines(self._buffer.getLineCount())

		self._text_area.addLeftOfScrollBar(self._error_bar)

		# Add this class instance to the jEdit EditBus
		EditBus.addToBus(self)

	#--------------------------------------------------------------------------
	def shutdown(self):
		"""
		Detaches the listener objecst from the TextArea.
		"""

		Log.log(Log.DEBUG, PyLintMacro, "shutdown()")

		self.clear_state()

		self._buffer.removeBufferListener(self)
		self._painter.removeExtension(self)
		self._painter.removeMouseListener(self._mouse_listener)
		self._text_area.removeLeftOfScrollBar(self._error_bar)
		EditBus.removeFromBus(self)

	#--------------------------------------------------------------------------
	def add_pylint_error(self, buffer_line_number, message):
		"""
		Adds a line number with a message to the set of PyLint errors for
		display.
		"""

		if buffer_line_number not in self._errors:
			self._errors[buffer_line_number] = []

		self._errors[buffer_line_number].append(message)
		self._error_bar.add_line(buffer_line_number)

		Log.log(Log.DEBUG, self, "added line number %d" % buffer_line_number)

		n_errors = len(self._errors.keys())

		self._text_area.repaint()

		view.getStatus().setMessage(
			"PyLint: Found %d errors/warnings" % n_errors)

	#--------------------------------------------------------------------------
	def clear_state(self):
		"""
		Removes all errors, nothing will get displayed.
		"""

		Log.log(Log.DEBUG, PyLintMacro, "clear_state()")
		self._errors = {}
		self._error_bar.clear_state()

	#--------------------------------------------------------------------------
	def get_error_message_from_event(self, event):
		"""
		Gets called from the CaretListener, so we can detect when a line of
		interest gets clicked on.
		"""

		if self._buffer_is_dirty or event is None:
			return

		buffer_line_number = self._text_area.getCaretLine() + 1

		if buffer_line_number in self._errors:
			msg = ""
			for line in self._errors[buffer_line_number]:
				msg += line + "\n"

			return msg, buffer_line_number

		return None, None

	#--------------------------------------------------------------------------
	# BufferListener callbacks

	def bufferLoaded(self, buf):
		"""
		BufferListener callback.
		"""

		self.transactionComplete(buf)

	def contentInserted(self, buf, start_line, buffer_offset, n_lines, length):
		"""
		Called when text is inserted into the buffer.
		"""

		self._error_bar.clear_state()
		self._error_bar.set_total_buffer_lines(
			self._buffer.getLineCount() + n_lines)

		buffer_line_number = start_line + 1

		new_errors = {}
		for key in self._errors:
			if key > buffer_line_number:
				new_errors[key + n_lines] = self._errors[key]
			else:
				new_errors[key] = self._errors[key]

		self._errors = new_errors

		for key in self._errors:
			self._error_bar.add_line(key)

		self._error_bar.repaint()

	def contentRemoved(self, buf, start_line, buffer_offset, n_lines, length):
		"""
		Called when text is inserted into the buffer.
		"""

		self._error_bar.clear_state()
		self._error_bar.set_total_buffer_lines(
			self._buffer.getLineCount()
			- n_lines)

		buffer_line_number = start_line + 1

		new_errors = {}
		for key in self._errors:
			if key > buffer_line_number:
				new_errors[key - n_lines] = self._errors[key]
			else:
				new_errors[key] = self._errors[key]

		self._errors = new_errors

		for key in self._errors:
			self._error_bar.add_line(key)

		self._error_bar.repaint()

	def transactionComplete(self, buf):
		"""
		BufferListener callback.
		"""

		if self._buffer != buf:
			return

		# Don't do anything unless the buffer is clean.
		if buf.isDirty():
			view.getStatus().setMessage("PyLint: Buffer dirty")

		else:

			self._run_pylint(buf)

	#--------------------------------------------------------------------------
	# EditBus EBComponet callbacks
	def handleMessage(self, eb_message):
		"""
		Handles EditBus messages, used for detecting when the buffer get's
		saved.
		"""

		if not isinstance(eb_message, BufferUpdate):
			return

		if eb_message.getWhat() != BufferUpdate.SAVED:
			return

		self.transactionComplete(eb_message.getBuffer())

	#--------------------------------------------------------------------------
	# TextAreaPainter callbacks

	def paintValidLine(
			self,
			gfx,
			screen_line_number,
			buffer_line_number,
			offset_start,
			offset_end,
			y):
		"""
		TextAreaPainter callback, gets called for each line visible, for each
		buffer line number, check if there was a PyLint error, if so, draw a
		red box around it.
		"""

		if self._buffer_is_dirty:
			return

		if self._text_area.getBuffer() != self._buffer:
			return

		if buffer_line_number not in self._errors:
			return

		# Convert buffer line numbers into graphical screen locations
		p_start = self._text_area.offsetToXY(buffer_line_number - 1, 0)
		p_stop  = self._text_area.offsetToXY(buffer_line_number - 1, offset_start)

		if p_start is not None:
			x = p_start.x

		else:
			x = 0

		width = 0

		if p_stop is not None:
			width = p_stop.x - p_start.x + 1

		if width < 10:
			width = 10

		height = int(self._painter.getFontMetrics().getHeight())

		gfx.setColor(Color.RED)
		gfx.drawRoundRect(x, y - height - 1, width, height, 5, 5)

	#--------------------------------------------------------------------------
	def _run_pylint(self, buf):
		"""
		Creates a thread to run PyLint on the buffer.
		"""

		view.getStatus().setMessage(
			"PyLint: Found %d errors/warnings" % 0)

		self.clear_state()

		filename = buf.getPath()

		thread = PyLintRunner(self, filename)

		thread.start()

		self._buffer_is_dirty = False

###############################################################################
def _run_command(cmd, env = None):
	"""
	Runs a command on the shell, returning stdout, stderr.

	WARNING: This fuction does not handle redirection!  That is, no >, | in the
	command.

	Parameters:

		*cmd* : str
			The command to execute in the shell.

		*raise_exception* : bool
			If True, raises a RuntimeError if data is written to stderr,
			default is False.

	Returns:

		*stdout* : str
			Standard output from the command.

		*stderr* : str
			Standard error from the command.
	"""

	tokens = shlex.split(cmd)

	sub_p = subprocess.Popen(
		tokens,
		env = env,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE)

	stdout, stderr = sub_p.communicate()

	stdout = stdout.strip()
	stderr = stderr.strip()

	return stdout, stderr

###############################################################################
def main():
	"""
	Attaches a PyLintMacro object to a TextArea Buffer.  If one is already
	attached, remove it.
	"""

	Log.log(
		Log.DEBUG,
		PyLintRunner,
		"Running ~/.jedit/macros/pylint.py")

	# Try to read the pylint_state.txt file to determine if the
	# TextAreaExtension needs to be removed from the current buffer.

	extension_is_active = False

	views = jEdit.getViews()

	for v in views:

		edit_pane = v.getEditPane()
		text_area = edit_pane.getTextArea()
		painter = text_area.getPainter()
		active_extensions = painter.getExtensions()

		# Scan for any active PyLintRunners and remove them
		for ext in active_extensions:

			if "PyLintMacro" in ext.__class__.__name__:
				ext.shutdown()
				extension_is_active = True

	if extension_is_active:
		view.getStatus().setMessage("PyLint: disabled")

	else:
		view.getStatus().setMessage("PyLint: enabled")

		PyLintMacro(view.getEditPane())

###############################################################################
if __name__ in ('__main__','main'):
	main()
