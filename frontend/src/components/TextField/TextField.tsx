import { TextField as MuiTextField } from '@mui/material'
import { styled } from '@mui/material/styles'
import { ComponentProps } from 'react'

const StyledTextField = styled(MuiTextField)<ComponentProps<typeof MuiTextField>>`
  .MuiInputAdornment-sizeSmall .MuiTypography-root,
  .MuiInputBase-root {
    margin-bottom: 4px;
    min-height: 32px;
    padding: 0px;
  }
  .MuiInputBase-input {
    padding: 4px 15px 0px 15px;
    height: 100%;
    width: 100%;
    font-size: 13px;
    font-weight: 400;
    color: ${(p) => p.theme.colors.dark1};
  }
`

export default StyledTextField
