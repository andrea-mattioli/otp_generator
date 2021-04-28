#!/usr/bin/python
import pyotp
import yaml
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio
import sys
import os
from pathlib import Path
data_path = "~/.local/share/"
data_dir = "/.local/share/otp_generator"
home_dir = str(Path.home())
Path(home_dir+data_dir).mkdir(parents=True, exist_ok=True)
otp_config_file = Path(home_dir+data_dir+"/otp_config.yaml")
otp_config_file.touch(exist_ok=True)
otp_count_file = Path(home_dir+data_dir+"/otp_count.yaml")
otp_count_file.touch(exist_ok=True)
config_dict_file = {'otp_config' : {'pin':'','url':''}}
if otp_config_file.stat().st_size == 0:
    with open(otp_config_file, 'w') as file:
        documents = yaml.dump(config_dict_file, file)
count_dict_file = {'count':1}
if otp_count_file.stat().st_size == 0:
    with open(otp_count_file, 'w') as file:
        documents = yaml.dump(count_dict_file, file)

class SettingsPage(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Settings", deletable=False)
        self.set_default_size(200, 100)
        self.set_border_width(10)
        grid = Gtk.Grid(column_homogeneous=True, column_spacing=10, row_spacing=10)
        self.pin_label = Gtk.Label()
        self.pin_label.set_text("Pin: ")
        self.url_label = Gtk.Label()
        self.url_label.set_text("Url: ")
        self.entry_pin = Gtk.Entry()
        self.entry_url = Gtk.Entry()
        self.activity_mode = False
        try:
            with open(otp_config_file, 'r') as nf:
                otp_cfg = yaml.safe_load(nf)
            url=(otp_cfg["otp_config"]["url"])
            pin=(otp_cfg["otp_config"]["pin"])
            self.entry_pin.set_text(pin)
            self.entry_url.set_text(url)
        except:
            pass
        button_save = Gtk.Button(label="Save")
        button_discard = Gtk.Button(label="Discard")
        check_hide = Gtk.CheckButton(label="Hide")
        grid.add(self.pin_label)
        grid.attach(self.url_label, 0, 1, 1, 1)
        grid.attach(self.entry_pin, 1, 0, 1, 1)
        grid.attach(self.entry_url, 1, 1, 1, 1)
        grid.attach(button_save, 0, 2, 1, 1 )
        grid.attach(button_discard, 2, 2, 1, 1 )
        grid.attach(check_hide, 2, 0, 1, 1 )
        check_hide.connect("toggled", self.on_hide_toggled)
        check_hide.set_active(True)
        self.entry_pin.set_visibility(False)
        button_save.connect("clicked", self.on_save_clicked)
        button_discard.connect("clicked", self.on_discard_clicked)       
        self.add(grid)

    def write_settings(self, pin, url):
        with open(otp_config_file) as f:
            otp_config = yaml.safe_load(f)
        otp_config["otp_config"]["pin"] = pin
        otp_config["otp_config"]["url"] = url
        with open(otp_config_file, 'w') as f:
            yaml.dump(otp_config, f)
    
    def on_save_clicked(self, widget):
        pin = self.entry_pin.get_text()
        url = self.entry_url.get_text()
        self.write_settings(pin, url)
        self.destroy()

    def on_discard_clicked(self, widget):
        self.destroy()
        
    def on_hide_toggled(self, button):
        value = button.get_active()
        self.entry_pin.set_visibility(value)   

class MainPage(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, title="Mattiols OTP", application=app)
        self.set_default_size(200, 100)
        self.set_border_width(10)
        grid = Gtk.Grid(column_homogeneous=False, column_spacing=10, row_spacing=10)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.otp_label = Gtk.Label()
        self.progressbar = Gtk.ProgressBar()
        self.image = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.MENU)
        button_copy = Gtk.Button(label="Copy")
        button_settings = Gtk.Button(label="Settings")
        button_generate = Gtk.Button()
        button_generate.add(self.image)
        button_generate.set_property("width-request", 1)
        button_generate.set_property("height-request", 1)
        grid.add(button_generate)
        grid.attach(self.progressbar, 2, 0, 1, 1)
        grid.attach(self.otp_label, 1, 0, 1, 1)
        grid.attach(button_copy, 2, 0, 1, 1 )
        grid.attach(button_settings, Gtk.PositionType.LEFT, 1, 3, 1 )
        button_copy.connect("clicked", self.copy)
        button_settings.connect("clicked", self.on_settings_clicked)
        button_generate.connect("clicked", self.on_generate_clicked)
        self.add(grid)
        self.timeout_id = GLib.timeout_add(300, self.on_timeout, None)
        self.activity_mode = False
        self.gen_otp()  

    def copy(self, widget):
        self.clipboard.set_text(self.otp_label.get_text(), -1)

    def set_count(self, count):
        with open(otp_count_file) as f:
            otp_count = yaml.safe_load(f)
        otp_count["count"] = count
        with open(otp_count_file, 'w') as f:
            yaml.dump(otp_count, f)

    def gen_otp(self):
        try:
            with open(otp_config_file, 'r') as nf:
                otp_cfg = yaml.safe_load(nf)
            url=(otp_cfg["otp_config"]["url"])
            pin=(otp_cfg["otp_config"]["pin"])
            with open(otp_count_file, 'r') as f:
                otp_count = yaml.safe_load(f)
            count=(otp_count["count"])
            hotp = pyotp.parse_uri(url)
            count += 1
            self.activity_mode = False
            self.set_count(count)
            self.otp_label.set_text("%s%s" % (pin,hotp.at(count)))
        except:
            pass
            self.activity_mode = True

    def on_settings_clicked(self, button):
        win = SettingsPage()
        win.show_all()

    def on_generate_clicked(self, button):
        self.activity_mode=False
        self.progressbar.set_fraction(0.0)
        self.gen_otp()

    def on_timeout(self, user_data):
        if self.activity_mode:
            self.progressbar.set_fraction(0.0)
            win = SettingsPage()
            win.show_all()
        else:
            new_value = self.progressbar.get_fraction() + 0.01
            if new_value > 1:
                self.gen_otp()
                new_value = 0
            self.progressbar.set_fraction(new_value)
            return True

class MyOTP(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = MainPage(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.quit_callback)
        self.add_action(quit_action)

    def quit_callback(self, action, parameter):
        self.quit()

app = MyOTP()
exit_status = app.run(sys.argv)
sys.exit(exit_status)