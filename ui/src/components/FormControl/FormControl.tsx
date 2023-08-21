import { FormControl as BaseFormControl } from '@mui/material'
import { ComponentProps } from 'react'
import { styled } from '@mui/system';


const FormControl = styled(BaseFormControl) <ComponentProps<typeof BaseFormControl>>`
    .MuiInputBase-root {
      margin-bottom: 4px;
      height: 32px !important;
      padding: 0px;
    }
`

export default FormControl;