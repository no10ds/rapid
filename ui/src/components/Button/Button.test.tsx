import { screen } from '@testing-library/react'
import { renderWithProviders } from '@/lib/test-utils'
import Button from './Button'

describe('Button', () => {
  it('Renders', async () => {
    const text = 'Click me'
    renderWithProviders(<Button>{text}</Button>)
    expect(screen.getByText(text)).toBeInTheDocument()
  })
})
