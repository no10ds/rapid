locals {
  layer_permissions = concat([for layer in var.layers : upper(layer)], ["ALL"])
  data_permissions = merge(var.master_data_permissions, flatten([
    for action in var.data_actions : flatten([
      for layer in local.layer_permissions : [
        for sensitivity in var.global_data_sensitivities :
        {
          "${action}_${layer}_${sensitivity}" = {
            type        = action
            sensitivity = sensitivity
            layer       = layer
          }
        }
      ]
    ])
  ])...)
}
