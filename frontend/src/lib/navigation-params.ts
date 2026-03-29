/**
 * Preserve only the TTH query flag across route transitions.
 */
export function withTTHParam(path: string, tthEnabled: boolean): string {
  const [base, hashPart] = path.split('#')
  const [pathname, queryPart] = base.split('?')
  const params = new URLSearchParams(queryPart || '')

  if (tthEnabled) {
    params.set('tth', 'true')
  } else {
    params.delete('tth')
  }

  const query = params.toString()
  const hash = hashPart ? `#${hashPart}` : ''

  return `${pathname}${query ? `?${query}` : ''}${hash}`
}
