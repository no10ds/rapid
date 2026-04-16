import AccountLayout from '@/components/Layout/AccountLayout'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { CreateSchema as CreateSchemaComponent } from '@/components'
import {
  generateSchema,
  schemaGenerateSchema,
  GlobalSensitivities,
  ProtectedSensitivity
} from '@/service'
import { getLayers } from '@/service/fetch'
import { GenerateSchemaResponse, SchemaGenerate } from '@/service/types'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useState, useEffect, ReactNode } from 'react'
import { useForm, Controller } from 'react-hook-form'

function CreateSchema() {
  const [file, setFile] = useState<File | undefined>()

  const {
    isLoading: isLayersLoading,
    data: layersData,
    error: layersError
  } = useQuery(['layers'], getLayers)

  const { control, handleSubmit, setValue } = useForm<SchemaGenerate>({
    resolver: zodResolver(schemaGenerateSchema),
    mode: 'onSubmit',
    defaultValues: {
      sensitivity: '',
      layer: '',
      domain: '',
      title: ''
    }
  })

  useEffect(() => {
    if (layersData?.length === 1) {
      setValue('layer', layersData[0])
    }
  }, [layersData, setValue])

  const {
    isLoading,
    mutate,
    error,
    data: schemaData
  } = useMutation<GenerateSchemaResponse, Error, { path: string; data: FormData }>({
    mutationFn: generateSchema
  })

  if (schemaData) {
    return <CreateSchemaComponent schemaData={schemaData} layersData={layersData} />
  }

  if (isLayersLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  if (layersError) {
    return <ErrorCard error={layersError as Error} />
  }

  return (
    <form
      className="form-wrap-wide"
      onSubmit={handleSubmit(
        async (data: SchemaGenerate) => {
          const formData = new FormData()
          formData.append('file', file)
          const path = `${data.layer}/${data.sensitivity}/${data.domain}/${data.title}/generate`
          await mutate({ path, data: formData })
        },
        (errors) => {
          console.error('Form validation errors:', errors)
        }
      )}
    >
      {/* Card 1 — Dataset properties */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">1</div>
          <div className="form-card-title">Dataset properties</div>
        </div>
        <div className="form-card-body">
          <Controller
            name="sensitivity"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <div className="field-row">
                <label className="f-lbl" htmlFor="field-level">
                  Sensitivity Level
                </label>
                <select
                  {...field}
                  id="field-level"
                  className="f-sel"
                  data-testid="field-level"
                  style={fieldError ? { borderColor: 'var(--red)' } : undefined}
                >
                  <option value="" disabled>
                    Please select
                  </option>
                  {[...GlobalSensitivities, ProtectedSensitivity].map((value) => (
                    <option key={value}>{value}</option>
                  ))}
                </select>
                {fieldError && (
                  <span className="f-hint" style={{ color: 'var(--red)' }}>
                    {fieldError.message}
                  </span>
                )}
              </div>
            )}
          />

          <Controller
            name="layer"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <div className="field-row">
                <label className="f-lbl" htmlFor="field-layer">
                  Dataset Layer
                </label>
                <select
                  {...field}
                  id="field-layer"
                  className="f-sel"
                  data-testid="field-layer"
                  style={fieldError ? { borderColor: 'var(--red)' } : undefined}
                >
                  <option value="" disabled>
                    Please select
                  </option>
                  {layersData.map((value) => (
                    <option key={value}>{value}</option>
                  ))}
                </select>
                {fieldError && (
                  <span className="f-hint" style={{ color: 'var(--red)' }}>
                    {fieldError.message}
                  </span>
                )}
              </div>
            )}
          />

          <Controller
            name="domain"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <div className="field-row">
                <label className="f-lbl" htmlFor="field-domain">
                  Dataset Domain
                </label>
                <input
                  {...field}
                  id="field-domain"
                  className="f-sel"
                  placeholder="showcase"
                  data-testid="field-domain"
                  style={fieldError ? { borderColor: 'var(--red)' } : undefined}
                />
                {fieldError && (
                  <span className="f-hint" style={{ color: 'var(--red)' }}>
                    {fieldError.message}
                  </span>
                )}
              </div>
            )}
          />

          <Controller
            name="title"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <div className="field-row">
                <label className="f-lbl" htmlFor="field-title">
                  Dataset Title
                </label>
                <input
                  {...field}
                  id="field-title"
                  className="f-sel"
                  placeholder="movies"
                  data-testid="field-title"
                  style={fieldError ? { borderColor: 'var(--red)' } : undefined}
                />
                {fieldError && (
                  <span className="f-hint" style={{ color: 'var(--red)' }}>
                    {fieldError.message}
                  </span>
                )}
              </div>
            )}
          />
        </div>
      </div>

      {/* Card 2 — Upload CSV */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">2</div>
          <div className="form-card-title">Upload sample data</div>
        </div>
        <div className="form-card-body">
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
            Upload a CSV file to automatically generate the schema from its structure.
          </p>

          {!file && (
            <label className="upload-zone" htmlFor="schema-file">
              <div className="upload-ico">↑</div>
              <div className="upload-text">Click to browse or drag &amp; drop</div>
              <div className="upload-sub">CSV file only</div>
            </label>
          )}

          {file && (
            <div
              style={{
                fontSize: '12px',
                color: 'var(--pink)',
                fontWeight: 500,
                marginBottom: '8px'
              }}
            >
              {file.name}
            </div>
          )}

          <input
            name="file"
            id="schema-file"
            type="file"
            data-testid="field-file"
            style={{ display: 'none' }}
            onChange={(event) => setFile(event.target.files[0])}
          />

          {error && (
            <div className="warn-box" style={{ marginTop: '12px' }}>
              {error?.message}
            </div>
          )}
        </div>
        <div className="form-actions">
          <button
            className="btn-primary"
            type="submit"
            data-testid="submit"
            disabled={isLoading || !file}
          >
            {isLoading ? 'Generating…' : 'Generate schema'}
          </button>
        </div>
      </div>
    </form>
  )
}

export default CreateSchema

CreateSchema.getLayout = (page: ReactNode) => (
  <AccountLayout title="Create Schema">{page}</AccountLayout>
)
