type CacheType = 'sessionStorage' | 'localStorage'

class SimpleCache {
  private storage: Storage

  constructor(type: CacheType = 'localStorage') {
    this.storage = type === 'localStorage' ? window.localStorage : window.sessionStorage
  }

  set(key: string, value: any) {
    try {
      const serialized = typeof value === 'string' ? value : JSON.stringify(value)
      this.storage.setItem(key, serialized)
    } catch (e) {
      console.error('Cache set error:', e)
    }
  }

  get(key: string) {
    try {
      const value = this.storage.getItem(key)
      if (!value) return null
      try {
        return JSON.parse(value)
      } catch {
        return value
      }
    } catch (e) {
      console.error('Cache get error:', e)
      return null
    }
  }

  delete(key: string) {
    this.storage.removeItem(key)
  }
}

export const useCache = (type: CacheType = 'localStorage') => {
  const wsCache = new SimpleCache(type)
  return { wsCache }
}
