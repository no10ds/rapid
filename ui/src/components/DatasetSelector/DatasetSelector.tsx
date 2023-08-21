
import { Row } from '@/components'
import { TextField, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { Autocomplete, GroupHeader, GroupItems } from '../Autocomplete/Autocomplete'
import FormControl from '../FormControl/FormControl'
import { Dataset } from "@/service/types"


const DatasetSelector = ({ datasetsList, setParentDataset, enableVersionSelector = true }) => {

  const [maxVersion, setMaxVersion] = useState(0)
  const [filteredDatasetsList, setFilteredDatasetsList] = useState<Dataset[]>([])
  const [layerFilteredDatasetsList, setLayerFilteredDatasetsList] = useState<Dataset[]>([])
  const [layer, setLayer] = useState<string>('')
  const [domain, setDomain] = useState<string>('')
  const [dataset, setDataset] = useState<Dataset>(null)
  const [version, setVersion] = useState<number>(1)

  useEffect(() => {
    if (datasetsList) {
      let filteredList = datasetsList;
      if (layer) {
        filteredList = filteredList.filter((dataset) => dataset.layer === layer);

        if (domain) {
          filteredList = filteredList.filter((dataset) => dataset.domain === domain);
        }
      }
      setFilteredDatasetsList(filteredList);
      setLayerFilteredDatasetsList(filteredList);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [layer, domain])

  useEffect(() => {
    if (datasetsList) {
      setFilteredDatasetsList(datasetsList)
      setLayerFilteredDatasetsList(datasetsList)
    }
  }, [datasetsList])

  const handleDomainSelect = (value) => {
    if (value) {
      const splits = value.split('/')
      const layer = splits[0]
      const domain = splits[1]
      setLayer(layer)
      setDomain(domain)
    }
    else {
      setDomain(null)
    }
    setDataset(null)
  }

  const handleLayerSelect = (value) => {
    if (value) { setLayer(value); setDomain(null) }
    else { setLayer(null), setDataset(null), setDataset(null) }
  }

  useEffect(() => {
    let version = 0
    if (dataset) {
      version = dataset.version
      setLayer(dataset.layer)
      setDomain(dataset.domain)
    }
    else {
      setLayer(null)
      setDomain(null)
    }

    setVersion(version)
    setMaxVersion(version)
    setParentDataset(dataset)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataset])


  useEffect(() => {
    if (dataset) {
      dataset.version = version
      setParentDataset(dataset)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [version])

  const getUniqueLayers = () => [...new Set(datasetsList.map((dataset) => dataset.layer))]
  const getUniqueDomains = () => [...new Set(layerFilteredDatasetsList.map((dataset) => `${dataset.layer}/${dataset.domain}`))]

  return (
    <>
      <Row>
        <Typography variant="caption">Layer</Typography>
        <FormControl fullWidth sx={{ m: 1 }}>
          <Autocomplete
            multiple={false}
            options={getUniqueLayers()}
            getOptionLabel={(option) => (option as string) || ""}
            renderInput={(params) => <TextField {...params} size="small" />}
            value={getUniqueLayers().length === 1 ? datasetsList[0].layer : layer || null}
            onChange={(_, newValue) => {
              handleLayerSelect(newValue);
            }}
            data-testid='select-layer'
          />
        </FormControl>
        <Typography variant="caption">Domain</Typography>
        <FormControl fullWidth sx={{ m: 1 }}>
          <Autocomplete
            multiple={false}
            options={getUniqueDomains()}
            getOptionLabel={(option) => (option as string).split('/')[1] || ""}
            renderInput={(params) => <TextField {...params} size="small" />}
            value={layer && domain ? `${layer}/${domain}` : null}
            onChange={(_, newValue) => {
              handleDomainSelect(newValue);
            }}
            data-testid='select-domain'
          />
        </FormControl>
        <Typography variant="caption">Dataset</Typography>
        <FormControl fullWidth sx={{ m: 1 }}>
          <Autocomplete
            multiple={false}
            options={filteredDatasetsList}
            groupBy={(dataset) => `${(dataset as Dataset).layer}-${(dataset as Dataset).domain}`}
            getOptionLabel={(dataset) => (dataset as unknown as Dataset).dataset || ""}
            renderInput={(params) => <TextField {...params} size="small" />}
            renderGroup={(params) => (
              <li key={params.key}>
                <GroupHeader>{params.group}</GroupHeader>
                <GroupItems>{params.children}</GroupItems>
              </li>
            )}
            defaultValue={undefined}
            value={dataset}
            onChange={(_, newValue) => {
              setDataset(newValue as unknown as Dataset);
            }}
            data-testid='select-dataset'
          />
        </FormControl>
        {(enableVersionSelector && maxVersion != 0) && (
          <FormControl fullWidth sx={{ m: 1 }}>
            <Typography variant="caption">Select version</Typography>
            <Autocomplete
              multiple={false}
              options={Array(maxVersion).fill(0).map((_, i) => i + 1)}
              renderInput={(params) => <TextField {...params} size="small" />}
              onChange={(_, newValue) => {
                setVersion(newValue as unknown as number);
              }}
              value={version}
              data-testid='select-version'
            />
          </FormControl>
        )}
      </Row>
    </>
  )
}


export default DatasetSelector;
