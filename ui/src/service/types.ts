import { z } from 'zod'
import {
  schemaCreateSchema,
  schemaGenerateSchema,
  SensitivityEnum as schemaSensitivityEnum
} from './schema'

export type SchemaCreate = z.infer<typeof schemaCreateSchema>
export type SchemaGenerate = z.infer<typeof schemaGenerateSchema>

export type DataFormats = 'csv' | 'json'
export type SensitivityEnum = z.infer<typeof schemaSensitivityEnum>

export type ClientCreateBody = {
  client_name: string
  permissions: string[]
}

export type ClientCreateResponse = {
  client_id: string
  client_name: string
  client_secret: string
  permissions: string[]
}

export type UserCreateBody = {
  username: string
  email: string
  permissions: string[]
}

export type UserCreateResponse = {
  username: string
  user_id: string
  email: string
  permissions: string[]
}

export type FilteredSubjectList = {
  ClientApps: {
    subjectId: string
    subjectName: string
  }[]
  Users: {
    subjectId: string
    subjectName
  }[]
}

export type UpdateSubjectPermissionsResponse = {
  subject_id: string
  permissions: string[]
}

export type UpdateSubjectPermissionsBody = {
  subject_id: string
  permissions: string[]
}

export type UploadDatasetResponseDetails = {
  dataset_version: number
  job_id: string
  original_filename: string
  raw_filename: string
  status: string
}

export type UploadDatasetResponse = {
  details: UploadDatasetResponseDetails
}

export type DeleteDatasetResponse = {
  details: string
}

export type DatasetInfoResponse = {
  metadata: {
    domain: string
    dataset: string
    sensitivity: string
    description?: string
    version?: number
    key_value_tags: { [key: string]: string }
    key_only_tags: string[]
    owners?: { name: string; email: string }[]
    update_behaviour: 'APPEND'
    number_of_columns: number
    number_of_rows: number
    last_updated: string
  }
  columns: {
    name: string
    partition_index?: number
    data_type: string
    allow_null: boolean
    format?: string
    statistics?: { [key: string]: string }
  }[]
}

export type GenerateSchemaResponse = {
  metadata: {
    layer: string
    domain: string
    dataset: string
    sensitivity: string
    description?: string
    update_behaviour: string
    key_value_tags: { [key: string]: string }
    key_only_tags: string[]
    owners?: { name: string; email: string }[]
  }
  columns: {
    name: string
    partition_index?: number
    data_type: string
    allow_null: boolean
    format?: string
  }[]
}

export type CreateSchemaResponse = {
  details: string
}

// TODO Probably want to type this better
export type JobResponse = { [key: string]: string | number | string[] }
export type AllJobsResponse = JobResponse[]

export type MethodsResponse = {
  message: string | null
  can_manage_users?: boolean
  can_upload?: boolean
  can_download?: boolean
  can_create_schema: boolean
  can_search_catalog: boolean
}

export type AuthResponse = {
  detail: string
}

export type GetLoginResponse = {
  auth_url: string
}

export type MetadataItem = {
  dataset: string
  domain: string
  data: string
  version: string
  data_type: 'column_name' | 'data_name' | 'description'
}

export type MetadataSearchResponse = MetadataItem[]

export type Dataset = {
  layer: string
  domain: string
  dataset: string
  version: number
}

export type SubjectPermission = {
  name: string
  type: string
  layer: string | undefined
  sensitivity: string | undefined
  domain: string | undefined
}

export type PermissionUiResponse = {
  [key: string]: string | { [key: string]: { [key: string]: string | { [key: string]: string } } }
}