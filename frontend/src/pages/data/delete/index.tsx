import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import { deleteDataset, getDatasetsUi } from '@/service'
import { Dataset, DeleteDatasetResponse } from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useState, ReactNode } from 'react'

function DeleteDataset({ datasetInput = null }: { datasetInput?: Dataset | null }) {
  const router = useRouter()
  const { layer, domain, dataset: datasetName } = router.query ?? {}

  const fromQuery: Dataset | null =
    layer && domain && datasetName
      ? { layer: layer as string, domain: domain as string, dataset: datasetName as string, version: 1, sensitivity: undefined }
      : null

  const [dataset, setDataset] = useState<Dataset | null>(datasetInput ?? fromQuery)
  const [deleteDatasetSuccessDetails, setDeleteDatasetSuccessDetails] = useState<string | undefined>()

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  const { isLoading, mutate, error } = useMutation<DeleteDatasetResponse, Error, { path: string }>({
    mutationFn: deleteDataset,
    onMutate: () => setDeleteDatasetSuccessDetails(undefined),
    onSuccess: (data) => setDeleteDatasetSuccessDetails(data.details)
  })

  if (isDatasetsListLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  const currentDataset = dataset

  return (
    <form
      className="form-page"
      onSubmit={async (event) => {
        event.preventDefault()
        if (currentDataset) {
          await mutate({ path: `${currentDataset.layer}/${currentDataset.domain}/${currentDataset.dataset}` })
        }
      }}
    >
      {/* Warning banner */}
      <div className="form-card" style={{ marginBottom: '16px' }}>
        <div className="form-card-hd form-card-hd-danger">
          <div className="form-card-num form-card-num-danger">!</div>
          <div className="form-card-title form-card-title-danger">Destructive action</div>
        </div>
        <div className="form-card-body">
          <div className="warn-box" style={{ marginBottom: 0 }}>
            This action permanently deletes the dataset, its schema, crawlers, and all raw
            data. This <strong>cannot be undone</strong>.
          </div>
        </div>
      </div>

      {/* Select dataset */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Select dataset to delete</div>
        </div>
        <div className="form-card-body">
          {fromQuery ? (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {[['Layer', fromQuery.layer], ['Domain', fromQuery.domain], ['Dataset', fromQuery.dataset]].map(([label, val]) => (
                <div key={label} style={{ padding: '8px 14px', background: '#f9fafb', border: '1px solid var(--border)', borderRadius: 'var(--radius)', fontSize: 12 }}>
                  <span style={{ color: 'var(--text-tertiary)', fontWeight: 600, marginRight: 6, textTransform: 'uppercase', fontSize: 10, letterSpacing: '.04em' }}>{label}</span>
                  <span style={{ fontWeight: 500 }}>{val}</span>
                </div>
              ))}
            </div>
          ) : (
            <DatasetSelector
              datasetsList={datasetsList}
              setParentDataset={setDataset}
              enableVersionSelector={false}
            />
          )}

          {deleteDatasetSuccessDetails && (
            <div
              data-testid="delete-status"
              style={{
                marginTop: '14px',
                padding: '10px 14px',
                background: 'var(--green-faint)',
                border: '1px solid rgba(16,185,129,.2)',
                borderRadius: '6px',
                fontSize: '12px',
                color: '#059669',
                fontWeight: 500
              }}
            >
              Dataset deleted: {currentDataset
                ? `${currentDataset.layer}/${currentDataset.domain}/${currentDataset.dataset}`
                : deleteDatasetSuccessDetails}
            </div>
          )}

          {error && (
            <div className="warn-box" style={{ marginTop: '14px', marginBottom: 0 }}>
              {error.message}
            </div>
          )}
        </div>
        <div className="form-actions">
          <button
            className="btn-danger"
            type="submit"
            data-testid="submit"
            disabled={!currentDataset || isLoading}
          >
            {isLoading ? 'Deleting…' : 'Delete dataset'}
          </button>
          <button
            className="btn-secondary"
            type="button"
            onClick={() => router.push('/catalog')}
          >
            Cancel
          </button>
          {currentDataset && !deleteDatasetSuccessDetails && (
            <span className="info-chip" style={{ marginLeft: 'auto' }}>
              <span>{currentDataset.layer} / {currentDataset.domain} / {currentDataset.dataset}</span>
            </span>
          )}
        </div>
      </div>
    </form>
  )
}

export default DeleteDataset

DeleteDataset.getLayout = (page: ReactNode) => (
  <AccountLayout title="Delete Data">{page}</AccountLayout>
)
