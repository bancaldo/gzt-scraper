import wx


OK = wx.OK | wx.ICON_EXCLAMATION
ACV = wx.ALIGN_CENTER_VERTICAL
YN = wx.YES_NO | wx.ICON_WARNING


class ViewPlayer(wx.Frame):
    def __init__(self, parent, title, is_editor=False):
        self.parent = parent
        self.title = title
        self.is_editor = is_editor
        super(ViewPlayer, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        self.panel = PanelPlayer(parent=self)
        self.panel.btn_delete.Disable()
        self.SetSize((350, 250))
        # bindings
        self.Bind(wx.EVT_CLOSE, self.parent.quit_child)
        self.Bind(wx.EVT_BUTTON, self.parent.quit_child, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.panel.btn_save)
        self.Bind(wx.EVT_BUTTON, self.delete_player, self.panel.btn_delete)

    # noinspection PyUnusedLocal
    def on_save(self, event):
        if self.is_editor:
            self.update_player(event)
        else:
            self.new_player(event)

    # noinspection PyUnusedLocal
    def new_player(self, event):
        code = self.panel.code.GetValue()
        name = self.panel.name.GetValue()
        if not code:
            self.show_message("WARNING: You have to fill 'code' field")
        elif not name:
            self.show_message("WARNING: You have to fill 'name' field")
        else:
            fullname = self.panel.fullname.GetValue()
            self.controller.new_player(code, name, fullname)
            self.clear_text_controls()

    # noinspection PyUnusedLocal
    def delete_player(self, event):
        choice = wx.MessageBox('Deleting player...are you sure?', 'warning', YN)
        if choice == wx.YES:
            code = self.panel.code.GetValue()
            self.controller.delete_player(code)
            players = self.controller.get_players()
            self.clear_text_controls()
        else:
            choice.Destroy()

    def clear_text_controls(self):
        for w in [w for w in self.panel.GetChildren()
                  if isinstance(w, wx.TextCtrl)]:
            w.SetValue('')

    # noinspection PyUnusedLocal
    def update_player(self, event):
        code = self.panel.code.GetValue()
        name = self.panel.name.GetValue()
        fullname = self.panel.fullname.GetValue()
        if code and name:
            player = self.controller.update_player(code, name, fullname)
            self.clear_text_controls()
            self.show_message("INFO: player %s updated" % code)
        else:
            self.show_message("ERROR: Missing fields, please fill them")
        self.Destroy()

    @staticmethod
    def show_message(string):
        wx.MessageBox(string, 'core info', OK)


class PanelPlayer(wx.Panel):
    def __init__(self, parent):
        super(PanelPlayer, self).__init__(parent)
        # Attributes
        self.code = wx.TextCtrl(self)
        self.name = wx.TextCtrl(self)
        self.fullname = wx.TextCtrl(self)
        # Layout
        text_sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=5, vgap=5)
        text_sizer.Add(wx.StaticText(self, label="Player Code:"), 0, ACV)
        text_sizer.Add(self.code, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Player Name:"), 0, ACV)
        text_sizer.Add(self.name, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Player full name:"), 0, ACV)
        text_sizer.Add(self.fullname, 0, wx.EXPAND)
        text_sizer.AddGrowableCol(1)

        button_sizer = wx.FlexGridSizer(rows=1, cols=3, hgap=5, vgap=5)
        self.btn_save = wx.Button(self, wx.ID_SAVE)
        self.btn_delete = wx.Button(self, wx.ID_DELETE)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_quit.SetDefault()
        button_sizer.Add(self.btn_save, 0, ACV)
        button_sizer.Add(self.btn_delete, 0, ACV)
        button_sizer.Add(self.btn_quit, 0, ACV)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_sizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetBackgroundColour('LightGray')
        self.SetSizer(sizer)
