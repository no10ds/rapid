import { fireEvent, screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import { renderWithProviders } from '@/lib/test-utils'
import SchemaCreatePage from '@/pages/schema/create'

const mockProps = jest.fn()
jest.mock('@/components/SchemaCreate', () => (props) => {
  mockProps(props)
  return <div data-testid="create-schema-component" />
})

const mockGenerate = {
  metadata: {
    domain: 'example.com',
    dataset: 'My dataset example',
    sensitivity: 'PUBLIC',
    description: 'In a very long description far far away....',
    key_value_tags: {},
    key_only_tags: [],
    owners: [
      {
        name: 'Tiny Tim',
        email: 'owners@test.com'
      }
    ],
    update_behaviour: 'APPEND'
  },
  columns: [
    {
      name: 'contents of file',
      partition_index: null,
      data_type: 'object',
      allow_null: true,
      format: null
    }
  ]
}

describe('Page: Upload page', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders', async () => {
    fetchMock.mockResponseOnce(JSON.stringify(['default']), { status: 200 })
    renderWithProviders(<SchemaCreatePage />)

    await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

    expect(screen.getByTestId('submit')).toBeInTheDocument()
    expect(screen.getByTestId('field-level')).toBeInTheDocument()
    expect(screen.getByTestId('field-layer')).toBeInTheDocument()
    expect(screen.getByTestId('field-domain')).toBeInTheDocument()
    expect(screen.getByTestId('field-title')).toBeInTheDocument()
    expect(screen.getByTestId('field-file')).toBeInTheDocument()
  })

  describe('on submit', () => {

    const file = new File(['test'], 'testfile.txt', { type: 'text/plain' })
    const formData = new FormData()
    formData.append('file', file)

    it('errors', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(['default']), { status: 200 })
      renderWithProviders(<SchemaCreatePage />)
      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(screen.queryAllByText('Required')).toHaveLength(3)
      })

      expect(
        screen.getByText('Upload the data to generate the schema for')
      ).toBeInTheDocument()
    })

    it('success', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(['default']), { status: 200 })
      fetchMock.mockResponseOnce(JSON.stringify(mockGenerate))
      renderWithProviders(<SchemaCreatePage />)

      await waitForElementToBeRemoved(() => screen.queryByRole('progressbar'))

      userEvent.selectOptions(screen.getByTestId('field-level'), 'PUBLIC')
      userEvent.selectOptions(screen.getByTestId('field-layer'), 'default')
      await userEvent.type(screen.getByTestId('field-domain'), 'my-domain')
      await userEvent.type(screen.getByTestId('field-title'), 'my-title')
      await fireEvent.change(screen.getByTestId('field-file'), {
        target: { files: [file] }
      })

      await userEvent.click(screen.getByTestId('submit'))

      await waitFor(async () => {
        expect(fetchMock).toHaveBeenCalledWith(
          '/api/schema/default/PUBLIC/my-domain/my-title/generate',
          {
            body: formData,
            credentials: 'include',
            method: 'POST'
          }
        )
      })

      await waitFor(async () => {
        expect(screen.getByTestId('create-schema-component')).toBeInTheDocument()
      })
      expect(mockProps).toHaveBeenCalledWith(
        expect.objectContaining({
          schemaData: expect.objectContaining({ ...mockGenerate })
        })
      )
    })
  })
})
