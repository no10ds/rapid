// eslint-disable-next-line @typescript-eslint/no-var-requires
const fs = require('fs')

const file = fs.readFileSync('./CHANGELOG.md', { encoding: 'utf-8' })

const parsedLines = []
let adding = false

file.split(/\r?\n/).forEach((line) => {
  const pattern = /## v[0-9]\.[0-9]\.[0-9] - _[0-9]{4}-[0-9]{2}-[0-9]{2}_/
  if (pattern.test(line)) {
    adding = !adding
  }

  if (adding) {
    parsedLines.push(line)
  }
})

if (!parsedLines.length) {
  throw new Error(
    'It looks like there is no release information in the changelog. Please check it.'
  )
} else {
  const file = fs.createWriteStream('latest_release_changelog.md')
  file.on('error', (error) => {
    throw new Error(error)
  })
  parsedLines.forEach((line) => {
    file.write(`${line} \n`)
  })
  file.end()
}
