import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import { getDatasetsUi } from '@/service'
import { Dataset } from '@/service/types'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'

function DownloadData({ datasetInput = null }: { datasetInput?: Dataset | null }) {
  const router = useRouter()
  const [dataset, setDataset] = useState<Dataset | null>(datasetInput)

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  if (isDatasetsListLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  if (Object.keys(datasetsList).length === 0) {
    return (
      <div className="form-card" data-testid="no-data-helper">
        <div className="form-card-body">
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '10px' }}>
            You currently do not have any data to download. Get started by creating a schema
            and uploading a dataset that you want to store in rAPId.
          </p>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            All datasets will then become available to be downloaded from here.
          </p>
        </div>
      </div>
    )
  }

  const datasetLabel = dataset
    ? `${dataset.layer} / ${dataset.domain} / ${dataset.dataset}`
    : null

  return (
    <form
      className="form-wrap-wide"
      onSubmit={(event) => {
        event.preventDefault()
        if (dataset) {
          router.push(
            `/data/download/${dataset.layer}/${dataset.domain}/${dataset.dataset}?version=${dataset.version}`
          )
        }
      }}
    >
      {/* Card 1 — Select dataset */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Select dataset</div>
        </div>
        <div className="form-card-body">
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Download the contents of a datasource from rAPId. Select the relevant dataset
            and version to download from. Large datasets may take some time to query.
          </p>
          <DatasetSelector datasetsList={datasetsList} setParentDataset={setDataset} />
        </div>
        <div className="form-actions">
          <button
            className="btn-primary"
            type="submit"
            data-testid="submit"
            disabled={!dataset}
          >
            Next
          </button>
          {datasetLabel && (
            <span className="info-chip" style={{ marginLeft: 'auto' }}>
              <span>{datasetLabel}</span>
            </span>
          )}
        </div>
      </div>
    </form>
  )
}

export default DownloadData

DownloadData.getLayout = (page: ReactNode) => (
  <AccountLayout title="Download Data">{page}</AccountLayout>
)
