import wx
import sys
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from player import ViewPlayer


OK = wx.OK | wx.ICON_EXCLAMATION
ACV = wx.ALIGN_CENTER_VERTICAL
STYLE = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | \
    wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class Core(wx.Frame):
    def __init__(self, parent, controller, title):
        super(Core, self).__init__(parent=parent, title=title)
        self.parent = parent
        self.controller = controller
        self.sub_view = None
        self.panel = Panel(self)
        self.panel.SetBackgroundColour('LightGray')
        # Menues
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        # Player menu
        menu_player = wx.Menu()
        self.menubar.Append(menu_player, "Players")
        self.menu_new_player = menu_player.Append(-1, "New Player",
                                                  "New Player")
        menu_player.AppendSeparator()
        self.menu_players_import = menu_player.Append(-1, "import Players",
                                                      "import Players")
        menu_player.AppendSeparator()
        self.menu_evaluations = menu_player.Append(-1, "extract evaluations",
                                                   "extract evaluations")
        # Bindings
        # player bindings
        self.Bind(wx.EVT_MENU, self.new_player, self.menu_new_player)
        self.Bind(wx.EVT_MENU, self.on_import, self.menu_players_import)
        self.Bind(wx.EVT_MENU, self.on_extract, self.menu_evaluations)
        self.Bind(wx.EVT_BUTTON, self.quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list,
                  self.panel.players)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_list_column,
                  self.panel.players)  # Players initialization
        players = self.controller.get_players()
        if players:
            self.fill_players(players)
            self.panel.status.SetLabel('Players on database: %s' % len(players))
        else:
            self.panel.status.SetLabel('No Players on database')

        size = (450, 500)
        self.SetSize(size)
        self.Show()

    # noinspection PyUnusedLocal
    def quit(self, event):
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_extract(self, event):
        view_extract = ViewExtract(parent=self, title="extract evaluations")

    # noinspection PyUnusedLocal
    def on_import(self, event):
        choice = wx.MessageBox('Deleting All Players?', 'warning',
                               wx.YES_NO | wx.ICON_WARNING)
        if choice == wx.YES:
            self.controller.delete_all_players()
            self.controller.import_players()
            wx.MessageBox('Players successfully imported!', '', OK)
            players = self.controller.get_players()
            self.fill_players(players)

    def set_progress(self, count):
        self.panel.status.set_progress(count)
        self.panel.status.SetLabel('elaborating %s' % count)
        wx.MicroSleep(5)

    def set_range(self, max_limit):
        self.panel.status.set_range(max_limit)

    # noinspection PyUnusedLocal
    def edit_player(self, event):
        self.Disable()
        ViewPlayer(parent=self, title='Edit Player', is_editor=True)

    # noinspection PyUnusedLocal
    def new_player(self, event):
        self.Disable()
        ViewPlayer(parent=self, title='New Player')

# noinspection PyUnusedLocal
    def on_quit(self, event):
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        self.panel.players.DeleteAllItems()
        players = self.controller.get_players()
        self.fill_players(players)

    # noinspection PyUnusedLocal
    def on_list(self, event):
        item_id = event.m_itemIndex
        player_code = self.panel.players.GetItemText(item_id)
        player = self.controller.get_player_by_code(player_code)
        self.controller.set_temporary_object(player)
        item_name = self.panel.players.GetItem(item_id, 1)
        player_name = item_name.GetText()
        item_fullname = self.panel.players.GetItem(item_id, 2)
        player_fullname = item_fullname.GetText()
        view_edit = ViewPlayer(self, "Edit player", is_editor=True)
        view_edit.panel.code.SetValue(player_code)
        view_edit.panel.name.SetValue(player_name)
        view_edit.panel.fullname.SetValue(player_fullname)
        # Qui utilizzo ChangeValue per non scatenare EVT_TEXT, come invece
        # succederebbe usando SetValue. Questo EVT_TEXT, cercherebbe un
        # Handler al livello attuale (Frame) e non trovandolo, passerebbe
        # al Parent, che invece ha proprio un Bind di EVT_TEXT, proprio con
        # la textctrl 'ppl', la quale richiamerebbe la callback
        # 'on_text_entry, facendo casino.
        # view_edit.panel.btn_delete.Enable()
        view_edit.SetWindowStyle(wx.STAY_ON_TOP)

    def on_list_column(self, event):
        self.panel.players.DeleteAllItems()
        id_column = event.GetColumn()
        players = self.controller.get_sorted_players(id_column)
        self.fill_players(players)

    def fill_players(self, players):
        for player in players:
            index = self.panel.players.InsertStringItem(sys.maxint,
                                                        str(player.code))
            self.panel.players.SetStringItem(index, 1, str(player.name))
            self.panel.players.SetStringItem(index, 2, str(player.fullname))

    @staticmethod
    def show_message(string):
        wx.MessageBox(string, 'core info', wx.OK | wx.ICON_EXCLAMATION)

    @staticmethod
    def show_subframe(child):
        child.Centre()
        child.Show()

    def quit_subframe(self, event):
        subframe = event.GetEventObject().GetParent()
        if isinstance(subframe, wx.Panel):
            subframe = subframe.GetParent()
        self.Enable()
        subframe.Destroy()


