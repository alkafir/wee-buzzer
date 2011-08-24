"""
    Wee-buzzer - Weechat buzzer plug-in.
    Copyright (C) 2011 Alfredo 'IceCoder' Mungo

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

import os
import weechat
import time

#BEGIN - CONFIGURATION PARAMETERS
SOUNDAPP = 'aplay'
SOUNDFILE = '/usr/share/sounds/icecoder/wee-buzzer-alert.wav'

sound_threshold = 5 #5 secs
messg_threshold = 1 #1 sec
#END - CONFIGURATION PARAMETERS

sound_time = 0
messg_time = 0

nickname = ''

def playSound():
  global SOUNDFILE, sound_threshold, sound_time, SOUNDAPP
  
  if checkTime(True, sound_threshold):
    os.system('%s %s 1>&2 2>/dev/null' % (SOUNDAPP, SOUNDFILE))

def parseMsg(data, buff, date, tags, displayed, highlight, prefix, msg):
  global messg_threshold, messg_time, nickname
  
  if len(nickname) > 0:
    bname =  weechat.buffer_get_string(buff, 'name')

    if bname.find('server.') != 0 and msg.find(nickname) != -1 and bname != 'weechat' and msg.find('Nick') != 0:
      weechat.prnt('', 'You have been called in %s (%s)' % (bname, msg))
      playSound()
      
  return weechat.WEECHAT_RC_OK

def privMsg(data, signal, signal_data):

  pmsg = signal_data.split(' ')
  if pmsg[0].find(':') == 0:
    pmsg = pmsg[1:]
  
  if pmsg[1].find('#') != 0 and pmsg[1].find('&') != 0:
  
    if checkTime(False, messg_threshold):
      weechat.prnt('', "You have a private message.")
    
    playSound()
  return weechat.WEECHAT_RC_OK

def checkTime(sound, threshold):
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

weechat.register('Wee-buzzer', 'Alfredo \'IceCoder\' Mungo', '1.0', 'GPL3', 'Message buzzer', '', '')
weechat.hook_signal("*,irc_in2_privmsg", "privMsg", '')
weechat.hook_print('', '', nickname, 1, 'parseMsg', '')
weechat.hook_signal('*,irc_out_nick', 'nickSet', '')
