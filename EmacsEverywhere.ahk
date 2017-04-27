;
; AutoHotkey Version: 1.x
; Language:         English
; Platform:         WinNT
; inspirator:  David <tchepak@gmail.com>
; Script Function:
;   Provides an Emacs-like keybinding emulation mode that can be toggled on and off using
;   the ctrl+CapsLock key.
;
; Cheat Sheet/Reminder
; --:---------------------
; # : Windows Key
; ! : Alt
; ^ : Control
; + : Shift
; 
;==========================
;Initialization
;==========================
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

#InstallKeybdHook
#UseHook

enabledIcon := "EmacsEverywhere_on.ico"
disabledIcon := "EmacsEverywhere_off.ico"
; C-x status
is_pre_x = 0
; C-Space status
is_pre_spc = 0
EmacsModeStat := false
SetEmacsMode(false)

;==========================
;Timer Subroutine
;==========================
KeyX:
  SetTimer, KeyX, off
  global is_pre_x = 0
  return

;==========================
;Emacs mode toggle
;==========================
;; Switch to Emacs Mode
^\::
  if (not EmacsHasFocus() )
  {
    SetEmacsMode(!EmacsModeStat)
  }
  else
  {
    Send ^\
  }

  return

SetEmacsMode(toActive) {
  local iconFile := toActive ? enabledIcon : disabledIcon
  local state := toActive ? "ON" : "OFF"

  EmacsModeStat := toActive

  Menu, Tray, Icon, %iconFile%,
  Menu, Tray, Tip, Emacs Everywhere`nEmacs mode is %state%
  TrayTip, Emacs Key Mapping, Mapping is %state%, 3

  Send {Shift Up}
}

;==========================
;is target
; WinActive("ahk_class Chrome_WidgetWin_1") ||
;==========================
is_target() {
  ; force disable
  if ( WinActive("ahk_class Emacs") || WinActive("ahk_class mintty") || WinActive("ahk_class Console_2_Main") || WinActive("ahk_class PuTTY") )
  {
    return false
  }
  return true
}

EmacsHasFocus() {
  if ( WinActive("ahk_class Emacs") )
  {
    return true
  }
}

ChromeHasFocus() {
  if ( WinActive("ahk_class Chrome_WidgetWin_1") )
  {
    return true
  }
}

;; MattMc: OneNoteHasFocus is needed for up, down work-around in OneNote.
;; See move_line(), previous_line(), next_line() below.
;; OneNote up and down cursor keys don't work for some unknown reason.
;; Work-around (use Ctrl) found online and seems to work.
OneNoteHasFocus()
{
   if(WinActive("ahk_class Framework::CFrame")) {
      return true
   }
   return false
}

IsMSWord()
{
   if(WinActive("ahk_class OpusApp")) {
      return true
   }
   return false
}

;; Emacs State Flag is True AND not in actual Emacs
IsInEmacsMode() {
  global EmacsModeStat
  if (EmacsModeStat && is_target()) {
    return true
  } else {
    return false
  }
}

;;; Assumes CapsLock is mapped to Left Control
;;+RCtrl::Capslock

;==========================
;Action Functions
;==========================
delete_char() {
  Send {Del}
  global is_pre_spc = 0
  Return
}

delete_backward_char() {
  Send {BS}
  global is_pre_spc = 0
  Return
}

kill_line() {
  if ( IsMSWord() )
  {
    Send {ShiftDown}{End}{Left}{ShiftUp}
  }
  else
  {
    Send {ShiftDown}{End}{ShiftUp}
  }

  Sleep 10 ;[ms]
  Send ^x
  global is_pre_spc = 0
  Return
}

open_line() {
  Send {END}{Enter}{Up}
  global is_pre_spc = 0
  Return
}

quit() {
  Send {ESC}
  global is_pre_spc = 0
  Return
}

newline() {
  Send {Enter}
  global is_pre_spc = 0
  Return
}

indent_for_tab_command() {
  Send {Tab}
  global is_pre_spc = 0
  Return
}

newline_and_indent() {
  Send {Enter}{Tab}
  global is_pre_spc = 0
  Return
}

isearch_forward() {
  Send ^f
  global is_pre_spc = 0
  Return
}

isearch_backward() {
  Send ^f
  global is_pre_spc = 0
  Return
}

kill_region() {
  Send ^x
  global is_pre_spc = 0
  Return
}

kill_ring_save() {
  Send ^c
  global is_pre_spc = 0
  Return
}

yank() {
  Send ^v
  global is_pre_spc = 0
  Return
}

undo() {
  Send ^z
  global is_pre_spc = 0
  Return
}

find_file() {
  Send ^o
  global is_pre_x = 0
  Return
}

save_buffer() {
  Send, ^s
  global is_pre_x = 0
  Return
}

close_windows_program() {
  Send !{F4}
  global is_pre_x = 0
  Return
}

move_beginning_of_line() {
  global
  if is_pre_spc
    Send +{HOME}
  Else
    Send {HOME}
  Return
}

move_end_of_line() {
  global
  if is_pre_spc
    Send +{END}
  Else
    Send {END}
  Return
}

move_line(key) {
  global

  if (OneNoteHasFocus())
  {
    key = ^%key%
  }

  if (is_pre_spc)
    Send +%key%
  else
    Send %key%

  return
}

previous_line() {
  move_line("{Up}")
}

next_line() {
  move_line("{Down}")
}

backward_char() {
  global
  if is_pre_spc
    Send +{Left}
  Else
    Send {Left}
  Return
}

scroll_up() {
  global
  if is_pre_spc
    Send +{PgUp}
  Else
    Send {PgUp}
  Return
}

scroll_down() {
  global
  if is_pre_spc
    Send +{PgDn}
  Else
    Send {PgDn}
  Return
}

singleLetterFallbackToDefault() {
  state := GetKeyState("Capslock", "T")
  If(state) {
    Send +%A_ThisHotkey%  ; + for upper case
  }
  Else {
    Send %A_ThisHotkey%
  }
}

;==========================
;Keybindings
;==========================
;^x::
;  If IsInEmacsMode() {
;    global is_pre_x = 1
;    SetTimer, KeyX, 1000
;  }
;  Else
;    Send %A_ThisHotkey%
;  Return

h::
  If (IsInEmacsMode() && is_pre_x) {
    Send ^a  ; select all
    global is_pre_x = 0
  }
  Else
    singleLetterFallbackToDefault()
  Return

^f::
  If IsInEmacsMode() {
    If is_pre_x {
      Send ^o
      global is_pre_x = 0
    } Else {
      if is_pre_spc
        Send +{Right}
      Else
        Send {Right}
    }
  } Else
    Send %A_ThisHotkey%
  Return

!f::
  If IsInEmacsMode() {
    If is_pre_x {
      Send ^o
      global is_pre_x = 0
    } Else {
      if is_pre_spc
        Send +^{Right}
      Else
        Send ^{Right}
    }
  } Else
    Send %A_ThisHotkey%
  Return

;^c::
;  if IsInEmacsMode()
;  {
;     if is_pre_x
;     {
;        close_windows_program()
;        global is_pre_x = 0
;     }
;  }
;  else
;  {
;    Send %A_ThisHotkey%
;  }
;  Return

^d::
  If IsInEmacsMode()
    delete_char()
  Else
    Send %A_ThisHotkey%
  Return

^k::
  If IsInEmacsMode()
    kill_line()
  Else
    Send %A_ThisHotkey%
  Return
^o::
  If IsInEmacsMode()
    open_line()
  Else
    Send %A_ThisHotkey%
  Return
^g::
  If IsInEmacsMode()
    quit()
  Else
    Send %A_ThisHotkey%
  Return
^j::
  If IsInEmacsMode()
    newline_and_indent()
  Else
    Send %A_ThisHotkey%
  Return
^m::
  If IsInEmacsMode()
    newline()
  Else
    Send %A_ThisHotkey%
  Return
^i::
  If IsInEmacsMode()
    indent_for_tab_command()
  Else
    Send %A_ThisHotkey%
  Return
^s::
  If IsInEmacsMode()
  {
    If is_pre_x
      save_buffer()
    Else
      isearch_forward()
  }
  Else
    Send %A_ThisHotkey%
  Return
^r::
  If IsInEmacsMode()
    isearch_backward()
  Else
    Send %A_ThisHotkey%
  Return
^w::
  If IsInEmacsMode() and not ChromeHasFocus()
    kill_region()
  Else
    Send %A_ThisHotkey%
  Return
!w::
  If IsInEmacsMode()
    kill_ring_save()
  Else
    Send %A_ThisHotkey%
  Return
^y::
  If IsInEmacsMode()
    yank()
  Else
    Send %A_ThisHotkey%
  Return
^/::
  If IsInEmacsMode() and not OneNoteHasFocus()
    undo()
  Else
    Send %A_ThisHotkey%
  Return
^+/::
  if IsInEmacsMode()
    send ^/
  return

;$^{Space}::
^vk20sc039::
  If IsInEmacsMode()
  {
    If is_pre_spc
    {
       is_pre_spc = 0
       Send {Right}
    }
    Else
    {
       is_pre_spc = 1
    }
  }
  Else
  {
       Send {CtrlDown}{Space}{CtrlUp}
  }
  Return
^@::
  If IsInEmacsMode()
  {
    If is_pre_spc
      is_pre_spc = 0
    Else
      is_pre_spc = 1
  }
  Else
    Send %A_ThisHotkey%
  Return
^a::
  If IsInEmacsMode()
    move_beginning_of_line()
  Else
    Send %A_ThisHotkey%
  Return
^e::
  If IsInEmacsMode()
    move_end_of_line()
  Else
    Send %A_ThisHotkey%
  Return
^p::
  If IsInEmacsMode()
    previous_line()
  Else
    Send %A_ThisHotkey%
  Return
^n::
  If IsInEmacsMode()
    next_line()
  Else
    Send %A_ThisHotkey%
  Return

^b::
  If IsInEmacsMode()
    backward_char()
  Else
    Send %A_ThisHotkey%
  Return

^+b::
  if IsInEmacsMode()
    Send ^b
  return

;^v::
;  If IsInEmacsMode()
;    scroll_down()
;  Else
;    Send %A_ThisHotkey%
;  Return
;^+v::
;  If IsInEmacsMode()
;    scroll_up()
;  Else
;    Send %A_ThisHotkey%
;  Return

; Alt Space to pull up the windows menu.
;!space::
;   send ^{Escape}
;   return

^?::
   WinGetClass, winClassName, A
   MsgBox, ClassName- "%winClassName%"
   return

;==========================
;Original
;==========================
SendCommand(emacsKey, translationToWindowsKeystrokes, secondWindowsKeystroke="") {
  if (IsInEmacsMode()) {
    Send, %translationToWindowsKeystrokes%
    if (secondWindowsKeystroke<>"") {
      Send, %secondWindowsKeystroke%
    }
  } else {
    Send, %emacsKey% ;passthrough original keystroke
  }
  return
}
;==========================
;Word Navigation
;==========================

$!p::SendCommand("!p","^{Up}")

$!n::SendCommand("!n","^{Down}")

;$!f::SendCommand("!f","^{Right}")

$!b::SendCommand("!b","^{Left}")

;==========================
;Page Navigation
;==========================
$!<::SendCommand("!<","^{Home}")

$!>::SendCommand("!>","^{End}")

;==========================
;Undo
;==========================

$^_::SendCommand("^_","^z")

;==========================
;Delete
;==========================
$!d::SendCommand("!d","^+{Right}","{Delete}")



;==========================
;Disable Win Key but not its combinations
;==========================
;~LWin Up:: return

;==========================
;Auto Save
;==========================
;Toggle = 0
;#MaxThreadsPerHotkey 2
;$F8::              ;hit F8 to toggle script on and off.
;  Toggle := !Toggle
;  While Toggle{
;    if (WinActive("ahk_class classFoxitReader")) {
;      Send, ^s
;    }
;    Sleep, 60*1000 ; in ms
;  }
;return
