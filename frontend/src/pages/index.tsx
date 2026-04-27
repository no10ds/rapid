import AccountLayout from '@/components/Layout/AccountLayout'
import { useQuery } from '@tanstack/react-query'
import { getMethods } from '@/service'
import { ReactNode, useState } from 'react'
import { useRouter } from 'next/router'

function AccountIndexPage() {
  const router = useRouter()
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['methods'],
    queryFn: getMethods,
    keepPreviousData: false,
    cacheTime: 0,
    refetchInterval: 0
  })

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" />
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (search.trim()) {
      router.push({ pathname: '/catalog', query: { q: search.trim() } })
    } else {
      router.push('/catalog')
    }
  }

  return (
    <div className="hp-wrap" data-testid="intro">
      <div className="hp-hero">
        <div className="hp-hero-glow" />
        <div className="hp-hero-wave" />
        <div className="hp-hero-wave-2" />
        <div className="hp-hero-inner">
          <h1 className="hp-hero-title">Welcome to rAPId</h1>
          <p className="hp-hero-sub">
            Your centralised platform for sharing, discovering and managing datasets.
          </p>
          <form className="hp-search-form" onSubmit={handleSearch}>
            <input
              className="hp-search-input"
              type="text"
              placeholder="Search datasets…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button className="hp-search-btn" type="submit">
              Search
            </button>
          </form>
        </div>
      </div>

      {(data?.can_upload || data?.can_download) && (
        <span data-testid="data-management" />
      )}
      {data?.can_create_schema && (
        <span data-testid="schema-management" />
      )}
      {data?.can_manage_users && (
        <span data-testid="user-management" />
      )}
    </div>
  )
}

export default AccountIndexPage

AccountIndexPage.getLayout = (page: ReactNode) => (
  <AccountLayout title="Dashboard" noPad>{page}</AccountLayout>
)
