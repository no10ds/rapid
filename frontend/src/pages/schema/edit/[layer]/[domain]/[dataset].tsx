import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { CreateSchema as SchemaForm } from '@/components'
import { getDatasetInfo } from '@/service'
import { getLayers } from '@/service/fetch'
import { GenerateSchemaResponse } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { ReactNode } from 'react'

function EditSchema() {
  const router = useRouter()
  const { layer, domain, dataset } = router.query
  const version = router.query.version ? router.query.version : 0

  const {
    isLoading: isLayersLoading,
    data: layersData,
    error: layersError
  } = useQuery(['layers'], getLayers)

  const {
    isLoading: isInfoLoading,
    data: infoData,
    error: infoError
  } = useQuery(
    ['datasetInfo', layer, domain, dataset, version ? version : 0],
    getDatasetInfo,
    { enabled: !!layer && !!domain && !!dataset }
  )

  if (isLayersLoading || isInfoLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (layersError) return <ErrorCard error={layersError as Error} />
  if (infoError) return <ErrorCard error={infoError as Error} />
  if (!infoData) return null

  const schemaData: GenerateSchemaResponse = {
    metadata: {
      layer: layer as string,
      domain: infoData.metadata.domain,
      dataset: infoData.metadata.dataset,
      sensitivity: infoData.metadata.sensitivity,
      description: infoData.metadata.description,
      update_behaviour: infoData.metadata.update_behaviour,
      key_value_tags: infoData.metadata.key_value_tags || {},
      key_only_tags: infoData.metadata.key_only_tags || [],
      owners: infoData.metadata.owners || [{ name: '', email: '' }]
    },
    columns: infoData.columns.map((col) => ({
      name: col.name,
      partition_index: col.partition_index,
      data_type: col.data_type,
      allow_null: col.allow_null,
      unique: col.unique,
      format: col.format
    }))
  }

  return <SchemaForm schemaData={schemaData} layersData={layersData} mode="edit" />
}

export default EditSchema

EditSchema.getLayout = (page: ReactNode) => (
  <AccountLayout title="Edit Dataset">{page}</AccountLayout>
)
