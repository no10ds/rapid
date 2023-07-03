import { z } from 'zod'

export const SensitivityEnum = z.enum(['PUBLIC', 'PRIVATE', 'PROTECTED'])
const UserTypeEnum = z.enum(['User', 'Client'])

export const SubjectCreate = z.object({
  type: UserTypeEnum,
  email: z.string().email().optional(),
  name: z.string(),
  permissions: z.array(z.string()).optional()
})

export const schemaCreateSchema = z.object({
  sensitivity: SensitivityEnum,
  domain: z.string(),
  title: z.string(),
  description: z.string().optional(),
  ownerEmail: z
    .string()
    .email()
    .refine((arg) => !(arg === 'change_me@email.com'), { message: 'Change Required' }),
  ownerName: z
    .string()
    .refine((arg) => !(arg === 'change_me'), { message: 'Change Required' })
})

export const schemaGenerateSchema = z.object({
  sensitivity: SensitivityEnum,
  domain: z.string(),
  title: z.string()
})
