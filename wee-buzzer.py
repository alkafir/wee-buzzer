#!/usr/bin/python
"""
    Wee-buzzer - Weechat buzzer plug-in.
    Copyright (C) 2012 Alfredo 'IceCoder' Mungo

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os
import time

try:
  import weechat
except:
  print('wee-buzzer is a weechat plugin script, and is not intended to be run standalone.')
  sys.exit(1)


wb_options = {
  'sound_app' : 'aplay',
  'sound_file' : '/usr/share/sounds/icecoder/wee-buzzer-alert.wav',
  'sound_threshold' : 5, #5 secs
  'messg_threshold' : 1,  #1 sec
  'replist_autoremove' : 'on',
  'beep': 'on'
}

sound_time = 0
messg_time = 0
nickname = ''
repchans = []
replist_enabled = True


def _playSound():
  if _checkTime(True, wb_options['sound_threshold']):
    if wb_options['beep'] == 'on':
      with open('/dev/tty', 'w') as f: f.write('\a')
    else:
      os.system('%s %s 1>&2 2>/dev/null' % (wb_options['sound_app'], wb_options['sound_file']))

def parseMsg(data, buff, date, tags, displayed, highlight, prefix, msg):
  if len(nickname) > 0:
    bname =  weechat.buffer_get_string(buff, 'name')

    if bname.find('server.') != 0 and msg.find(nickname) != -1 and bname != 'weechat' and msg.find('Nick') != 0:
      weechat.prnt('', 'You have been called in %s (%s)' % (bname, msg))
      _playSound()
  return weechat.WEECHAT_RC_OK

def privMsg(data, signal, signal_data):
  pmsg = signal_data.split(' ')
  if pmsg[0].find(':') == 0:
    pmsg = pmsg[1:]
  
  if pmsg[1].find('#') != 0 and pmsg[1].find('&') != 0:
  
    if _checkTime(False, wb_options['messg_threshold']):
      weechat.prnt('', "You have a private message.")
    
    _playSound()
  return weechat.WEECHAT_RC_OK

def _checkTime(sound, threshold):
  global sound_time, messg_time

  tm = time.time()
  if sound:
      last_time = sound_time
  else:
      last_time = messg_time
      
  if tm > (last_time + threshold):
    if sound:
      sound_time = tm
    else:
      messg_time = tm
    return True
  else:
    return False

def nickSet(data, signal, signal_data):
  global nickname
  ssd = signal_data.split(' ')
  
  if len(ssd) >= 2:
    if ssd[0].find(':') == 0:
      ssd = ssd[1:]
    nickname = ssd[1]
  return weechat.WEECHAT_RC_OK

def cfg_check(data, option, value):
  global wb_options

  opt = option.rsplit('.', 1)[1]

  if opt == 'messg_threshold' or opt == 'sound_threshold': #integer
    wb_options[opt] = int(value)
  else: #string
    wb_options[opt] = value

  return weechat.WEECHAT_RC_OK

""" Add channels to the report-list.

chans: list of channels
"""
def _rep_add(chans):
  global repchans

  for chan in chans:
    if chan in repchans:
      weechat.prnt('', 'Channel %s already in report-list' % weechat.buffer_get_string(chan, 'name'))
      continue
    else:
      repchans.append(chan)
      weechat.prnt('', 'Added channel %s to report-list' % weechat.buffer_get_string(chan, 'name'))

""" Delete channels from the report-list.

chans: list of channels
"""
def _rep_del(chans):
  global repchans

  for chan in chans:
    if chan in repchans:
      repchans.remove(chan)
      weechat.prnt('', 'Removed channel %s from report-list' % weechat.buffer_get_string(chan, 'name'))

def _rep_list():
  if len(repchans) > 0:
    weechat.prnt('', 'Channels in report list:')
    for chan in repchans:
      weechat.prnt('', '  %s' % weechat.buffer_get_string(chan, "name"))
  else:
    weechat.prnt('', 'Report list is empty.')

def report_chan(data, buff, date, tags, displayed, hilighted, prefix, message):
  if replist_enabled:
    if displayed:
      if buff in repchans:
        _playSound()
        weechat.prnt('', 'Message delivered to %s' % weechat.buffer_get_string(buff, 'name'))
        if wb_options['replist_autoremove'] == 'on': repchans.remove(buff)
  return weechat.WEECHAT_RC_OK

def clbkReport(data, buff, args):
  global replist_enabled

  if len(args) == 0: #no arguments, print state
    weechat.prnt('', 'Report-list is %s' % ('on' if replist_enabled else 'off'))
    return weechat.WEECHAT_RC_OK

  pargs = args.split(' ')
  cmd = pargs.pop(0)

  if cmd == 'add':
    if len(pargs) == 0: #add the current buffer
      _rep_add([buff])

  elif cmd == 'del':
    if len(pargs) == 0: #del the current buffer
      _rep_del([buff])

  elif cmd == 'list':
    if len(pargs) > 0:
      weechat.prnt('', "Report-list: 'list' command accepts no parameters.")
    else:
      _rep_list()

  elif cmd == 'on': replist_enabled = True
  elif cmd == 'off': replist_enabled = False

  else:
    weechat.prnt('', "Report-list: unknown command. Type '/help replist' for help.")

  if cmd == 'on' or cmd == 'off':
    weechat.prnt('', 'Report-list is %s' % ('on' if replist_enabled else 'off'))

  return weechat.WEECHAT_RC_OK

def _init_options():
  global wb_options

  for opt, def_val in wb_options.items():
    if not weechat.config_is_set_plugin(opt):
      weechat.config_set_plugin(opt, str(def_val))
      
  for key in wb_options:
    cfg_check('', '.%s' % key, weechat.config_get_plugin(key))

weechat.register('wee-buzzer', 'Alfredo \'IceCoder\' Mungo', '1.1', 'GPL3', 'Message buzzer', '', '')

weechat.hook_signal("*,irc_in2_privmsg", "privMsg", '')
weechat.hook_signal('*,irc_out_nick', 'nickSet', '')
weechat.hook_print('', '', nickname, 1, 'parseMsg', '')
weechat.hook_print('', '', '', 0, 'report_chan', '')
weechat.hook_config("plugins.var.python.wee-buzzer.*", "cfg_check", "")
weechat.hook_command("replist", "Report-list command.\n",

                     "[add]"
                     "|| [del]"
                     "|| [list]"
                     "|| [on | off]"
                     "|| [empty]",

                     "add: Add the current buffer\n"
                     "del: Delete the current buffer\n"
                     "list: List the buffers in the report-list\n"
                     "on|off: Enable/disable the report-list system"
                     "empty: Empty the report-list",

                     "list"
                     "||add"
                     "||del"
                     "||on"
                     "||off"
                     "||empty",
                     "clbkReport", '')

_init_options()
