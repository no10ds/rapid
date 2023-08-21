import { screen } from '@testing-library/react'
import ConditionalWrapper from './ConditionalWrapper'
import { renderWithProviders } from '@/lib/test-utils'
import { FC } from 'react'

const Content: FC = () => <div data-testid="content">test</div>
const renderWrapper = (children) => <div data-testid="wrapper">{children}</div>

describe('Page: Sign in', () => {
  it('renders with wrapper', () => {
    renderWithProviders(
      <ConditionalWrapper condition={true} wrapper={renderWrapper}>
        <Content />
      </ConditionalWrapper>
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
    expect(screen.getByTestId('wrapper')).toBeInTheDocument()
  })

  it('renders without wrapper', () => {
    renderWithProviders(
      <ConditionalWrapper condition={false} wrapper={renderWrapper}>
        <Content />
      </ConditionalWrapper>
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
    expect(screen.queryByTestId('wrapper')).not.toBeInTheDocument()
  })
})
