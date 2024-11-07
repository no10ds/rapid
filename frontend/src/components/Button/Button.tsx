import { forwardRef } from 'react'
import { LoadingButton as MuiButton } from '@mui/lab'
import Link from 'next/link'
import { Props, ButtonOverrides } from './types'
import { FormHelperText, styled } from '@mui/material'

const StyledButton = styled(MuiButton)``

const Button = forwardRef<HTMLButtonElement, Props>(
  ({ href, error, disableRoute, ...rest }, ref) => {
    const routeProps = href ? { component: 'a', to: href } : {}
    const props = { ...routeProps, ...overrides[rest.color], ref: ref, ...rest }

    return href && !disableRoute ? (
      <Link href={href} passHref>
        <StyledButton {...props} />
      </Link>
    ) : (
      <>
        <StyledButton {...props} href={href} />
        {!!error && <FormHelperText error>{error}</FormHelperText>}
      </>
    )
  }
)

Button.displayName = 'Button'

export default Button

export const overrides: ButtonOverrides = {
  primary: { variant: 'contained' },
  secondary: { variant: 'contained' },
  tertiary: { variant: 'outlined' },
  error: { variant: 'contained' }
}
