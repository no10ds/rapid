import { AccountLayout, FormCard } from '@/components'
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
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  TextField,
  Select,
  FormControl,
  InputLabel,
  FormHelperText
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'

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
    return <LinearProgress color="primary" role="progressbar" />
  }

  if (layersError) {
    return <ErrorCard error={layersError as Error} />
  }

  return (
    <Box
      component="form"
      sx={{ maxWidth: 860, mx: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}
      onSubmit={handleSubmit(async (data: SchemaGenerate) => {
        const formData = new FormData()
        formData.append('file', file)
        const path = `${data.layer}/${data.sensitivity}/${data.domain}/${data.title}/generate`
        await mutate({ path, data: formData })
      })}
    >
      <FormCard num={1} title="Dataset properties">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Controller
            name="sensitivity"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <FormControl size="small" error={!!fieldError} fullWidth>
                <InputLabel htmlFor="field-level" shrink>Sensitivity Level</InputLabel>
                <Select
                  {...field}
                  native
                  label="Sensitivity Level"
                  notched
                  inputProps={{ 'data-testid': 'field-level', id: 'field-level' }}
                >
                  <option value="" disabled>Please select</option>
                  {[...GlobalSensitivities, ProtectedSensitivity].map((value) => (
                    <option key={value} value={value}>{value}</option>
                  ))}
                </Select>
                {fieldError && <FormHelperText>{fieldError.message}</FormHelperText>}
              </FormControl>
            )}
          />

          <Controller
            name="layer"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <FormControl size="small" error={!!fieldError} fullWidth>
                <InputLabel htmlFor="field-layer" shrink>Dataset Layer</InputLabel>
                <Select
                  {...field}
                  native
                  label="Dataset Layer"
                  notched
                  inputProps={{ 'data-testid': 'field-layer', id: 'field-layer' }}
                >
                  <option value="" disabled>Please select</option>
                  {layersData.map((value) => (
                    <option key={value} value={value}>{value}</option>
                  ))}
                </Select>
                {fieldError && <FormHelperText>{fieldError.message}</FormHelperText>}
              </FormControl>
            )}
          />

          <Controller
            name="domain"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <TextField
                {...field}
                size="small"
                label="Dataset Domain"
                placeholder="showcase"
                error={!!fieldError}
                helperText={fieldError?.message}
                inputProps={{ 'data-testid': 'field-domain', id: 'field-domain' }}
                InputLabelProps={{ shrink: true }}
              />
            )}
          />

          <Controller
            name="title"
            control={control}
            render={({ field, fieldState: { error: fieldError } }) => (
              <TextField
                {...field}
                size="small"
                label="Dataset Title"
                placeholder="movies"
                error={!!fieldError}
                helperText={fieldError?.message}
                inputProps={{ 'data-testid': 'field-title', id: 'field-title' }}
                InputLabelProps={{ shrink: true }}
              />
            )}
          />
        </Box>
      </FormCard>

      <FormCard
        num={2}
        title="Upload sample data"
        actionsError={error}
        actions={
          <Button
            variant="contained"
            type="submit"
            data-testid="submit"
            disabled={isLoading || !file}
          >
            {isLoading ? 'Detecting…' : 'Next'}
          </Button>
        }
      >
        <Typography variant="body2" sx={{ fontSize: 12, mb: 2 }}>
          Upload a sample CSV file so we can detect the column types automatically.
        </Typography>

        {!file && (
          <Box
            component="label"
            htmlFor="schema-file"
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 1,
              p: 4,
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 1,
              cursor: 'pointer',
              bgcolor: 'background.default',
              '&:hover': { borderColor: 'primary.main' }
            }}
          >
            <CloudUploadIcon sx={{ fontSize: 32, color: 'text.disabled' }} />
            <Typography sx={{ fontSize: 13, fontWeight: 500 }}>Click to browse or drag &amp; drop</Typography>
            <Typography sx={{ fontSize: 11, color: 'text.disabled' }}>CSV file only</Typography>
          </Box>
        )}

        {file && (
          <Typography sx={{ fontSize: 12, color: 'primary.main', fontWeight: 500 }}>
            {file.name}
          </Typography>
        )}

        <input
          name="file"
          id="schema-file"
          type="file"
          data-testid="field-file"
          style={{ display: 'none' }}
          onChange={(event) => setFile(event.target.files[0])}
        />
      </FormCard>
    </Box>
  )
}

export default CreateSchema

CreateSchema.getLayout = (page: ReactNode) => (
  <AccountLayout title="Add New Dataset">{page}</AccountLayout>
)
