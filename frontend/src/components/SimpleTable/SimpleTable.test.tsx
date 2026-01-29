import SimpleTable from './SimpleTable'
import { renderWithProviders, screen } from '@/utils/testing'

describe('SimpleTable', () => {
  it('empty row', async () => {
    const text = 'Nothing to see here'
    renderWithProviders(<SimpleTable list={[]} noRowContent={text} />)

    expect(screen.getByTestId('simpletable-empty-rows')).toBeInTheDocument()
    expect(screen.getByTestId('simpletable-empty-rows')).toHaveTextContent(text)
  })
})
