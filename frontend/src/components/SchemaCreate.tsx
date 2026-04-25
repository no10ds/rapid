import {
  createSchema,
  schemaCreateSchema,
  GlobalSensitivities,
  ProtectedSensitivity
} from '@/service'
import {
  CreateSchemaResponse,
  GenerateSchemaResponse,
  SchemaCreate,
  SensitivityEnum
} from '@/service/types'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'

const dataTypes = [
  'bigint', 'boolean', 'char', 'date', 'decimal', 'double',
  'float', 'int', 'smallint', 'string', 'timestamp', 'tinyint', 'varchar'
]

function CreateSchema({
  schemaData,
  layersData
}: {
  schemaData: GenerateSchemaResponse
  layersData: string[]
}) {
  const [newSchemaData, setNewSchemaData] = useState<GenerateSchemaResponse>(schemaData)
  const [keyValueTag, setKeyValueTag] = useState({ key: '', value: '' })
  const [valueTag, setValueTag] = useState('')

  const { control, handleSubmit } = useForm<SchemaCreate>({
    resolver: zodResolver(schemaCreateSchema)
  })

  const { isLoading, mutate, error, isSuccess, data } = useMutation<
    CreateSchemaResponse,
    Error,
    GenerateSchemaResponse
  >({
    mutationFn: createSchema
  })

  const setMeta = (key: string, value: unknown) =>
    setNewSchemaData((prev) => ({ ...prev, metadata: { ...prev.metadata, [key]: value } }))

  const setCol = (name: string, key: string, value: unknown) =>
    setNewSchemaData((prev) => ({
      ...prev,
      columns: prev.columns.map((c) => c.name === name ? { ...c, [key]: value } : c)
    }))

  if (isSuccess) {
    return (
      <div className="form-page">
        <div className="form-card">
          <div className="form-card-hd" style={{ background: 'rgba(16,185,129,.06)', borderBottomColor: 'rgba(16,185,129,.2)' }}>
            <div className="form-card-title" style={{ color: '#059669' }}>Schema created successfully</div>
          </div>
          <div className="form-card-body">
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{data.details}</p>
          </div>
        </div>
      </div>
    )
  }

  const hasDateColumn = newSchemaData.columns.some((c) => c.data_type === 'date')

  return (
    <form
      className="form-page"
      onSubmit={handleSubmit(async (_data: SchemaCreate) => {
        const payload = { ...newSchemaData }
        payload.metadata.owners = [{ email: _data.ownerEmail, name: _data.ownerName }]
        payload.metadata.sensitivity = _data.sensitivity
        payload.metadata.domain = _data.domain
        payload.metadata.dataset = _data.title
        payload.metadata.description = _data.description
        await mutate(payload)
      })}
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
            defaultValue={newSchemaData.metadata.sensitivity.toUpperCase() as SensitivityEnum}
            render={({ field, fieldState: { error: fe } }) => (
              <div className="field-row">
                <label className="f-lbl">Sensitivity Level</label>
                <select {...field} className="f-sel" data-testid="sensitivity" style={fe ? { borderColor: 'var(--red)' } : undefined}>
                  <option value="" disabled>Please select</option>
                  {[...GlobalSensitivities, ProtectedSensitivity].map((v) => <option key={v}>{v}</option>)}
                </select>
                {fe && <span className="f-hint" style={{ color: 'var(--red)' }}>{fe.message}</span>}
              </div>
            )}
          />
          <Controller
            name="layer"
            control={control}
            defaultValue={newSchemaData.metadata.layer}
            render={({ field, fieldState: { error: fe } }) => (
              <div className="field-row">
                <label className="f-lbl">Dataset Layer</label>
                <select {...field} className="f-sel" data-testid="layer" style={fe ? { borderColor: 'var(--red)' } : undefined}>
                  <option value="" disabled>Please select</option>
                  {layersData.map((v) => <option key={v}>{v}</option>)}
                </select>
                {fe && <span className="f-hint" style={{ color: 'var(--red)' }}>{fe.message}</span>}
              </div>
            )}
          />
          <Controller
            name="domain"
            control={control}
            defaultValue={newSchemaData.metadata.domain}
            render={({ field, fieldState: { error: fe } }) => (
              <div className="field-row">
                <label className="f-lbl">Dataset Domain</label>
                <input {...field} className="f-sel" placeholder="showcase" data-testid="domain" style={fe ? { borderColor: 'var(--red)' } : undefined} />
                {fe && <span className="f-hint" style={{ color: 'var(--red)' }}>{fe.message}</span>}
              </div>
            )}
          />
          <Controller
            name="title"
            control={control}
            defaultValue={newSchemaData.metadata.dataset}
            render={({ field, fieldState: { error: fe } }) => (
              <div className="field-row">
                <label className="f-lbl">Dataset Title</label>
                <input {...field} className="f-sel" placeholder="movies" data-testid="dataset" style={fe ? { borderColor: 'var(--red)' } : undefined} />
                {fe && <span className="f-hint" style={{ color: 'var(--red)' }}>{fe.message}</span>}
              </div>
            )}
          />
          <Controller
            name="description"
            control={control}
            defaultValue={newSchemaData.metadata.description}
            render={({ field, fieldState: { error: fe } }) => (
              <div className="field-row">
                <label className="f-lbl">Dataset Description</label>
                <textarea
                  {...field}
                  className="f-sel"
                  rows={2}
                  placeholder="Enter a human readable description of the dataset…"
                  data-testid="description"
                  style={{ resize: 'vertical', ...(fe ? { borderColor: 'var(--red)' } : {}) }}
                />
                {fe && <span className="f-hint" style={{ color: 'var(--red)' }}>{fe.message}</span>}
              </div>
            )}
          />
        </div>
      </div>

      {/* Card 2 — Data types */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">2</div>
          <div className="form-card-title">Validate the data types for the schema</div>
        </div>
        <div className="form-card-body" style={{ padding: 0 }}>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', padding: '0 20px 12px' }}>
            Consult the{' '}
            <a href="https://rapid.readthedocs.io/en/latest/api/schema/" target="_blank" rel="noreferrer" style={{ color: 'var(--pink)' }}>
              schema writing guide
            </a>{' '}
            for further information.
          </p>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #f0f0f0' }}>
                {['Name', 'Data Type', hasDateColumn ? 'Date Format' : '', 'Allows Null', 'Is Unique', 'Partition Index'].map((h, i) =>
                  h ? <th key={i} style={thStyle}>{h}</th> : <th key={i} style={{ ...thStyle, width: 0, padding: 0 }} />
                )}
              </tr>
            </thead>
            <tbody>
              {newSchemaData.columns.map((col) => (
                <tr key={col.name} style={{ borderBottom: '1px solid #f9f9f9' }}>
                  <td style={tdStyle}>{col.name}</td>
                  <td style={tdStyle}>
                    <select className="f-sel" style={{ height: 28, fontSize: 12 }} value={col.data_type} onChange={(e) => setCol(col.name, 'data_type', e.target.value)}>
                      {dataTypes.map((t) => <option key={t}>{t}</option>)}
                    </select>
                  </td>
                  {hasDateColumn && (
                    <td style={tdStyle}>
                      {col.data_type === 'date' && (
                        <input
                          className="f-sel"
                          style={{ height: 28, fontSize: 12, width: 100 }}
                          placeholder="%Y-%m-%d"
                          data-testid="date-format"
                          required
                          onChange={(e) => setCol(col.name, 'format', e.target.value)}
                        />
                      )}
                    </td>
                  )}
                  <td style={tdStyle}>
                    <select className="f-sel" style={{ height: 28, fontSize: 12 }} value={String(col.allow_null)} onChange={(e) => setCol(col.name, 'allow_null', e.target.value === 'true')}>
                      <option>true</option><option>false</option>
                    </select>
                  </td>
                  <td style={tdStyle}>
                    <select className="f-sel" style={{ height: 28, fontSize: 12 }} value={String(col.unique ?? false)} onChange={(e) => setCol(col.name, 'unique', e.target.value === 'true')}>
                      <option>true</option><option>false</option>
                    </select>
                  </td>
                  <td style={tdStyle}>
                    <input
                      className="f-sel"
                      style={{ height: 28, fontSize: 12, width: 70 }}
                      type="number"
                      value={col.partition_index ?? ''}
                      onChange={(e) => setCol(col.name, 'partition_index', parseInt(e.target.value))}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Card 3 — Data owner */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">3</div>
          <div className="form-card-title">Set the data owner</div>
        </div>
        <div className="form-card-body">
          <Controller
            name="ownerEmail"
            control={control}
            defaultValue={newSchemaData.metadata.owners[0].email}
            render={({ field, fieldState: { error: fe } }) => (
              <div className="field-row">
                <label className="f-lbl">Owner Email</label>
                <input {...field} className="f-sel" type="email" style={fe ? { borderColor: 'var(--red)' } : undefined} />
                {fe && <span className="f-hint" style={{ color: 'var(--red)' }}>{fe.message}</span>}
              </div>
            )}
          />
          <Controller
            name="ownerName"
            control={control}
            defaultValue={newSchemaData.metadata.owners[0].name}
            render={({ field, fieldState: { error: fe } }) => (
              <div className="field-row">
                <label className="f-lbl">Owner Name</label>
                <input {...field} className="f-sel" style={fe ? { borderColor: 'var(--red)' } : undefined} />
                {fe && <span className="f-hint" style={{ color: 'var(--red)' }}>{fe.message}</span>}
              </div>
            )}
          />
        </div>
      </div>

      {/* Card 4 — Upload behaviour */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">4</div>
          <div className="form-card-title">Set the file upload behaviour</div>
        </div>
        <div className="form-card-body">
          <div className="field-row">
            <label className="f-lbl">Update Behaviour</label>
            <select className="f-sel" value={newSchemaData.metadata.update_behaviour} onChange={(e) => setMeta('update_behaviour', e.target.value)}>
              <option>APPEND</option>
              <option>OVERWRITE</option>
            </select>
          </div>
        </div>
      </div>

      {/* Card 5 — Tags (optional) */}
      <div className="form-card">
        <div className="form-card-hd">
          <div className="form-card-num">5</div>
          <div className="form-card-title">Tags <span style={{ fontWeight: 400, fontSize: 12, color: 'var(--text-tertiary)' }}>(optional)</span></div>
        </div>
        <div className="form-card-body">
          <p style={{ fontSize: 12, color: 'var(--text-tertiary)', marginBottom: 10 }}>Key-value tags</p>
          {Object.entries(newSchemaData.metadata.key_value_tags).map(([key, val]) => (
            <div key={key} style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'center' }}>
              <input className="f-sel" value={key} disabled style={{ flex: 1, height: 30, fontSize: 12 }} />
              <input className="f-sel" value={val as string} disabled style={{ flex: 1, height: 30, fontSize: 12 }} />
              <button type="button" style={{ fontSize: 11, color: '#dc2626', background: 'none', border: 'none', cursor: 'pointer' }}
                onClick={() => {
                  const tags = { ...newSchemaData.metadata.key_value_tags }
                  delete tags[key]
                  setMeta('key_value_tags', tags)
                }}>Remove</button>
            </div>
          ))}
          <div style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
            <input className="f-sel" value={keyValueTag.key} placeholder="Key" style={{ flex: 1, height: 30, fontSize: 12 }} onChange={(e) => setKeyValueTag((t) => ({ ...t, key: e.target.value }))} />
            <input className="f-sel" value={keyValueTag.value} placeholder="Value" style={{ flex: 1, height: 30, fontSize: 12 }} onChange={(e) => setKeyValueTag((t) => ({ ...t, value: e.target.value }))} />
            <button type="button" className="btn-secondary" style={{ height: 30, fontSize: 11 }}
              onClick={() => {
                setMeta('key_value_tags', { ...newSchemaData.metadata.key_value_tags, [keyValueTag.key]: keyValueTag.value })
                setKeyValueTag({ key: '', value: '' })
              }}>Add</button>
          </div>

          <p style={{ fontSize: 12, color: 'var(--text-tertiary)', margin: '16px 0 10px' }}>Key-only tags</p>
          {newSchemaData.metadata.key_only_tags.map((tag) => (
            <div key={tag} style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'center' }}>
              <input className="f-sel" value={tag} disabled style={{ flex: 1, height: 30, fontSize: 12 }} />
              <button type="button" style={{ fontSize: 11, color: '#dc2626', background: 'none', border: 'none', cursor: 'pointer' }}
                onClick={() => setMeta('key_only_tags', newSchemaData.metadata.key_only_tags.filter((t) => t !== tag))}>Remove</button>
            </div>
          ))}
          <div style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
            <input className="f-sel" value={valueTag} placeholder="Tag" style={{ flex: 1, height: 30, fontSize: 12 }} onChange={(e) => setValueTag(e.target.value)} />
            <button type="button" className="btn-secondary" style={{ height: 30, fontSize: 11 }}
              onClick={() => {
                setMeta('key_only_tags', [...newSchemaData.metadata.key_only_tags, valueTag])
                setValueTag('')
              }}>Add</button>
          </div>
        </div>

        <div className="form-actions">
          <button className="btn-primary" type="submit" disabled={isLoading}>
            {isLoading ? 'Creating…' : 'Create Schema'}
          </button>
          {error && <span style={{ fontSize: 12, color: '#dc2626', marginLeft: 8 }}>{error.message}</span>}
        </div>
      </div>
    </form>
  )
}

const thStyle: React.CSSProperties = {
  padding: '7px 12px',
  fontSize: 10,
  fontWeight: 600,
  letterSpacing: '.06em',
  textTransform: 'uppercase',
  color: '#71717a',
  textAlign: 'left'
}

const tdStyle: React.CSSProperties = {
  padding: '8px 12px',
  fontSize: 12
}

export default CreateSchema
