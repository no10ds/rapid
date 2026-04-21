import { AccountLayout, Alert, Button } from '@/components'
import ErrorCard from '@/components/ErrorCard/ErrorCard'
import { getDatasetsUi, deleteDataset, getMethods } from '@/service'
import { Dataset } from '@/service/types'
import {
  Box,
  Checkbox,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/router'
import { useMemo, useState } from 'react'

function buildDownloadUrl(dataset: Dataset): string {
  const params = new URLSearchParams({
    layer: dataset.layer,
    domain: dataset.domain,
    dataset: dataset.dataset,
    version: String(dataset.version)
  })
  return `/data/download/?${params.toString()}`
}

function CatalogPage() {
  const router = useRouter()

  const [searchTerm, setSearchTerm] = useState('')
  const [domainFilter, setDomainFilter] = useState<string>('')
  const [selectedDatasets, setSelectedDatasets] = useState<Set<string>>(new Set())
  const [deleteTarget, setDeleteTarget] = useState<Dataset | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const {
    isLoading: isDatasetsLoading,
    data: datasets,
    error: datasetsError,
    refetch: refetchDatasets
  } = useQuery(['datasetsList', 'READ'], getDatasetsUi)

  const { data: methods, isLoading: isMethodsLoading } = useQuery(['methods'], getMethods)

  const { mutate: doDelete, isLoading: isDeleting } = useMutation(deleteDataset, {
    onSuccess: () => {
      setDeleteTarget(null)
      setDeleteError(null)
      refetchDatasets()
    },
    onError: (err: Error) => {
      setDeleteError(err?.message ?? 'Failed to delete dataset')
    }
  })

  const canDelete = methods?.can_create_schema === true

  const allDomains = useMemo<string[]>(() => {
    if (!datasets) return []
    return Array.from(new Set(datasets.map((d) => d.domain))).sort()
  }, [datasets])

  const filteredDatasets = useMemo<Dataset[]>(() => {
    if (!datasets) return []
    return datasets.filter((d) => {
      const matchesSearch =
        searchTerm.trim() === '' ||
        d.dataset.toLowerCase().includes(searchTerm.trim().toLowerCase())
      const matchesDomain = domainFilter === '' || d.domain === domainFilter
      return matchesSearch && matchesDomain
    })
  }, [datasets, searchTerm, domainFilter])

  function rowKey(d: Dataset): string {
    return `${d.layer}/${d.domain}/${d.dataset}/${d.version}`
  }

  const allVisibleSelected =
    filteredDatasets.length > 0 &&
    filteredDatasets.every((d) => selectedDatasets.has(rowKey(d)))

  const someVisibleSelected =
    filteredDatasets.some((d) => selectedDatasets.has(rowKey(d))) && !allVisibleSelected

  function handleSelectAll(checked: boolean) {
    setSelectedDatasets((prev) => {
      const next = new Set(prev)
      for (const d of filteredDatasets) {
        if (checked) {
          next.add(rowKey(d))
        } else {
          next.delete(rowKey(d))
        }
      }
      return next
    })
  }

  function handleSelectRow(d: Dataset, checked: boolean) {
    const key = rowKey(d)
    setSelectedDatasets((prev) => {
      const next = new Set(prev)
      if (checked) {
        next.add(key)
      } else {
        next.delete(key)
      }
      return next
    })
  }

  const selectedCount = filteredDatasets.filter((d) => selectedDatasets.has(rowKey(d))).length

  function handleBulkDownload() {
    const toDownload = filteredDatasets.filter((d) => selectedDatasets.has(rowKey(d)))
    if (toDownload.length === 0) return
    router.push(buildDownloadUrl(toDownload[0]))
  }

  function handleDownloadSingle(d: Dataset) {
    router.push(buildDownloadUrl(d))
  }

  function handleDeleteClick(d: Dataset) {
    setDeleteError(null)
    setDeleteTarget(d)
  }

  function handleDeleteConfirm() {
    if (!deleteTarget) return
    const path = `${deleteTarget.layer}/${deleteTarget.domain}/${deleteTarget.dataset}`
    doDelete({ path })
  }

  function handleDeleteCancel() {
    setDeleteTarget(null)
    setDeleteError(null)
  }

  if (isDatasetsLoading || isMethodsLoading) {
    return <LinearProgress />
  }

  if (datasetsError) {
    return <ErrorCard error={datasetsError as Error} />
  }

  return (
    <Box>
      <Typography variant="h2" gutterBottom>
        Data Catalog
      </Typography>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <TextField
          label="Search by dataset title"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ minWidth: 280 }}
          inputProps={{ 'data-testid': 'catalog-search' }}
        />
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="domain-filter-label">Filter by domain</InputLabel>
          <Select
            labelId="domain-filter-label"
            value={domainFilter}
            label="Filter by domain"
            onChange={(e) => setDomainFilter(e.target.value as string)}
            inputProps={{ 'data-testid': 'domain-filter' }}
          >
            <MenuItem value="">
              <em>All domains</em>
            </MenuItem>
            {allDomains.map((domain) => (
              <MenuItem key={domain} value={domain}>
                {domain}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        {domainFilter && (
          <Chip
            label={`Domain: ${domainFilter}`}
            onDelete={() => setDomainFilter('')}
            size="small"
          />
        )}
      </Box>

      {/* Bulk download bar */}
      {selectedCount > 0 && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            mb: 2,
            p: 1.5,
            bgcolor: 'primary.light',
            borderRadius: 1
          }}
        >
          <Typography variant="body2" sx={{ color: 'primary.contrastText' }}>
            {selectedCount} dataset{selectedCount > 1 ? 's' : ''} selected
          </Typography>
          <Button
            color="primary"
            size="small"
            onClick={handleBulkDownload}
            data-testid="bulk-download-btn"
          >
            Download Selected
          </Button>
        </Box>
      )}

      {/* Dataset table */}
      {filteredDatasets.length === 0 ? (
        <Typography variant="body1" sx={{ mt: 2 }}>
          No datasets found{searchTerm || domainFilter ? ' matching the current filters' : ''}.
        </Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small" data-testid="datasets-table">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={someVisibleSelected}
                    checked={allVisibleSelected}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    inputProps={{ 'aria-label': 'select all datasets' }}
                    data-testid="select-all-checkbox"
                  />
                </TableCell>
                <TableCell>Layer</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Dataset</TableCell>
                <TableCell>Version</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredDatasets.map((d) => {
                const key = rowKey(d)
                const isSelected = selectedDatasets.has(key)
                return (
                  <TableRow
                    key={key}
                    selected={isSelected}
                    hover
                    data-testid={`dataset-row-${key}`}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isSelected}
                        onChange={(e) => handleSelectRow(d, e.target.checked)}
                        inputProps={{ 'aria-label': `select ${d.dataset}` }}
                      />
                    </TableCell>
                    <TableCell>{d.layer}</TableCell>
                    <TableCell>{d.domain}</TableCell>
                    <TableCell>{d.dataset}</TableCell>
                    <TableCell>{d.version}</TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 0.5 }}>
                        <Tooltip title="Download">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => handleDownloadSingle(d)}
                            data-testid={`download-btn-${key}`}
                            aria-label={`Download ${d.dataset}`}
                          >
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {canDelete && (
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteClick(d)}
                              data-testid={`delete-btn-${key}`}
                              aria-label={`Delete ${d.dataset}`}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteTarget !== null}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        data-testid="delete-dialog"
      >
        <DialogTitle id="delete-dialog-title">Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the dataset{' '}
            <strong>
              {deleteTarget
                ? `${deleteTarget.domain} / ${deleteTarget.dataset} (v${deleteTarget.version})`
                : ''}
            </strong>
            ? This action cannot be undone.
          </DialogContentText>
          {deleteError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {deleteError}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            color="inherit"
            onClick={handleDeleteCancel}
            disabled={isDeleting}
            data-testid="delete-cancel-btn"
          >
            Cancel
          </Button>
          <Button
            color="error"
            onClick={handleDeleteConfirm}
            loading={isDeleting}
            data-testid="delete-confirm-btn"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default CatalogPage

CatalogPage.getLayout = (page) => (
  <AccountLayout title="Data Catalog">{page}</AccountLayout>
)
