const regexSuffixless = /\/[^/.]+$/ // e.g. "/some/page" but not "/", "/some/" or "/some.jpg"
const regexTrailingSlash = /.+\/$/ // e.g. "/some/" or "/some/page/" but not root "/"

exports.handler = function (event, _, callback) {
  const { request } = event.Records[0].cf
  const uri = request.uri

  // Handle dynamic routes
  const dynamicRoutes = {
    '/catalog/[search].html': /\/catalog\/[0-9a-zA-Z]/,
    '/data/download/[domain]/[dataset].html': /\/data\/download\/[^/]+\/[^/]+/,
    '/subject/modify/[subjectId].html': /\/subject\/modify\/[0-9]+/,
    '/subject/modify/success/[subjectId].html': /\/subject\/modify\/success\/[0-9]+/,
    '/tasks/[jobId].html': /\/tasks\/[0-9]+/
  }
  if (uri && !uri.endsWith('.js')) {
    let found = false
    Object.keys(dynamicRoutes).forEach((key) => {
      const value = dynamicRoutes[key]
      const isDynamicRouteMatch = value.test(uri)
      if (isDynamicRouteMatch) {
        request.uri = key
        found = true
        return
      }
    })
    if (found) {
      callback(null, request)
      return
    }
  }

  // Handle route without a suffix
  if (uri.match(regexSuffixless)) {
    request.uri = uri + '.html'
    callback(null, request)
    return
  }

  // Handle all other routes that have a trailing slash
  if (uri.match(regexTrailingSlash)) {
    request.uri = uri + 'index.html'
    callback(null, request)
    return
  }

  callback(null, request)
  return
}
