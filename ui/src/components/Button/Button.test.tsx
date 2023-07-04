import { screen } from '@testing-library/react'
import { renderWithProviders } from '@/utils/test-utils'
import Button from './Button'

describe('Button', () => {
  it('Renders', async () => {
    const text = 'Click me'
    renderWithProviders(<Button>{text}</Button>)
    expect(screen.getByText(text)).toBeInTheDocument()
  })
})
