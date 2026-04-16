import { ComponentProps, ReactNode, useState } from 'react'
import { useQueries } from '@tanstack/react-query'
import { getAuthStatus, getMethods } from '@/service'
import { MethodsResponse } from '@/service/types'
import { useRouter } from 'next/router'
import Router from 'next/router'
import Link from 'next/link'
import Image from 'next/image'

// ─── SVG Icons (stroke/fill style, 17×17 rendered via CSS) ──────────────────

const IconDashboard = () => (
  <svg className="stroke-icon" viewBox="0 0 24 24">
    <rect x="3" y="3" width="7" height="7" rx="1" />
    <rect x="14" y="3" width="7" height="7" rx="1" />
    <rect x="3" y="14" width="7" height="7" rx="1" />
    <rect x="14" y="14" width="7" height="7" rx="1" />
  </svg>
)

const IconCatalog = () => (
  <svg className="fill-icon" viewBox="0 0 24 24">
    <path d="m16 6a1 1 0 0 1 0 2h-8a1 1 0 0 1 0-2zm7.707 17.707a1 1 0 0 1 -1.414 0l-2.407-2.407a4.457 4.457 0 0 1 -2.386.7 4.5 4.5 0 1 1 4.5-4.5 4.457 4.457 0 0 1 -.7 2.386l2.407 2.407a1 1 0 0 1 0 1.414zm-6.207-3.707a2.5 2.5 0 1 0 -2.5-2.5 2.5 2.5 0 0 0 2.5 2.5zm-4.5 2h-6a3 3 0 0 1 -3-3v-14a3 3 0 0 1 3-3h12a1 1 0 0 1 1 1v8a1 1 0 0 0 2 0v-8a3 3 0 0 0 -3-3h-12a5.006 5.006 0 0 0 -5 5v14a5.006 5.006 0 0 0 5 5h6a1 1 0 0 0 0-2z" />
  </svg>
)

const IconUpload = () => (
  <svg className="stroke-icon" viewBox="0 0 24 24">
    <path d="M17 17H17.01M15.6 14H18C18.9319 14 19.3978 14 19.7654 14.1522C20.2554 14.3552 20.6448 14.7446 20.8478 15.2346C21 15.6022 21 16.0681 21 17C21 17.9319 21 18.3978 20.8478 18.7654C20.6448 19.2554 20.2554 19.6448 19.7654 19.8478C19.3978 20 18.9319 20 18 20H6C5.06812 20 4.60218 20 4.23463 19.8478C3.74458 19.6448 3.35523 19.2554 3.15224 18.7654C3 18.3978 3 17.9319 3 17C3 16.0681 3 15.6022 3.15224 15.2346C3.35523 14.7446 3.74458 14.3552 4.23463 14.1522C4.60218 14 5.06812 14 6 14H8.4M12 15V4M12 4L15 7M12 4L9 7" />
  </svg>
)

const IconSchema = () => (
  <svg className="fill-icon" viewBox="0 0 24 24">
    <path d="M0,3v8H11V0H3A3,3,0,0,0,0,3ZM9,9H2V3A1,1,0,0,1,3,2H9Z" />
    <path d="M0,21a3,3,0,0,0,3,3h8V13H0Zm2-6H9v7H3a1,1,0,0,1-1-1Z" />
    <path d="M13,13V24h8a3,3,0,0,0,3-3V13Zm9,8a1,1,0,0,1-1,1H15V15h7Z" />
    <polygon points="17 11 19 11 19 7 23 7 23 5 19 5 19 1 17 1 17 5 13 5 13 7 17 7 17 11" />
  </svg>
)

const IconJobs = () => (
  <svg className="fill-icon" viewBox="0 0 24 24">
    <path d="M4,11H20c5.276-.138,5.272-7.863,0-8H4c-5.276,.138-5.272,7.863,0,8ZM22,7c0,1.103-.897,2-2,2h-4V5h4c1.103,0,2,.897,2,2Zm-2,6H4c-5.276,.138-5.272,7.863,0,8H20c5.276-.138,5.272-7.863,0-8Zm0,6H10v-4h10c2.629,.048,2.627,3.953,0,4Z" />
  </svg>
)

const IconUserAdmin = () => (
  <svg className="stroke-icon" viewBox="0 0 24 24">
    <path d="M17,21V19a4,4,0,0,0-4-4H5a4,4,0,0,0-4,4v2" />
    <circle cx="9" cy="7" r="4" />
    <line x1="17" x2="23" y1="11" y2="11" />
    <line x1="20" x2="20" y1="8" y2="14" />
  </svg>
)

const IconDataAdmin = () => (
  <svg className="fill-icon" viewBox="0 0 24 24">
    <path d="M12 2C6.48 2 2 4.69 2 8v8c0 3.31 4.48 6 10 6s10-2.69 10-6V8c0-3.31-4.48-6-10-6zm0 2c4.42 0 8 2.01 8 4s-3.58 4-8 4-8-2.01-8-4 3.58-4 8-4zm0 16c-4.42 0-8-2.01-8-4v-2.23c1.61 1.38 4.62 2.23 8 2.23s6.39-.85 8-2.23V16c0 1.99-3.58 4-8 4zm0-6c-4.42 0-8-2.01-8-4v-2.23c1.61 1.38 4.62 2.23 8 2.23s6.39-.85 8-2.23V10c0 1.99-3.58 4-8 4z"/>
  </svg>
)

// ─── Nav item component ──────────────────────────────────────────────────────

