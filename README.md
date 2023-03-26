# Waybar wttr Weather forecast

## Intro
Weather forecast custom widget for waybar that caches its results.

## Setup
- Clone this repo to ~/.config/waybar
- Setup Python Dependencies
There are different ways to do this. The easiest way may be to install system packages for the Python dependencies in requirements.txt
On Ubuntu/Debian, this could be:
```bash
sudo apt install python3-requests python3-platformdirs
```

The following method uses Python 3's builtin venv module to store dependencies in their own environment.
```bash
cd ~/.config/waybar/weather
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Configure waybar
If you used the venv method above, you can copy and paste this verbatim.
```
    "custom/weather": {
        "exec": "$HOME/.config/waybar/weather/venv/bin/python $HOME/.config/waybar/weather/weather.py 2>/dev/null",
        "format": "{}",
        "tooltip": true,
        "interval": 3600,
        "return-type": "json"
    },
```

Restart waybar, or restart your wm, or re-login, or reboot.

## Credits
- https://gist.github.com/bjesus/f8db49e1434433f78e5200dc403d58a3
- https://github.com/khaneliman/dotfiles/blob/7d00ee4f66cdfcfce6fc3d11f0a7c6b3f00cc57f/dots/linux/hyprland/home/.config/waybar/scripts/weather.py
- https://github.com/chubin/wttr.in
