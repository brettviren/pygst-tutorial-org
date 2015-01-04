
#!/usr/bin/env python

import os
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject, Gtk

class GTK_Main:
    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Mpeg2-Player")
        window.set_default_size(500, 400)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        self.entry = Gtk.Entry()
        hbox.add(self.entry)
        self.button = Gtk.Button("Start")
        hbox.pack_start(self.button, False, False, 0)
        self.button.connect("clicked", self.start_stop)
        self.movie_window = Gtk.DrawingArea()
        vbox.add(self.movie_window)
        window.show_all()
        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("filesrc", "file-source")
        demuxer = Gst.ElementFactory.make("mpegpsdemux", "demuxer")
        demuxer.connect("pad-added", self.demuxer_callback)
        self.video_decoder = Gst.ElementFactory.make("mpeg2dec", "video-decoder")
        png_decoder = Gst.ElementFactory.make("pngdec", "png-decoder")
        png_source = Gst.ElementFactory.make("filesrc", "png-source")
        png_source.set_property("location", os.path.realpath("tvlogo.png"))
        mixer = Gst.ElementFactory.make("videomixer", "mixer")
        self.audio_decoder = Gst.ElementFactory.make("mad", "audio-decoder")
        audioconv = Gst.ElementFactory.make("audioconvert", "converter")
        audiosink = Gst.ElementFactory.make("autoaudiosink", "audio-output")
        videosink = Gst.ElementFactory.make("autovideosink", "video-output")
        self.queuea = Gst.ElementFactory.make("queue", "queuea")
        self.queuev = Gst.ElementFactory.make("queue", "queuev")
        ffmpeg1 = Gst.ElementFactory.make("videoconvert", "ffmpeg1")
        ffmpeg2 = Gst.ElementFactory.make("videoconvert", "ffmpeg2")
        ffmpeg3 = Gst.ElementFactory.make("videoconvert", "ffmpeg3")
        videobox = Gst.ElementFactory.make("videobox", "videobox")
        alphacolor = Gst.ElementFactory.make("alphacolor", "alphacolor")
        for ele in (source, demuxer, self.video_decoder, png_decoder, png_source, mixer,
                    self.audio_decoder, audioconv, audiosink, videosink, self.queuea, 
                    self.queuev, ffmpeg1, ffmpeg2, ffmpeg3, videobox, alphacolor):
            self.player.add(ele)

        source.link(demuxer)

        self.queuev.link(self.video_decoder)
        self.video_decoder.link(ffmpeg1)
        ffmpeg1.link(mixer)
        mixer.link(ffmpeg2)
        ffmpeg2.link(videosink)

        png_source.link(png_decoder)
        png_decoder.link(alphacolor)
        alphacolor.link(ffmpeg3)
        ffmpeg3.link(videobox)
        videobox.link(mixer)

        self.queuea.link(self.audio_decoder)
        self.audio_decoder.link(audioconv)
        audioconv.link(audiosink)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        videobox.set_property("border-alpha", 0)
        videobox.set_property("alpha", 0.5)
        videobox.set_property("left", -10)
        videobox.set_property("top", -10)

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            filepath = self.entry.get_text().strip()
            if os.path.isfile(filepath):
                filepath = os.path.realpath(filepath)
                self.button.set_label("Stop")
                self.player.get_by_name("file-source").set_property("location", filepath)
                self.player.set_state(Gst.State.PLAYING)
            else:
                self.player.set_state(Gst.State.NULL)
                self.button.set_label("Start")

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.movie_window.window.xid)

    def demuxer_callback(self, demuxer, pad):
        tpl_property = pad.get_property("template")
        tpl_name = tpl_property.name_template
        print 'demuxer_callback: template name template: "%s"' % tpl_name
        if tpl_name == "video_%02d":
            queuev_pad = self.queuev.get_pad("sink")
            pad.link(queuev_pad)
        elif tpl_name == "audio_%02d":
            queuea_pad = self.queuea.get_pad("sink")
            pad.link(queuea_pad)

GObject.threads_init()
Gst.init(None)        
GTK_Main()
Gtk.main()
