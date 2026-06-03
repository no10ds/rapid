import FormCard from './FormCard/FormCard'
import {
  createSchema,
  updateSchema,
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
import {
  Box,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText,
  Alert,
  AlertTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stack,
  IconButton,
  Link as MuiLink
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'

const dataTypes = [
  'bigint', 'boolean', 'char', 'date', 'decimal', 'double',
  'float', 'int', 'smallint', 'string', 'timestamp', 'tinyint', 'varchar'
]

function CreateSchema({
  schemaData,
  layersData,
  mode = 'create'
}: {
  schemaData: GenerateSchemaResponse
  layersData: string[]
  mode?: 'create' | 'edit'
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
    mutationFn: mode === 'edit' ? updateSchema : createSchema
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
      <Box sx={{ maxWidth: 860, mx: 'auto' }}>
        <Alert severity="success" variant="outlined">
          <AlertTitle sx={{ fontSize: 14, fontWeight: 600 }}>
            {mode === 'edit' ? 'Schema updated — a new version has been created' : 'Dataset added successfully'}
          </AlertTitle>
          <Typography sx={{ fontSize: 13 }}>{data.details}</Typography>
        </Alert>
      </Box>
    )
  }

  const hasDateColumn = newSchemaData.columns.some((c) => c.data_type === 'date')

  return (
    <Box
      component="form"
      sx={{ maxWidth: 860, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}
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
      <FormCard num={1} title="Dataset properties">
        <Stack spacing="18px">
          <Controller
            name="sensitivity"
            control={control}
            defaultValue={newSchemaData.metadata.sensitivity.toUpperCase() as SensitivityEnum}
            render={({ field, fieldState: { error: fe } }) => (
              <FormControl size="small" fullWidth error={!!fe}>
                <InputLabel shrink>Sensitivity Level</InputLabel>
                <Select {...field} label="Sensitivity Level" notched displayEmpty inputProps={{ 'data-testid': 'sensitivity' }}>
                  <MenuItem value="" disabled>Please select</MenuItem>
                  {[...GlobalSensitivities, ProtectedSensitivity].map((v) => (
                    <MenuItem key={v} value={v}>{v}</MenuItem>
                  ))}
                </Select>
                {fe && <FormHelperText>{fe.message}</FormHelperText>}
              </FormControl>
            )}
          />
          <Controller
            name="layer"
            control={control}
            defaultValue={newSchemaData.metadata.layer}
            render={({ field, fieldState: { error: fe } }) => (
              <FormControl size="small" fullWidth error={!!fe}>
                <InputLabel shrink>Dataset Layer</InputLabel>
                <Select {...field} label="Dataset Layer" notched displayEmpty inputProps={{ 'data-testid': 'layer' }}>
                  <MenuItem value="" disabled>Please select</MenuItem>
                  {layersData.map((v) => (
                    <MenuItem key={v} value={v}>{v}</MenuItem>
                  ))}
                </Select>
                {fe && <FormHelperText>{fe.message}</FormHelperText>}
              </FormControl>
            )}
          />
          <Controller
            name="domain"
            control={control}
            defaultValue={newSchemaData.metadata.domain}
            render={({ field, fieldState: { error: fe } }) => (
              <TextField
                {...field}
                size="small"
                fullWidth
                label="Dataset Domain"
                placeholder="showcase"
                InputLabelProps={{ shrink: true }}
                inputProps={{ 'data-testid': 'domain' }}
                error={!!fe}
                helperText={fe?.message}
              />
            )}
          />
          <Controller
            name="title"
            control={control}
            defaultValue={newSchemaData.metadata.dataset}
            render={({ field, fieldState: { error: fe } }) => (
              <TextField
                {...field}
                size="small"
                fullWidth
                label="Dataset Title"
                placeholder="movies"
                InputLabelProps={{ shrink: true }}
                inputProps={{ 'data-testid': 'dataset' }}
                error={!!fe}
                helperText={fe?.message}
              />
            )}
          />
          <Controller
            name="description"
            control={control}
            defaultValue={newSchemaData.metadata.description}
            render={({ field, fieldState: { error: fe } }) => (
              <TextField
                {...field}
                size="small"
                fullWidth
                multiline
                minRows={2}
                label="Dataset Description"
                placeholder="Enter a human readable description of the dataset…"
                InputLabelProps={{ shrink: true }}
                inputProps={{ 'data-testid': 'description' }}
                error={!!fe}
                helperText={fe?.message}
              />
            )}
          />
        </Stack>
      </FormCard>

      <FormCard num={2} title="Validate the data types">
        <Typography sx={{ fontSize: 12, color: 'text.secondary', mb: 1.5 }}>
          Consult the{' '}
          <MuiLink href="https://rapid.readthedocs.io/en/latest/api/schema/" target="_blank" rel="noreferrer">
            schema writing guide
          </MuiLink>{' '}
          for further information.
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Data Type</TableCell>
                {hasDateColumn && <TableCell>Date Format</TableCell>}
                <TableCell>Allows Null</TableCell>
                <TableCell>Is Unique</TableCell>
                <TableCell>Partition Index</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {newSchemaData.columns.map((col) => (
                <TableRow key={col.name}>
                  <TableCell sx={{ fontSize: 12 }}>{col.name}</TableCell>
                  <TableCell>
                    <Select
                      size="small"
                      fullWidth
                      value={col.data_type}
                      onChange={(e) => setCol(col.name, 'data_type', e.target.value)}
                      sx={{ fontSize: 12 }}
                    >
                      {dataTypes.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                    </Select>
                  </TableCell>
                  {hasDateColumn && (
                    <TableCell>
                      {col.data_type === 'date' && (
                        <TextField
                          size="small"
                          fullWidth
                          placeholder="%Y-%m-%d"
                          required
                          inputProps={{ 'data-testid': 'date-format', style: { fontSize: 12 } }}
                          onChange={(e) => setCol(col.name, 'format', e.target.value)}
                        />
                      )}
                    </TableCell>
                  )}
                  <TableCell>
                    <Select
                      size="small"
                      fullWidth
                      value={String(col.allow_null)}
                      onChange={(e) => setCol(col.name, 'allow_null', e.target.value === 'true')}
                      sx={{ fontSize: 12 }}
                    >
                      <MenuItem value="true">true</MenuItem>
                      <MenuItem value="false">false</MenuItem>
                    </Select>
                  </TableCell>
                  <TableCell>
                    <Select
                      size="small"
                      fullWidth
                      value={String(col.unique ?? false)}
                      onChange={(e) => setCol(col.name, 'unique', e.target.value === 'true')}
                      sx={{ fontSize: 12 }}
                    >
                      <MenuItem value="true">true</MenuItem>
                      <MenuItem value="false">false</MenuItem>
                    </Select>
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      fullWidth
                      type="number"
                      value={col.partition_index ?? ''}
                      onChange={(e) => setCol(col.name, 'partition_index', parseInt(e.target.value))}
                      inputProps={{ style: { fontSize: 12 } }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </FormCard>

      <FormCard num={3} title="Set the data owner">
        <Stack spacing="18px">
          <Controller
            name="ownerEmail"
            control={control}
            defaultValue={newSchemaData.metadata.owners[0].email}
            render={({ field, fieldState: { error: fe } }) => (
              <TextField
                {...field}
                size="small"
                fullWidth
                type="email"
                label="Owner Email"
                InputLabelProps={{ shrink: true }}
                error={!!fe}
                helperText={fe?.message}
              />
            )}
          />
          <Controller
            name="ownerName"
            control={control}
            defaultValue={newSchemaData.metadata.owners[0].name}
            render={({ field, fieldState: { error: fe } }) => (
              <TextField
                {...field}
                size="small"
                fullWidth
                label="Owner Name"
                InputLabelProps={{ shrink: true }}
                error={!!fe}
                helperText={fe?.message}
              />
            )}
          />
        </Stack>
      </FormCard>

      <FormCard num={4} title="Set the file upload behaviour">
        <FormControl size="small" fullWidth>
          <InputLabel shrink>Update Behaviour</InputLabel>
          <Select
            label="Update Behaviour"
            notched
            value={newSchemaData.metadata.update_behaviour}
            onChange={(e) => setMeta('update_behaviour', e.target.value)}
          >
            <MenuItem value="APPEND">APPEND</MenuItem>
            <MenuItem value="OVERWRITE">OVERWRITE</MenuItem>
          </Select>
        </FormControl>
      </FormCard>

      <FormCard num={5} title="Tags" optional>
        <Typography sx={{ fontSize: 12, color: 'text.disabled', mb: 1 }}>Key-value tags</Typography>
        <Stack spacing={1}>
          {Object.entries(newSchemaData.metadata.key_value_tags).map(([key, val]) => (
            <Stack key={key} direction="row" spacing={1} alignItems="center">
              <TextField size="small" value={key} disabled fullWidth inputProps={{ style: { fontSize: 12 } }} />
              <TextField size="small" value={val as string} disabled fullWidth inputProps={{ style: { fontSize: 12 } }} />
              <IconButton
                size="small"
                color="error"
                onClick={() => {
                  const tags = { ...newSchemaData.metadata.key_value_tags }
                  delete tags[key]
                  setMeta('key_value_tags', tags)
                }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Stack>
          ))}
          <Stack direction="row" spacing={1} alignItems="center">
            <TextField
              size="small"
              fullWidth
              value={keyValueTag.key}
              placeholder="Key"
              onChange={(e) => setKeyValueTag((t) => ({ ...t, key: e.target.value }))}
              inputProps={{ style: { fontSize: 12 } }}
            />
            <TextField
              size="small"
              fullWidth
              value={keyValueTag.value}
              placeholder="Value"
              onChange={(e) => setKeyValueTag((t) => ({ ...t, value: e.target.value }))}
              inputProps={{ style: { fontSize: 12 } }}
            />
            <Button
              type="button"
              size="small"
              variant="outlined"
              onClick={() => {
                setMeta('key_value_tags', { ...newSchemaData.metadata.key_value_tags, [keyValueTag.key]: keyValueTag.value })
                setKeyValueTag({ key: '', value: '' })
              }}
            >
              Add
            </Button>
          </Stack>
        </Stack>

        <Typography sx={{ fontSize: 12, color: 'text.disabled', mt: 2.5, mb: 1 }}>Key-only tags</Typography>
        <Stack spacing={1}>
          {newSchemaData.metadata.key_only_tags.map((tag) => (
            <Stack key={tag} direction="row" spacing={1} alignItems="center">
              <TextField size="small" value={tag} disabled fullWidth inputProps={{ style: { fontSize: 12 } }} />
              <IconButton
                size="small"
                color="error"
                onClick={() => setMeta('key_only_tags', newSchemaData.metadata.key_only_tags.filter((t) => t !== tag))}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Stack>
          ))}
          <Stack direction="row" spacing={1} alignItems="center">
            <TextField
              size="small"
              fullWidth
              value={valueTag}
              placeholder="Tag"
              onChange={(e) => setValueTag(e.target.value)}
              inputProps={{ style: { fontSize: 12 } }}
            />
            <Button
              type="button"
              size="small"
              variant="outlined"
              onClick={() => {
                setMeta('key_only_tags', [...newSchemaData.metadata.key_only_tags, valueTag])
                setValueTag('')
              }}
            >
              Add
            </Button>
          </Stack>
        </Stack>
      </FormCard>

      <Stack direction="row" spacing={2} alignItems="center" sx={{ pt: 1 }}>
        <Button type="submit" variant="contained" disabled={isLoading}>
          {isLoading
            ? (mode === 'edit' ? 'Saving…' : 'Adding…')
            : (mode === 'edit' ? 'Update Schema' : 'Add Dataset')}
        </Button>
        {error && (
          <Typography sx={{ fontSize: 12, color: 'error.main' }}>{error.message}</Typography>
        )}
      </Stack>
    </Box>
  )
}

export default CreateSchema
