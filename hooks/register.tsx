import type { EngineInterface, Register, ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import { SCENE } from './scene.js'

// Moonlit night: deep navy surfaces, moon-white text, a soft moonlight-blue accent.
const { theme, problems } = makeColors({
  label: 'ASCII Hills (Night)',
  only: 'dark',
  roles: { accent: '#8aa8f0', danger: '#e06c75', success: '#7cc48a', warning: '#e2b86b', pro: '#b994d6' },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#070d1c',
        'surface-1': '#0c1426',
        'surface-2': '#111b31',
        'surface-3': '#16223b',
        'text-primary': '#e7ecf7',
        'text-secondary': '#bcc7db',
        'text-muted': '#93a0b8',
      },
    },
  },
})

// Lessons from earlier looks in this app: the scene must stay pure ASCII and
// well under 131,072 bytes, and draw with isInteractive. It is static now.
const LOOK: ThemeSetArgs = {
  colors: theme,
  overrideColorScheme: 'dark',
  backdrop: { scene: 'ascii-hills', glass: { blur: 2, tint: '#070d1c', opacity: 0.4 } },
}

// A reload can run session.start before the desktop app is attached; send the
// look again whenever a client attaches, and on each prompt until one draws it.
let drawn = false

async function apply($: EngineInterface): Promise<void> {
  const set = await $.theme.set(LOOK)

  drawn = set.isDrawn
  $.ui.status(set.isDrawn ? undefined : set.reason)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))

    if (unpainted !== undefined) {
      $.ui.toast(unpainted)
    }
    await apply($)

    return next(e)
  })

  on('session.attach', async ($, e, next) => {
    const result = await next(e)

    await apply($)

    return result
  })

  on('prompt.submit', async ($, e, next) => {
    if (!drawn) {
      await apply($)
    }

    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    if (e.surface !== 'desktop' && e.surface !== 'mobile') {
      return next(e)
    }
    const { Svg } = $.ui.resolve(e)

    return <Svg source={SCENE} alt="Clean ASCII-art rolling hill at night under a full moon and a starry sky" isInteractive />
  })
}
