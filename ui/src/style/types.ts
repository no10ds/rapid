import { CSSProperties } from 'react'
/* eslint-disable @typescript-eslint/no-empty-interface */

export type AllColors = keyof Colors

export type Colors = {
  black: CSSProperties['color']
  white: CSSProperties['color']
  grey1: CSSProperties['color']
  grey2: CSSProperties['color']
  grey3: CSSProperties['color']
  grey4: CSSProperties['color']
  dark1: CSSProperties['color']
  blue1: CSSProperties['color']
  blue2: CSSProperties['color']
  blue3: CSSProperties['color']
  pink1: CSSProperties['color']
  pink2: CSSProperties['color']
  pink3: CSSProperties['color']
}

declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    small: true
    h2: true
    h3: true
    h4: false
    h5: false
    h6: false
    subtitle1: false
    subtitle2: false
    body2: true
    overline: false
  }
}

declare module '@mui/material/styles' {
  interface TypographyVariantsOptions {
    // display?: CSSProperties
  }

  interface Theme {
    colors: Colors
  }

  interface ThemeOptions {
    colors: Colors
  }

  interface BreakpointOverrides {
    sm: false
  }
}
