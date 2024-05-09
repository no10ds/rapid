import { screen } from '@testing-library/react'
import { CreateSchema } from '@/components'
import { GenerateSchemaResponse } from '@/service/types'
import { renderWithProviders } from '@/utils/testing'
import fetchMock from 'jest-fetch-mock'

const mockSchemaData: GenerateSchemaResponse = {
  metadata: {
    domain: 'domain',
    dataset: 'dataset',
    sensitivity: 'PRIVATE',
    layer: 'default',
    description: 'Some base description...',
    owners: [
      {
        name: 'Tiny Tim',
        email: 'tiny_tim@email.com'
      }
    ],
    key_only_tags: [],
    key_value_tags: {},
    update_behaviour: 'APPEND'
  },
  columns: [
    {
      name: 'col1',
      partition_index: null,
      data_type: 'int',
      allow_null: true,
      format: null
    }
  ]
}

const mockLayersData = ['default']

describe('Component: SchemaCreate', () => {
  afterEach(() => {
    fetchMock.resetMocks()
    jest.clearAllMocks()
  })

  it('renders', async () => {
    renderWithProviders(
      <CreateSchema schemaData={mockSchemaData} layersData={mockLayersData} />
    )

    // Expect the initial UI to be populated with the schema data
    expect(screen.getByTestId('sensitivity')).toHaveValue('PRIVATE')
    expect(screen.getByTestId('layer')).toHaveValue('default')
    expect(screen.getByTestId('domain')).toHaveValue('domain')
    expect(screen.getByTestId('dataset')).toHaveValue('dataset')
    expect(screen.getByTestId('description')).toHaveValue('Some base description...')
  })

  it('renders the need to change date format', async () => {
    mockSchemaData.columns[0].data_type = 'date'
    renderWithProviders(
      <CreateSchema schemaData={mockSchemaData} layersData={mockLayersData} />
    )

    // eslint-disable-next-line jest-dom/prefer-in-document
    expect(screen.getAllByTestId('date-format')).toHaveLength(1)
    expect(screen.getAllByTestId('date-format')[0]).toBeRequired()
  })
})