type NavItemProps = {
  href: string
  icon: ReactNode
  label: string
  badge?: string | number
  activePaths?: string[]
}

function NavItem({ href, icon, label, badge, activePaths }: NavItemProps) {
  const router = useRouter()
  const { asPath } = router
  const checkPaths = activePaths ?? [href]
  const isActive = checkPaths.some((p) => {
    if (p === '/') return asPath === '/'
    return asPath.startsWith(p)
  })

  return (
    <Link href={href} className={`ni${isActive ? ' act' : ''}`} style={{ textDecoration: 'none' }}>
      <div className="ni-ico">{icon}</div>
      <span className="ni-lbl">{label}</span>
      {badge !== undefined && <span className="ni-badge">{badge}</span>}
    </Link>
  )
}

// ─── Props ───────────────────────────────────────────────────────────────────

type AccountLayoutProps = {
  title?: string
  topbarActions?: ReactNode
  children: ReactNode
} & Omit<ComponentProps<'div'>, 'children' | 'title'>

// ─── Component ───────────────────────────────────────────────────────────────

const AccountLayout = ({ children, title, topbarActions }: AccountLayoutProps) => {
  const [collapsed, setCollapsed] = useState(false)

  const redirect = () => {
    Router.replace({ pathname: '/login' })
  }

  const results = useQueries({
    queries: [
      {
        queryKey: ['authStatus'],
        queryFn: getAuthStatus,
        keepPreviousData: false,
        cacheTime: 0,
        refetchInterval: 0,
        onError: () => redirect(),
        onSuccess: (data: { detail: string }) => {
          if (data.detail === 'fail') redirect()
        }
      },
      {
        queryKey: ['methods'],
        queryFn: getMethods,
        keepPreviousData: false,
        cacheTime: 0,
        refetchInterval: 0
      }
    ]
  })

  const isLoading = results[0].isLoading || results[1].isLoading
  const methods: MethodsResponse | undefined = results[1].data

  if (isLoading) {
    return <div className="rapid-loading-bar" role="progressbar" aria-label="Loading" />
  }

  const toggleCollapse = () => setCollapsed((c) => !c)

  const hasDataSection =
    methods?.can_upload ||
    methods?.can_download ||
    methods?.can_search_catalog ||
    methods?.can_create_schema

  const hasJobsSection = methods?.can_upload || methods?.can_download

  return (
    <div className="rapid-shell">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className={`rapid-sidebar${collapsed ? ' col' : ''}`}>
        {/* Header: logo + collapse toggle */}
        <div className="sb-header">
          <Link
            href="/"
            style={{
              flex: 1,
              minWidth: 0,
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              overflow: 'hidden'
            }}
          >
            <Image
              src="/img/logo.png"
              alt="rAPId"
              width={160}
              height={40}
              className="logo-img"
              style={{
                objectFit: 'contain',
                objectPosition: 'left center',
                padding: '8px 12px',
                height: '80%',
                width: 'auto',
                maxWidth: '100%',
                transition: 'opacity 0.2s'
              }}
              priority
            />
          </Link>
          <button
            className="sb-tog"
            onClick={toggleCollapse}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? '▶' : '◀'}
          </button>
        </div>

        {/* Dashboard — always visible */}
        <div className="sb-sec">
          <NavItem href="/" icon={<IconDashboard />} label="Dashboard" />
        </div>

        {/* DATA section */}
        {hasDataSection && (
          <div className="sb-sec">
            <div className="sb-sec-lbl">Data</div>
            {methods?.can_search_catalog && (
              <NavItem
                href="/catalog"
                icon={<IconCatalog />}
                label="Catalog"
                activePaths={['/catalog']}
              />
            )}
            {methods?.can_upload && (
              <NavItem
                href="/data/upload"
                icon={<IconUpload />}
                label="Upload"
                activePaths={['/data/upload', '/data/delete', '/data/download']}
              />
            )}
            {methods?.can_create_schema && (
              <NavItem
                href="/schema/create"
                icon={<IconSchema />}
                label="Create Schema"
                activePaths={['/schema']}
              />
            )}
          </div>
        )}

        {/* JOBS section */}
        {hasJobsSection && (
          <div className="sb-sec">
            <div className="sb-sec-lbl">Jobs</div>
            <NavItem
              href="/tasks"
              icon={<IconJobs />}
              label="Jobs"
              activePaths={['/tasks']}
            />
          </div>
        )}

        {/* ADMIN section */}
        {methods?.can_manage_users && (
          <div className="sb-sec">
            <div className="sb-sec-lbl">Admin</div>
            <NavItem
              href="/subject"
              icon={<IconUserAdmin />}
              label="User Admin"
              activePaths={['/subject']}
            />
            <NavItem
              href="/admin"
              icon={<IconDataAdmin />}
              label="Data Admin"
              activePaths={['/admin']}
            />
          </div>
        )}

        {/* Footer */}
        <div className="sb-foot">
          <div className="usr">
            <div className="ava">rA</div>
            <div className="usr-info">
              <div className="usr-name">rAPId User</div>
              <div className="usr-role">
                {methods?.can_manage_users ? 'User Admin' : 'Data User'}
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main area ────────────────────────────────────────── */}
      <div className="rapid-main">
        {/* Topbar */}
        <div className="rapid-topbar">
          <div className="topbar-title">{title}</div>
          <div className="topbar-spacer" />
          {topbarActions}
        </div>

        {/* Page content */}
        <div className="rapid-content">{children}</div>
      </div>
    </div>
  )
}

export default AccountLayout
