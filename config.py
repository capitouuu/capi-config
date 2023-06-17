from libqtile.widget import base
from libqtile import extension
from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile.command import lazy
from libqtile import qtile
import os
import psutil
import subprocess

# crear widget para controlar cmus desde la barra de qtile con botones


# definir el widget de Cmus
class CmusWidget(widget.TextBox):
    def __init__(self, **config):
        super().__init__(text='Cmus')        
        # Crea los botones como widgets de texto
        self.play_pause_button = widget.TextBox(text=' ▶️', fontsize=14, padding=5)
        self.prev_button = widget.TextBox(text=' ⏮️', fontsize=14, padding=5)
        self.next_button = widget.TextBox(text=' ⏭️', fontsize=14, padding=5)
        # Agrega los callbacks para los botones
        self.play_pause_button.add_callbacks({
            'Button1': self.toggle_play_pause
        })
        self.prev_button.add_callbacks({
            'Button1': self.prev
        })
        self.next_button.add_callbacks({
            'Button1': self.next
        })
    def update(self):
        self.text = self.get_current_track()
    def toggle_play_pause(self):
        subprocess.call(['cmus-remote', '-u'])
    def next(self):
        subprocess.call(['cmus-remote', '-n'])
    def prev(self):
        subprocess.call(['cmus-remote', '-r'])
    def get_current_track(self):
        try:
            status = subprocess.check_output(['cmus-remote', '-Q'], stderr=subprocess.STDOUT)
            status = status.decode('utf-8').strip().split('\n')
            title = ''
            artist = ''
            for s in status:
                if 'tag title ' in s:
                    title = s[10:]
                if 'tag artist ' in s:
                    artist = s[11:]
            if title == '':
                title = '[No title]'
            if artist == '':
                artist = '[No artist]'
            return '{} - {}'.format(artist, title)
        except subprocess.CalledProcessError:
            return ''
    def buttons(self):
        # Devuelve las tres imágenes de botones como lista
        return [
            self.prev_button,
            self.play_pause_button,
            self.next_button
        ]

class Moc(base.ThreadPoolText):
    """A simple MOC widget. Show the artist and album of now listening song and allow basic mouse control from the bar:
    - toggle pause (or play if stopped) on left click;
    - skip forward in playlist on scroll up;
    - skip backward in playlist on scroll down.
    MOC (http://moc.daper.net) should be installed.
    """
    def __init__(self, **config):
        base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(Moc.defaults)
        self.paused = False

    def button_press(self, x, y, button):
        if button == 1:
            os.system("mocp -G" if self.paused else "mocp -P")
            self.paused = not self.paused
        elif button == 4:
            os.system("mocp -f")
        elif button == 5:
            os.system("mocp -r")

    def poll(self):
        moc_info = subprocess.check_output(["mocp", "-i"]).decode("utf-8")
        artist = re.search(r"Artist:\s(.+)", moc_info).group(1)
        title = re.search(r"SongTitle:\s(.+)", moc_info).group(1)
        state = re.search(r"State:\s(.+)", moc_info).group(1)

        if state == "PLAY":
            return f"{artist} - {title}"
        else:
            return "Paused"






mod = "mod4"
terminal = 'xfce4-terminal'
terminal2 = 'alacritty'

def swap_screens():
    qtile.cmd_next_screen()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    # Abrir terminales mod+enter = xfce4, mod+a = Alacrtty.
    Key([mod], "Return", lazy.spawn("xfce4-terminal"), desc="Launch xfce4-termianl"),
    Key([mod], "a", lazy.spawn("alacritty"), desc="launch alacrtty"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([mod], "v", lazy.spawn("pavucontrol"), desc="launch pavucontrol control de audio"),
    Key([mod], "d", lazy.run_extension(extension.DmenuRun(
        #
        dmenu_pront=">",
        background="#2d2833", # color del background
        selected_background="#482177", # color de la seleccionado
        foreground="#7e6f90", # color del texto
        selected_foroground="#ae99c8" # color del texto seleccionado

        )), desc="launch dmenu"),
    Key([mod], "f", lazy.group["4"].toscreen(),
        lazy.spawn("firefox")),
    Key([mod], "b", lazy.group['4'].toscreen(),
        lazy.spawn("/usr/bin/microsoft-edge-stable %U")),
    Key([mod], "v", lazy.group["0"].toscreen(),
        lazy.spawn(terminal + " -e glances")),
    #Key([mod], "f", lazy.spawn("firefox"), desc="launch firefox"),
    Key([mod], "s", lazy.spawn("arandr"), desc="launch arandr"),
    Key([mod], "t", lazy.spawn("thunar"), desc="launch thunar"),
    Key([mod], "p", lazy.spawn("xfce4-appfinder"), desc="launch appfinder buscador de aplicaciones"),
    Key([mod, "shift"], "p", lazy.spawn("pamac-manager"), desc="launch pamac manager"),
    Key([mod], "x", lazy.function(swap_screens)),

    # configuracion de teclas de volumen.
    # Volume controls
    Key([], "XF86AudioRaiseVolume", lazy.spawn("amixer sset Master 5%+")),
    Key([], "XF86AudioLowerVolume", lazy.spawn("amixer sset Master 5%-")),
    Key([], "XF86AudioMute", lazy.spawn("amixer sset Master toggle")),
    # atajo de teclado para ejecutar Cmus

    # launch cmus in group number 9
    Key([mod], "c", lazy.group["9"].toscreen(),
        lazy.spawn(terminal + " -e cmus")),
    Key([mod], "m", lazy.group["9"].toscreen(),
        lazy.spawn(terminal + " -e mocp")),
    Key([mod], "e", lazy.group["1"].toscreen(),
        lazy.spawn("subl")),
    Key([mod], "n", lazy.group["9"].toscreen(),
        lazy.spawn(terminal2 + " -e ncspot")),
]

groups = [
    Group("1", matches=[Match(wm_class=['subl'])]),
    Group("2"),
    Group("3"),
    Group("4", matches=[Match(wm_class=["firefox","Microsoft Edge"])]),
    Group("5"),
    Group("6"),
    Group("7"),
    Group("8"),
    Group("9"),
    Group("0"),
]
#group_cmus = Group("cmus")

for i in groups:
    keys.extend(
        [
            # mod1 + letter of group = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            # mod1 + shift + letter of group = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod1 + shift + letter of group = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

layouts = [
    layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=4),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),:
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=2,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        bottom=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                # widget.TextBox("default config", name="default"),
                # widget.TextBox("Press &lt;M-r&gt; to spawn", foreground="#d75f5f"),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.StatusNotifier(),
                widget.Systray(),
                #CmusWidget().buttons(play_pause_button),
                widget.Clock(format="%Y-%m-%d %a %I:%M %p"),
                widget.QuickExit(),
                #widget.CmusWidget(),
                widget.PulseVolume(),
                
            ],
            22,
            background='#1e0140'
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
    ),

    Screen(
        bottom=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                    ),
                widget.Cmus(
                    fmt="{}",
                    font="sans",
                    background=None,# "#412c79",
                    foreground="#7e6f90",
                    #max_chars=0,
                    scroll=True,
                    ),
                widget.Net(interface="wlan0"),
                widget.Memory(measure_mem="G"),
                widget.CPU(),
                widget.QuickExit(),


            ],
            22,
            background='#1e0140'
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
    ),
]

config = {
        "keys": keys,
        "screens": screens,
}


# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
