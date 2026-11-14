# claude-xp-hills

A night-time ASCII-art theme for the Claude desktop app: a moonlit rolling hill under a starry sky, inspired by the classic Windows XP wallpaper.

The whole backdrop is drawn in ASCII characters (a full moon with maria, stars, moonlit cloud banks and a dithered green hill) behind a deep-navy dark theme.

> Original artwork made in the spirit of the XP wallpaper. Not affiliated with or endorsed by Microsoft.

## Install

At the prompt of a Claude Code terminal session:

```
/plugin install ascii-hills --marketplace arasarkan/claude-xp-hills
```

Answer `y` to add the marketplace, then pick a scope.

From a shell:

```
claude plugin install ascii-hills --marketplace arasarkan/claude-xp-hills
```

The backdrop shows in the Claude desktop app (and mobile); in a plain terminal you get the colors only.

## Regenerating the scene

`tools/scene-gen.py` generates the scene SVG (Python 3, no dependencies):

```
python tools/scene-gen.py tools/scene.svg
```

`hooks/scene.js` holds the same SVG as a string, exported as `SCENE`.
