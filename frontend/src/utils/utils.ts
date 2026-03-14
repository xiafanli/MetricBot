export const toLoginPage = (fullPath: string) => {
  if (!fullPath || fullPath === '/') {
    return {
      path: '/login',
    }
  }
  return {
    path: '/login',
    query: { redirect: fullPath },
  }
}

export const toLoginSuccess = (router: any) => {
  const redirect = router?.currentRoute?.value?.query?.redirect
  const redirectPath = Array.isArray(redirect) ? redirect[0] : redirect || '/'
  router.push(redirectPath as string)
}

export const getCurrentRouter = () => {
  const hash = location.hash
  if (!hash) return null
  return hash.replace('#/login?redirect=', '')
}

export const getQueryString = (name: string) => {
  const reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i')
  const r = window.location.search.substr(1).match(reg)
  if (r != null) {
    return unescape(r[2])
  }
  return null
}
