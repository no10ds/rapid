import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import DatasetSelector from '@/components/DatasetSelector/DatasetSelector'
import UploadProgress from '@/components/UploadProgress/UploadProgress'
import { getDatasetsUi, uploadDataset } from '@/service'
import {
  Dataset,
  UploadDatasetResponse,
  UploadDatasetResponseDetails
} from '@/service/types'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useState, ReactNode } from 'react'
import Link from 'next/link'

function UploadDataset({ datasetInput = null }: { datasetInput?: Dataset | null }) {
  const [file, setFile] = useState<File | undefined>()
  const [dataset, setDataset] = useState<Dataset | null>(datasetInput)
  const [disable, setDisable] = useState<boolean>(false)
  const [uploadSuccessDetails, setUploadSuccessDetails] = useState<
    UploadDatasetResponseDetails | undefined
  >()

  const {
    isLoading: isDatasetsListLoading,
    data: datasetsList,
    error: datasetsError
  } = useQuery(['datasetsList', 'WRITE'], getDatasetsUi)

  const { isLoading, mutate, error } = useMutation<
    UploadDatasetResponse,
    Error,
    { path: string; data: FormData }
  >({
    mutationFn: uploadDataset,
    onMutate: () => {
      setUploadSuccessDetails(undefined)
    },
    onSuccess: (data) => {
      setUploadSuccessDetails(data.details)
      setDisable(true)
    }
  })

  if (isDatasetsListLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  const datasetLabel = dataset
    ? `${dataset.layer} / ${dataset.domain} / ${dataset.dataset}`
    : null

  return (
    <form
      className="form-wrap-wide"
      onSubmit={async (event) => {
        event.preventDefault()
        if (dataset && file) {
          const formData = new FormData()
          formData.append('file', file)
          await mutate({
            path: `${dataset.layer}/${dataset.domain}/${dataset.dataset}?version=${dataset.version}`,
            data: formData
          })
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
          <DatasetSelector
            datasetsList={datasetsList}
            setParentDataset={setDataset}
          />
          <div
            style={{
              marginTop: '12px',
              padding: '12px 14px',
              background: '#fafafa',
              border: '1px dashed #e4e4e7',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px'
            }}
          >
            <span style={{ fontSize: '12px', color: '#71717a' }}>
              Can&apos;t find your dataset? You&apos;ll need to create a schema for it first.
            </span>
            <Link
              href="/schema/create"
              className="act-btn"
              style={{ color: 'var(--pink)', borderColor: 'rgba(236,72,153,.3)', whiteSpace: 'nowrap' }}
            >
              + Create schema
            </Link>
          </div>
        </div>
      </div>

      {/* Card 2 — Upload file */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">2</div>
          <div className="form-card-title">Upload file</div>
        </div>
        <div className="form-card-body">
          {datasetLabel && (
            <div className="selected-dataset">
              <div>
                <div className="lbl">Selected dataset</div>
                <div className="val">{datasetLabel}</div>
              </div>
            </div>
          )}

          {!disable && (
            <label className="upload-zone" htmlFor="file">
              <div className="upload-ico">↑</div>
              <div className="upload-text">Drag &amp; drop your CSV file here</div>
              <div className="upload-sub">or click to browse — CSV only, max 100 MB</div>
              {file && (
                <div style={{ fontSize: '12px', color: 'var(--pink)', fontWeight: 500 }}>
                  {file.name}
                </div>
              )}
            </label>
          )}
          <input
            name="file"
            id="file"
            type="file"
            data-testid="upload"
            style={{ display: 'none' }}
            onChange={(event) => setFile(event.target.files[0])}
            key={`file-upload-${disable.toString()}`}
          />

          {uploadSuccessDetails && (
            <div style={{ marginTop: '16px' }}>
              <UploadProgress
                uploadSuccessDetails={uploadSuccessDetails}
                setDisableUpload={setDisable}
              />
            </div>
          )}

          {error && (
            <div
              className="warn-box"
              style={{ marginTop: '12px', background: 'var(--red-faint)', borderColor: '#fecaca' }}
            >
              {error.message}
            </div>
          )}
        </div>
        <div className="form-actions">
          <button
            className="btn-primary"
            type="submit"
            disabled={!dataset || !file || isLoading || disable}
            data-testid="submit"
          >
            {isLoading ? 'Uploading…' : 'Upload dataset'}
          </button>
          <button
            className="btn-secondary"
            type="button"
            onClick={() => {
              setFile(undefined)
              setDataset(null)
              setDisable(false)
              setUploadSuccessDetails(undefined)
            }}
          >
            Cancel
          </button>
          {dataset && (
            <span className="info-chip" style={{ marginLeft: 'auto' }}>
              <span>{datasetLabel}</span>
            </span>
          )}
        </div>
      </div>
    </form>
  )
}

export default UploadDataset

UploadDataset.getLayout = (page: ReactNode) => (
  <AccountLayout title="Upload Data">{page}</AccountLayout>
)
