import {
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select as BasicSelect,
  styled
} from '@mui/material'
import { ComponentProps, FC, forwardRef, useId } from 'react'
import SelectCheckbox from './SelectCheckbox'
import { Props } from './types'

const StyledBasicSelect = styled(BasicSelect)<ComponentProps<typeof BasicSelect>>`
  .MuiInputBase-input {
    padding: 4px 15px 0px 15px;
    height: 100%;
    width: 100%;
    font-size: 13px;
    font-weight: 400;
    color: ${(p) => p.theme.colors.dark1};
  }
`

const StyledFormControl = styled(FormControl)<ComponentProps<typeof FormControl>>`
  .MuiInputBase-root {
    margin-bottom: 4px;
    height: 32px !important;
    padding: 0px;
  }
`

const Select: FC<Props> = forwardRef<FC, Props>(
  (
    { checkboxes, data = [], fullWidth = true, children, error, helperText, ...props },
    ref
  ) => {
    const id = useId()
    const labelId = `label-${id}`

    const newProps = {
      ...props,
      labelId,
      data,
      ref
    }

    return (
      <StyledFormControl error={!!error} fullWidth={fullWidth}>
        <InputLabel id={labelId} />

        {checkboxes ? (
          <SelectCheckbox {...newProps} />
        ) : (
          <StyledBasicSelect {...newProps}>
            {data.map((item) => (
              <MenuItem value={item} key={item}>
                {item}
              </MenuItem>
            ))}
            {children}
          </StyledBasicSelect>
        )}
        {!!helperText && <FormHelperText>{helperText}</FormHelperText>}
      </StyledFormControl>
    )
  }
)

Select.displayName = 'Select'

export default Select
