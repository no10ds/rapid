import {
  Row,
  AccountLayout,
  Card,
  Select,
  TextField,
  Button,
  Alert,
  CreateSchema as CreateSchemaComponent
} from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { generateSchema, schemaGenerateSchema, GlobalSensitivities, ProtectedSensitivity } from '@/service'
import { getLayers } from '@/service/fetch'
import { GenerateSchemaResponse, SchemaGenerate } from '@/service/types'
import { zodResolver } from '@hookform/resolvers/zod'
import { LinearProgress, Typography } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'

function CreateSchema() {
  const [file, setFile] = useState<File | undefined>()

  const { isLoading: isLayersLoading, data: layersData, error: layersError } = useQuery(
    ['layers'],
    getLayers,
  )

  const { control, handleSubmit } = useForm<SchemaGenerate>({
    resolver: zodResolver(schemaGenerateSchema)
  })

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
    return <LinearProgress />
  }

  if (layersError) {
    return <ErrorCard error={layersError as Error} />
  }


  return (
    <form
      onSubmit={handleSubmit(async (data) => {
        const formData = new FormData()
        formData.append('file', file)
        const path = `${data.layer}/${data.sensitivity}/${data.domain}/${data.title}/generate`
        await mutate({ path, data: formData })
      })}
    >
      <Card
        action={
          <Button color="primary" type="submit" loading={isLoading} data-testid="submit">
            Generate Schema
          </Button>
        }
      >
        <Typography variant="h2" gutterBottom>
          Populate dataset properties for the new schema:
        </Typography>

        <Row>
          <Controller
            name="sensitivity"
            control={control}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Sensitivity Level</Typography>
                <Select
                  {...field}
                  defaultValue=""
                  native
                  error={!!error}
                  helperText={error?.message}
                  inputProps={{ 'data-testid': 'field-level' }}
                >
                  <option value="" disabled>
                    Please select
                  </option>
                  {[...GlobalSensitivities, ProtectedSensitivity].map((value) => (
                    <option key={value}>{value}</option>
                  ))}
                </Select>
              </>
            )}
          />
        </Row>
        <Row>
          <Controller
            name="layer"
            control={control}
            defaultValue={layersData.length === 1 ? layersData[0] : ""}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Dataset Layer</Typography>
                <Select
                  {...field}
                  native
                  error={!!error}
                  helperText={error?.message}
                  inputProps={{ 'data-testid': 'field-layer' }}
                >
                  <option value="" disabled>
                    Please select
                  </option>
                  {layersData.map((value) => (
                    <option key={value}>{value}</option>
                  ))}
                </Select>
              </>
            )}
          />
        </Row>

        <Row>
          <Controller
            name="domain"
            control={control}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Dataset Domain</Typography>
                <TextField
                  {...field}
                  fullWidth
                  size="small"
                  variant="outlined"
                  placeholder="showcase"
                  error={!!error}
                  helperText={error?.message}
                  inputProps={{ 'data-testid': 'field-domain' }}
                />{' '}
              </>
            )}
          />
        </Row>

        <Row>
          <Controller
            name="title"
            control={control}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Dataset Title</Typography>
                <TextField
                  {...field}
                  fullWidth
                  size="small"
                  variant="outlined"
                  placeholder="movies"
                  error={!!error}
                  helperText={error?.message}
                  inputProps={{ 'data-testid': 'field-title' }}
                />
              </>
            )}
          />
        </Row>

        <Typography variant="h2" gutterBottom>
          Upload the data to generate the schema for
        </Typography>

        <Row>
          <input
            name="file"
            id="file"
            type="file"
            data-testid="field-file"
            onChange={(event) => setFile(event.target.files[0])}
          />
        </Row>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error?.message}
          </Alert>
        )}
      </Card>
    </form>
  )
}

export default CreateSchema

CreateSchema.getLayout = (page) => (
  <AccountLayout title="Create Schema">{page}</AccountLayout>
)
