import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2, Gdk
import markdown
import markdown_checklist


class gtkNote(Gtk.Window):
    def __init__(self):
        super().__init__(title="gtk-Noto")
        self.set_default_size(800, 600)

        # Main layout container (split pane)
        self.paned = Gtk.Paned()
        self.add(self.paned)

        # Left pane: Editor
        self.editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.paned.add1(self.editor_box)

        # Toolbar with buttons
        toolbar = Gtk.Box(spacing=5)
        self.editor_box.pack_start(toolbar, False, False, 0)

        # Button state defaults
        self.is_checkbox_active = False
        self.is_unordered_active = False
        self.is_ordered_active = False
        self.current_ordered_count = 1

        # Buttons to insert Markdown syntax
        btn_checkbox = Gtk.Button(label="Checkbox")
        btn_checkbox.connect("clicked", self.toggle_checkbox)
        toolbar.pack_start(btn_checkbox, False, False, 0)

        btn_unordered = Gtk.Button(label="Unordered List")
        btn_unordered.connect("clicked", self.toggle_unordered)
        toolbar.pack_start(btn_unordered, False, False, 0)

        btn_ordered = Gtk.Button(label="Ordered List")
        btn_ordered.connect("clicked", self.toggle_ordered)
        toolbar.pack_start(btn_ordered, False, False, 0)

        # Text editor area
        self.text_buffer = Gtk.TextBuffer()
        self.text_editor = Gtk.TextView(buffer=self.text_buffer)
        self.text_editor.set_wrap_mode(Gtk.WrapMode.WORD)

        # Connecting key presses event for Enter key
        self.text_editor.connect("key-press-event", self.on_key_press)

        scrolled_editor = Gtk.ScrolledWindow()
        scrolled_editor.add(self.text_editor)
        self.editor_box.pack_start(scrolled_editor, True, True, 0)

        # Render button
        btn_render = Gtk.Button(label="Render Markdown")
        btn_render.connect("clicked", self.render_markdown)
        self.editor_box.pack_start(btn_render, False, False, 0)

        # Right pane: web view
        self.webview = WebKit2.WebView()

        # Enable JavaScript in WebView settings
        settings = self.webview.get_settings()
        settings.set_enable_javascript(True)  # Enable JavaScript for interactivity

        scrolled_preview = Gtk.ScrolledWindow()
        scrolled_preview.add(self.webview)

        self.paned.add2(scrolled_preview)

        self.show_all()

    def toggle_checkbox(self, widget):
        self.is_checkbox_active = not self.is_checkbox_active

    def toggle_unordered(self, widget):
        self.is_unordered_active = not self.is_unordered_active

    def toggle_ordered(self, widget):
        self.is_ordered_active = not self.is_ordered_active

    def on_key_press(self, widget, event):
        keyval = event.keyval

        if keyval == Gdk.KEY_Return:  # Enter key pressed
            cursor_mark = self.text_buffer.get_insert()
            cursor = self.text_buffer.get_iter_at_mark(cursor_mark)

            # Get the current line's text
            start_iter = cursor.copy()
            start_iter.set_line_offset(0)  # Move to the start of the current line
            end_iter = cursor.copy()
            end_iter.forward_to_line_end()  # Move to the end of the current line
            current_line = self.text_buffer.get_text(start_iter, end_iter, False)

            # Insert appropriate Markdown syntax based on active button
            if self.is_unordered_active:
                if current_line.strip().startswith("- "):
                    self.text_buffer.insert_at_cursor("\n- ")
                else:
                    self.text_buffer.insert_at_cursor("- ")
                return True

            elif self.is_ordered_active:
                if current_line.strip().startswith(f"{self.current_ordered_count}. "):
                    self.current_ordered_count += 1
                    self.text_buffer.insert_at_cursor(f"\n{self.current_ordered_count}. ")
                else:
                    self.text_buffer.insert_at_cursor(f"{self.current_ordered_count}. ")
                return True

            elif self.is_checkbox_active:
                if current_line.strip().startswith("- [ ]"):
                    self.text_buffer.insert_at_cursor("\n- [ ] ")
                else:
                    self.text_buffer.insert_at_cursor("- [ ] ")
                return True

    def render_markdown(self, widget):
        # Get Markdown text
        start = self.text_buffer.get_start_iter()
        end = self.text_buffer.get_end_iter()
        md_text = self.text_buffer.get_text(start, end, False)

        # Preprocess Markdown content to ensure proper formatting
        md_text = self.preprocess_markdown(md_text)

        # Convert to HTML using markdown-checklist extension
        html_output = markdown.markdown(
            md_text,
            extensions=['markdown_checklist.extension']
        )

        # Include JavaScript for interactive checkboxes and strikethrough logic
        checklist_js = """
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
        $(document).ready(function() {
            $('input[type="checkbox"]').on('change', function() {
                const isChecked = $(this).prop('checked');
                const parentLi = $(this).closest('li');
                if (isChecked) {
                    parentLi.css('text-decoration', 'line-through');
                } else {
                    parentLi.css('text-decoration', 'none');
                }
            });
        });
        </script>
        """

        full_html = f"""
        <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                {html_output}
                {checklist_js}
            </body>
        </html>
        """

        # Display in WebView
        self.webview.load_html(full_html, "file:///")

    def preprocess_markdown(self, md_text):
        """
        Preprocess Markdown content to ensure proper formatting.
        """
        lines = md_text.split("\n")
        processed_lines = []

        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("-") or stripped_line.startswith("*"):
                # Ensure proper indentation for unordered lists
                processed_lines.append(stripped_line)
            elif stripped_line.startswith("[x]") or stripped_line.startswith("[ ]"):
                # Ensure proper indentation for checklist items
                processed_lines.append(f"- {stripped_line}")
            elif stripped_line.endswith("."):
                # Ensure proper formatting for ordered lists
                processed_lines.append(stripped_line)
            else:
                processed_lines.append(line)

        return "\n".join(processed_lines)


if __name__ == "__main__":
    win = gtkNote()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()