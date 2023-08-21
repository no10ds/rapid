import { ComponentProps } from 'react'
import {
    Autocomplete as BaseAutocomplete,
} from '@mui/material'

import { styled } from '@mui/system';


export const Autocomplete = styled(BaseAutocomplete) <ComponentProps<typeof BaseAutocomplete>>`
    .MuiInputBase-input {
      padding: 4px 15px 0px 15px;
      height: 100%;
      width: 100%;
      font-size: 13px;
      font-weight: 400
    }
  `


export const GroupHeader = styled('div')(() => ({
    position: 'sticky',
    top: '-8px',
    padding: '4px 10px',
    backgroundColor: 'lightgrey'
}));

export const GroupItems = styled('ul')({
    padding: 0,
});
