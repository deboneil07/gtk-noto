import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2

import markdown

class gtkNote(Gtk.Window):
    def __init__(self):
        super().__init__(title="gtk-Noto")
        self.set_default_size(800,600)

        #main layout container (split pane)
        self.paned = Gtk.Paned()
        self.add(self.paned)

        #left pane: Editor
        self.editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.paned.add1(self.editor_box)

        #toolbar with buttons
        toolbar = Gtk.Box(spacing=5)
        self.editor_box.pack_start(toolbar, False, False, 0)

        #buttons to insert markdown syntax
        btn_checkbox = Gtk.Button(label="Checkbox")
        btn_checkbox.connect("clicked", self.insert_text, "- [] ")
        toolbar.pack_start(btn_checkbox, False, False, 0)

        btn_unordered = Gtk.Button(label="Unordered List")
        btn_unordered.connect("clicked", self.insert_text, "- ")
        toolbar.pack_start(btn_unordered, False, False, 0)

        btn_ordered = Gtk.Button(label="Ordered list")
        btn_ordered.connect("clicked", self.insert_text, "1. ")
        toolbar.pack_start(btn_ordered, False, False, 0)

        #text editor area
        self.text_buffer = Gtk.TextBuffer()
        self.text_editor = Gtk.TextView(buffer=self.text_buffer)
        self.text_editor.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_editor = Gtk.ScrolledWindow()
        scrolled_editor.add(self.text_editor)
        self.editor_box.pack_start(scrolled_editor, True, True, 0)

        #render button
        btn_render = Gtk.Button(label="Render Markdown")
        btn_render.connect("clicked", self.render_markdown)
        self.editor_box.pack_start(btn_render, False, False, 0)

        #right pane, web view
        self.webview = WebKit2.WebView()
        scrolled_preview = Gtk.ScrolledWindow()
        scrolled_preview.add(self.webview)
        self.paned.add2(scrolled_preview)

        self.show_all()

    def insert_text(self, widget, text):
            #inserting markdown syntax at cursor position

            cursor = self.text_buffer.get_insert()
            self.text_buffer.insert_at_cursor(text)

    def render_markdown(self, widget):
        #get md text
        start = self.text_buffer.get_start_iter()
        end = self.text_buffer.get_end_iter()
        md_text = self.text_buffer.get_text(start, end, False)

        #conversion to html
        html_output = markdown.markdown(md_text)
        full_html = f"""
        <html>
            <head><meta charset="utf-8"></head>
            <body>{html_output}</body>
        </html>
        """

        #display in webview
        self.webview.load_html(full_html, "file:///")

if __name__ == "__main__":
    win = gtkNote()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()












