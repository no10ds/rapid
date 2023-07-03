import { createSchema, schemaCreateSchema } from '@/service'
import {
  CreateSchemaResponse,
  GenerateSchemaResponse,
  SchemaCreate,
  SensitivityEnum
} from '@/service/types'
import { zodResolver } from '@hookform/resolvers/zod'
import { Box, FormControl, Link, Typography } from '@mui/material'
import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import Alert from './Alert/Alert'
import Button from './Button/Button'
import Card from './Card/Card'
import Row from './Row'
import Select from './Select/Select'
import SimpleTable from './SimpleTable/SimpleTable'
import TextField from './TextField/TextField'

const dataTypes = ['Int64', 'Float64', 'object', 'date', 'boolean']

function CreateSchema({ schemaData }: { schemaData: GenerateSchemaResponse }) {
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

  const setNewSchemaDataMetadata = (key, value) => {
    setNewSchemaData({
      ...newSchemaData,
      metadata: {
        ...newSchemaData.metadata,
        [key]: value
      }
    })
  }

  const setNewSchemaDataColumn = (name, key, value) => {
    const newColumns = newSchemaData.columns.map((col) => {
      if (col.name === name) {
        return {
          ...col,
          [key]: value
        }
      }
      return col
    })
    setNewSchemaData({
      ...newSchemaData,
      columns: newColumns
    })
  }

  if (isSuccess) {
    return (
      <Card>
        <Alert severity="success" sx={{ mb: 3 }} title="Schema Created">
          <Typography variant="body2">{data.details}</Typography>
        </Alert>
      </Card>
    )
  }

  return (
    <form
      onSubmit={handleSubmit(async (_data) => {
        const data = { ...newSchemaData }
        data.metadata.owners = [{ email: _data.ownerEmail, name: _data.ownerName }]
        data.metadata.sensitivity = _data.sensitivity
        data.metadata.domain = _data.domain
        data.metadata.dataset = _data.title
        data.metadata.description = _data.description
        await mutate(data)
      })}
    >
      <Card
        action={
          <Button color="primary" type="submit" loading={isLoading}>
            Create Schema
          </Button>
        }
      >
        <Row>
          <Controller
            name="sensitivity"
            control={control}
            defaultValue={
              newSchemaData.metadata.sensitivity.toUpperCase() as SensitivityEnum
            }
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Sensitivity Level</Typography>
                <Select
                  {...field}
                  data={['PUBLIC', 'PRIVATE', 'PROTECTED']}
                  error={!!error}
                  helperText={error?.message}
                  onChange={(e) => field.onChange(e.target.value)}
                />
              </>
            )}
          />
        </Row>

        <Row>
          <Controller
            name="domain"
            control={control}
            defaultValue={newSchemaData.metadata.domain}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Dataset Domain</Typography>
                <TextField
                  {...field}
                  fullWidth
                  size="small"
                  variant="outlined"
                  error={!!error}
                  helperText={error?.message}
                  onChange={(e) => field.onChange(e.target.value)}
                />
              </>
            )}
          />
        </Row>

        <Row>
          <Controller
            name="title"
            control={control}
            defaultValue={newSchemaData.metadata.dataset}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Dataset Title</Typography>
                <TextField
                  {...field}
                  fullWidth
                  size="small"
                  variant="outlined"
                  error={!!error}
                  helperText={error?.message}
                  onChange={(e) => field.onChange(e.target.value)}
                />
              </>
            )}
          />
        </Row>

        <Row>
          <Controller
            name="description"
            control={control}
            defaultValue={newSchemaData.metadata.description}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Dataset Description</Typography>
                <TextField
                  {...field}
                  fullWidth
                  multiline
                  rows={2}
                  size="small"
                  variant="outlined"
                  error={!!error}
                  helperText={error?.message}
                  placeholder="Enter a human readable descriptive to describe the dataset..."
                  onChange={(e) => field.onChange(e.target.value)}
                />
              </>
            )}
          />
        </Row>

        <Typography variant="h2" gutterBottom>
          Validate the data types for the schema
        </Typography>

        <Typography gutterBottom>
          Consult the{' '}
          <Link
            href="https://github.com/no10ds/rapid-api/blob/main/docs/guides/usage/schema_creation.md"
            target="_blank"
          >
            schema writing guide
          </Link>{' '}
          for further information.
        </Typography>

        <SimpleTable
          sx={{ mb: 4 }}
          list={newSchemaData.columns.map((item) => {
            return [
              { children: item.name },
              {
                children: (
                  <FormControl fullWidth size="small">
                    <Select
                      label="Data Type"
                      data={dataTypes}
                      value={item.data_type}
                      onChange={(e) =>
                        setNewSchemaDataColumn(item.name, 'data_type', e.target.value)
                      }
                    />
                  </FormControl>
                )
              },
              {
                children: (
                  <FormControl fullWidth size="small">
                    <Select
                      label="Allows Null"
                      data={['true', 'false']}
                      value={item.allow_null}
                      onChange={(e) =>
                        setNewSchemaDataColumn(
                          item.name,
                          'allow_null',
                          e.target.value === 'true'
                        )
                      }
                    />
                  </FormControl>
                )
              },
              {
                children: (
                  <TextField
                    size="small"
                    variant="outlined"
                    value={item.partition_index}
                    type="number"
                    onChange={(e) =>
                      setNewSchemaDataColumn(
                        item.name,
                        'partition_index',
                        parseInt(e.target.value)
                      )
                    }
                  />
                )
              }
            ]
          })}
          headers={[
            { children: 'Name' },
            { children: 'Data Type' },
            { children: 'Allows Null' },
            { children: 'Partition Index (Optional)' }
          ]}
        />

        <Typography variant="h2" gutterBottom>
          Set the data owner
        </Typography>

        <Row>
          <Controller
            name="ownerEmail"
            control={control}
            defaultValue={newSchemaData.metadata.owners[0].email}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Owner Email</Typography>
                <TextField
                  {...field}
                  size="small"
                  type="email"
                  variant="outlined"
                  helperText={error?.message}
                  error={!!error}
                  onChange={(e) => field.onChange(e.target.value)}
                  fullWidth
                />
              </>
            )}
          />
        </Row>

        <Row>
          <Controller
            name="ownerName"
            control={control}
            defaultValue={newSchemaData.metadata.owners[0].name}
            render={({ field, fieldState: { error } }) => (
              <>
                <Typography variant="caption">Owner Name</Typography>
                <TextField
                  {...field}
                  size="small"
                  variant="outlined"
                  helperText={error?.message}
                  error={!!error}
                  onChange={(e) => field.onChange(e.target.value)}
                  fullWidth
                />
              </>
            )}
          />
        </Row>

        <Typography variant="h2" gutterBottom>
          Set the file upload behaviour
        </Typography>

        <Row>
          <FormControl fullWidth size="small">
            <Typography variant="caption">Update Behaviour</Typography>
            <Select
              data={['APPEND', 'OVERWRITE']}
              value={newSchemaData.metadata.update_behaviour}
              onChange={(e) =>
                setNewSchemaDataMetadata('update_behaviour', e.target.value)
              }
            />
          </FormControl>
        </Row>

        <Typography variant="h2" gutterBottom>
          Optionally set key value tags
        </Typography>

        {Object.keys(newSchemaData.metadata.key_value_tags).map((key) => (
          <Box key={key} sx={{ display: 'flex', gap: 3, mb: 1 }}>
            <TextField value={key} size="small" variant="outlined" fullWidth disabled />
            <TextField
              value={newSchemaData.metadata.key_value_tags[key]}
              size="small"
              variant="outlined"
              fullWidth
              disabled
            />
            <Button
              color="inherit"
              variant="text"
              onClick={() => {
                const keyValueTags = { ...newSchemaData.metadata.key_value_tags }
                delete keyValueTags[key]
                setNewSchemaDataMetadata('key_value_tags', keyValueTags)
              }}
              disableTouchRipple
            >
              Remove
            </Button>
          </Box>
        ))}

        <Box sx={{ display: 'flex', gap: 3, mb: 1 }}>
          <TextField
            value={keyValueTag.key}
            onChange={(e) => setKeyValueTag({ ...keyValueTag, key: e.target.value })}
            size="small"
            variant="outlined"
            fullWidth
          />
          <TextField
            value={keyValueTag.value}
            onChange={(e) => setKeyValueTag({ ...keyValueTag, value: e.target.value })}
            size="small"
            variant="outlined"
            fullWidth
          />
          <Button
            color="secondary"
            variant="text"
            onClick={() => {
              setNewSchemaDataMetadata('key_value_tags', {
                ...newSchemaData.metadata.key_value_tags,
                [keyValueTag.key]: keyValueTag.value
              })
              setKeyValueTag({ key: '', value: '' })
            }}
            disableTouchRipple
          >
            Add
          </Button>
        </Box>

        <Typography variant="h2" gutterBottom>
          Optionally set key only tags
        </Typography>

        {newSchemaData.metadata.key_only_tags.map((tag) => (
          <Box key={tag} sx={{ display: 'flex', gap: 3, mb: 1 }}>
            <TextField value={tag} size="small" variant="outlined" fullWidth disabled />
            <Button
              color="inherit"
              variant="text"
              onClick={() => {
                const valueTags = [...newSchemaData.metadata.key_only_tags]
                setNewSchemaDataMetadata(
                  'key_only_tags',
                  valueTags.filter((item) => item !== tag)
                )
              }}
            >
              Remove
            </Button>
          </Box>
        ))}

        <Box sx={{ display: 'flex', gap: 3, mb: 1 }}>
          <TextField
            value={valueTag}
            onChange={(e) => setValueTag(e.target.value)}
            size="small"
            variant="outlined"
            fullWidth
          />
          <Button
            color="secondary"
            variant="text"
            onClick={() => {
              setNewSchemaDataMetadata('key_only_tags', [
                ...newSchemaData.metadata.key_only_tags,
                valueTag
              ])
              setValueTag('')
            }}
            disableTouchRipple
          >
            Add
          </Button>
        </Box>

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
