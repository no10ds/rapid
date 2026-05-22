import { createTheme, Shadows } from '@mui/material/styles'
import { Colors } from './types'

const colors: Colors = {
  black: '#000',
  white: '#fff',
  dark1: '#313337',
  grey1: '#E9EAEC',
  grey2: '#AEAEAE',
  grey3: '#666',
  grey4: '#4b5563',
  blue1: '#60a5fa',
  blue2: '#3b82f6',
  blue3: '#2563eb',
  pink1: '#f472b6',
  pink2: '#ec4899',
  pink3: '#db2777'
}

const fonts = {
  default: ['Poppins', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
  mono: ['DM Mono', 'monospace']
}

const theme = createTheme({
  colors,
  palette: {
    mode: 'light',
    primary: {
      main: colors.pink2,
      light: colors.pink1,
      dark: colors.pink3
    },
    secondary: {
      main: '#1e3a5f',
      light: '#2a4a72',
      dark: '#162d4a'
    },
    error: {
      main: '#ef4444'
    },
    warning: {
      main: '#f59e0b'
    },
    success: {
      main: '#10b981'
    },
    info: {
      main: '#3b82f6'
    },
    background: {
      default: '#eef0f3',
      paper: '#ffffff'
    },
    text: {
      primary: '#111827',
      secondary: '#4b5563',
      disabled: '#9ca3af'
    },
    divider: '#e5e7eb'
  },
  typography: {
    fontFamily: fonts.default.join(','),
    h1: {
      fontWeight: 700,
      fontSize: 26,
      lineHeight: '123.5%',
      letterSpacing: '-1px',
      '&.MuiTypography-gutterBottom': {
        marginBottom: 16
      }
    },
    h2: {
      fontWeight: 600,
      fontSize: 20,
      lineHeight: '150.0%',
      color: colors.dark1,
      letterSpacing: '-1px',
      '&.MuiTypography-gutterBottom': {
        marginBottom: 16
      }
    },
    h3: {
      fontWeight: 700,
      fontSize: 16,
      lineHeight: '123.5%',
      letterSpacing: '-1px',
      '&.MuiTypography-gutterBottom': {
        marginBottom: 16
      }
    },
    body1: {
      fontWeight: 500,
      fontSize: 14,
      lineHeight: '150%',
      letterSpacing: '0.15px',
      '&.MuiTypography-gutterBottom': {
        marginBottom: 10
      }
    },
    body2: {
      fontSize: 12,
      fontWeight: 500,
      color: colors.grey4,
      lineHeight: '150%',
      letterSpacing: '0.15px',
      '&.MuiTypography-gutterBottom': {
        marginBottom: 10
      }
    },
    caption: {
      fontSize: 16,
      fontWeight: 500,
      color: colors.grey4
    },
    h4: undefined,
    h5: undefined,
    h6: undefined,
    subtitle1: undefined,
    subtitle2: undefined,
    overline: undefined
  },
  shadows: Array(25).fill('none') as Shadows,
  shape: {
    borderRadius: 5
  },
  spacing: [0, 5, 10, 16, 30, 60, 110],
  components: {
    MuiCssBaseline: {
      styleOverrides: `
        @font-face {
          font-family: 'Khula';
          font-style: normal;
          font-display: swap;
          font-weight: 400;
          src: local('Khula-Regular'), url(/fonts/Khula-Regular.ttf) format('truetype');
          unicodeRange: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF;
        }

        @font-face {
          font-family: 'Khula';
          font-style: normal;
          font-display: swap;
          font-weight: 600;
          src: url(/fonts/Khula-SemiBold.ttf) format('truetype');
          unicodeRange: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF;
        }

        @font-face {
          font-family: 'Khula';
          font-style: normal;
          font-display: swap;
          font-weight: 700;
          src: url(/fonts/Khula-Bold.ttf) format('truetype');
          unicodeRange: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF;
        }
      `
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: '#fafafa',
          '& .MuiTableCell-head': {
            fontSize: 10,
            fontWeight: 600,
            letterSpacing: '0.07em',
            textTransform: 'uppercase',
            color: '#9ca3af',
            padding: '10px 16px',
            borderBottom: '1px solid #f3f4f6',
            whiteSpace: 'nowrap'
          }
        }
      }
    },
    MuiTableCell: {
      styleOverrides: {
        body: {
          fontSize: 13,
          padding: '11px 16px',
          borderBottom: '1px solid #f9fafb',
          color: '#111827'
        }
      }
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&.MuiTableRow-hover:hover': {
            backgroundColor: '#fafafa',
            cursor: 'pointer'
          }
        }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500
        },
        sizeSmall: {
          fontSize: 11,
          height: 28,
          borderRadius: 20,
          paddingLeft: 4,
          paddingRight: 4
        }
      }
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          '&.Mui-selected': {
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.12)'
            },
            backgroundColor: 'rgba(255,255,255,0.08)'
          },
          '&.Mui-disabled': {
            opacity: 1
          },
          borderRadius: 5
        }
      }
    },
    MuiOutlinedInput: {
      defaultProps: {
        notched: false
      }
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          fontSize: 14,
          '& input': {
            '&:-webkit-autofill': {
              transition:
                'background-color 50000s ease-in-out 0s, color 50000s ease-in-out 0s'
            },
            '&:-webkit-autofill:focus': {
              transition:
                'background-color 50000s ease-in-out 0s, color 50000s ease-in-out 0s'
            },
            '&:-webkit-autofill:hover': {
              transition:
                'background-color 50000s ease-in-out 0s, color 50000s ease-in-out 0s'
            }
          }
        }
      }
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          fontSize: 14
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600
        }
      }
    },
    MuiCardActions: {
      styleOverrides: {
        root: {
          textDecoration: 'none',
          a: { textDecoration: 'none' }
        }
      }
    },
    MuiFormLabel: {
      styleOverrides: {
        root: {
          fontSize: 13,
          fontWeight: 600,
          color: '#374151'
        }
      }
    },
    MuiFormControlLabel: {
      styleOverrides: {
        root: {
          '.MuiFormControlLabel-label': {
            fontSize: 14
          }
        }
      }
    },
    MuiToolbar: {
      styleOverrides: {
        root: {
          minHeight: 47,
          height: 47
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0px 1px 3px rgba(0,0,0,0.06), 0px 1px 2px rgba(0,0,0,0.04)',
          padding: 0
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0px 1px 3px rgba(0,0,0,0.06), 0px 1px 2px rgba(0,0,0,0.04)'
        },
        outlined: {
          boxShadow: 'none'
        }
      }
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          fontSize: 13
        }
      }
    },
    MuiTypography: {
      defaultProps: {
        variantMapping: {
          h1: 'h1',
          body1: 'p',
          body2: 'p'
        }
      }
    },
    MuiDialog: {
      styleOverrides: {
        root: {
          '.MuiDialogTitle-root': {
            fontWeight: 600
          }
        }
      }
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4
        }
      }
    }
  }
})

export default theme