class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent=parent)
        self.status = ProgressStatusBar(self)
        self.players = AutoWidthListCtrl(self)
        self.players.InsertColumn(0, 'code', wx.LIST_FORMAT_RIGHT, 50)
        self.players.InsertColumn(1, 'name', width=125)
        self.players.InsertColumn(2, 'fullname', width=175)

        players_box = wx.BoxSizer(wx.HORIZONTAL)
        players_box.Add(self.players, 1, wx.EXPAND)
        btn_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="Refresh")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(players_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.status, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)


class ProgressStatusBar(wx.StatusBar):
    """Custom StatusBar with a built-in progress bar"""
    def __init__(self, parent, id_=wx.ID_ANY, style=wx.SB_FLAT,
                 name='ProgressStatusBar'):
        super(ProgressStatusBar, self).__init__(parent, id_, style, name)
        self._changed = False
        self.busy = False
        self.timer = wx.Timer(self)
        self.progress_bar = wx.Gauge(self, style=wx.GA_HORIZONTAL)
        self.progress_bar.Hide()

        self.SetFieldsCount(2)
        self.SetStatusWidths([-1, 155])
        # self.SetBackgroundColour('Pink')

        self.Bind(wx.EVT_IDLE, lambda evt: self.__reposition())
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def __del__(self):
        if self.timer.IsRunning():
            self.timer.Stop()

    def __reposition(self):
        """Repositions the gauge as necessary"""
        if self._changed:
            field = self.GetFieldsCount() - 1
            rect = self.GetFieldRect(field)
            progress_bar_pos = (rect.x + 2, rect.y + 2)
            self.progress_bar.SetPosition(progress_bar_pos)
            progress_bar_size = (rect.width - 8, rect.height - 4)
            self.progress_bar.SetSize(progress_bar_size)
        self._changed = False

    # noinspection PyUnusedLocal
    def on_size(self, evt):
        self._changed = True
        self.__reposition()
        evt.Skip()

    # noinspection PyUnusedLocal
    def on_timer(self, evt):
        if not self.progress_bar.IsShown():
            self.timer.Stop()
        if self.busy:
            self.progress_bar.Pulse()

    def run(self, rate=100):
        if not self.timer.IsRunning():
            self.timer.Start(rate)

    def get_progress(self):
        return self.progress_bar.GetValue()

    def set_progress(self, val):
        if not self.progress_bar.IsShown():
            self.show_progress(True)

        if val == self.progress_bar.GetRange():
            self.progress_bar.SetValue(0)
            self.show_progress(False)
        else:
            self.progress_bar.SetValue(val)

    def set_range(self, val):
        if val != self.progress_bar.GetRange():
            self.progress_bar.SetRange(val)

    def show_progress(self, show=True):
        self.__reposition()
        self.progress_bar.Show(show)

    def start_busy(self, rate=100):
        self.busy = True
        self.__reposition()
        self.show_progress(True)
        if not self.timer.IsRunning():
            self.timer.Start(rate)

    def stop_busy(self):
        self.timer.Stop()
        self.show_progress(False)
        self.progress_bar.SetValue(0)
        self.busy = False

    def is_busy(self):
        return self.busy


class ViewExtract(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        self.title = title
        super(ViewExtract, self).__init__(parent=self.parent, title=title,
                                          style=STYLE)
        self.controller = self.parent.controller
        self.panel = PanelExtract(parent=self)
        self.SetSize((300, 150))
        # bindings
        self.Bind(wx.EVT_BUTTON, self.parent.quit_subframe, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_extract, self.panel.btn_extract)

        self.parent.show_subframe(self)  # Show and center the frame

    # noinspection PyUnusedLocal
    def on_extract(self, event):
        day = self.panel.day.GetValue()
        if day:
            if self.controller.are_evaluations_ready(day):
                self.controller.extract_evaluations(day)
                self.Destroy()
            else:
                wx.MessageBox('Evaluations for day %s not ready!' % day, '', OK)
        else:
            wx.MessageBox('Please set a day to extract!', '', OK)


class PanelExtract(wx.Panel):
    def __init__(self, parent):
        super(PanelExtract, self).__init__(parent)
        # Attributes
        self.day = wx.TextCtrl(self)
        # Layout
        text_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        text_sizer.Add(wx.StaticText(self, label="Day:"), 0, ACV)
        text_sizer.Add(self.day, 0, ACV)
        text_sizer.AddGrowableCol(1)

        button_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        self.btn_extract = wx.Button(self, wx.ID_OK, label="Extract")
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_quit.SetDefault()
        button_sizer.Add(self.btn_extract, 0, ACV)
        button_sizer.Add(self.btn_quit, 0, ACV)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_sizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetBackgroundColour('LightGray')
        self.SetSizer(sizer)
