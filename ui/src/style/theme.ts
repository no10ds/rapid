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
  default: ['Khula', 'Poppins', 'sans-serif']
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
      main: colors.blue2,
      light: colors.blue1,
      dark: colors.blue3
    }
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
      lineHeight: '150%;',
      letterSpacing: '0.15px',
      '&.MuiTypography-gutterBottom': {
        marginBottom: 10
      }
    },
    body2: {
      fontSize: 12,
      fontWeight: 500,
      color: colors.grey4,
      lineHeight: '150%;',
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
    MuiListItemButton: {
      styleOverrides: {
        root: {
          '&.Mui-selected': {
            '&:hover': {
              backgroundColor: '#f8f8f8'
            },
            backgroundColor: '#f8f8f8',

            '.MuiListItemText-root': {
              fontWeight: 900
            }
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
          fontSize: 16,
          // To stop chrome autofill changing background color
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
          fontSize: 16
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          backgrondColor: colors.blue1
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
          fontSize: 16
        }
      }
    },
    MuiFormControlLabel: {
      styleOverrides: {
        root: {
          '.MuiFormControlLabel-label': {
            fontSize: 16
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
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)',
          padding: 20
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)'
        }
      }
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          boxShadow: 'none'
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
    }
  }
})

export default theme
