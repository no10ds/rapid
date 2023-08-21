import { z } from 'zod'
import { PermissionUiResponse } from './types'
import { Permission, DataPermission } from '@/service'

type DataPermissionType = z.infer<typeof DataPermission>
type PermissionType = z.infer<typeof Permission>

export const isDataPermission = (permission: PermissionType): boolean => {
    return permission.type === "READ" || permission.type === "WRITE";
}

export const isAdminPermission = (permission: PermissionType): boolean => {
    return permission.type === "DATA_ADMIN" || permission.type === "USER_ADMIN";
}

export const extractPermissionNames = (permission: PermissionType, permissionsListData: PermissionUiResponse) => {
    switch (true) {
        case isDataPermission(permission):
            permission = permission as DataPermissionType
            if (permission.domain != undefined) {
                return permissionsListData[permission.type][permission.layer][permission.sensitivity][permission.domain]
            }
            else if (permission.sensitivity != undefined) {
                return permissionsListData[permission.type][permission.layer][permission.sensitivity]
            }
        case isAdminPermission(permission):
            return permissionsListData[permission.type]
    }
}