import { defineStore } from 'pinia'
import { api } from '@/api'
import { useCache } from '@/utils/useCache'
import { store } from './index'

const { wsCache } = useCache()

interface UserState {
  token: string
  uid: string
  username: string
  email: string
  isActive: boolean
  isSuperuser: boolean
  exp: number
}

export const UserStore = defineStore('user', {
  state: (): UserState => {
    return {
      token: wsCache.get('user.token') || '',
      uid: wsCache.get('user.uid') || '',
      username: wsCache.get('user.username') || '',
      email: wsCache.get('user.email') || '',
      isActive: wsCache.get('user.isActive') || false,
      isSuperuser: wsCache.get('user.isSuperuser') || false,
      exp: wsCache.get('user.exp') || 0,
    }
  },
  getters: {
    getToken(): string {
      return this.token
    },
    getUid(): string {
      return this.uid
    },
    getUsername(): string {
      return this.username
    },
    getEmail(): string {
      return this.email
    },
    getIsActive(): boolean {
      return this.isActive
    },
    getIsSuperuser(): boolean {
      return this.isSuperuser
    },
    getExp(): number {
      return this.exp
    },
    isLoggedIn(): boolean {
      return !!this.token && this.exp > Date.now() / 1000
    },
  },
  actions: {
    async login(formData: { username: string; password: string }) {
      const res: any = await api.login(formData.username, formData.password)
      this.setToken(res.access_token)
      await this.info()
    },

    async logout() {
      this.clear()
    },

    async info() {
      const res: any = await api.getCurrentUser()
      
      this.setUid(String(res.id))
      this.setUsername(res.username)
      this.setEmail(res.email)
      this.setIsActive(res.is_active)
      this.setIsSuperuser(res.is_superuser)
    },

    setToken(token: string) {
      wsCache.set('user.token', token)
      this.token = token
      
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        this.setExp(payload.exp)
      } catch (e) {
        console.error('Failed to parse token:', e)
      }
    },

    setExp(exp: number) {
      wsCache.set('user.exp', exp)
      this.exp = exp
    },

    setUid(uid: string) {
      wsCache.set('user.uid', uid)
      this.uid = uid
    },

    setUsername(username: string) {
      wsCache.set('user.username', username)
      this.username = username
    },

    setEmail(email: string) {
      wsCache.set('user.email', email)
      this.email = email
    },

    setIsActive(isActive: boolean) {
      wsCache.set('user.isActive', isActive)
      this.isActive = isActive
    },

    setIsSuperuser(isSuperuser: boolean) {
      wsCache.set('user.isSuperuser', isSuperuser)
      this.isSuperuser = isSuperuser
    },

    clear() {
      const keys: string[] = [
        'token',
        'uid',
        'username',
        'email',
        'isActive',
        'isSuperuser',
        'exp',
      ]
      keys.forEach((key) => wsCache.delete('user.' + key))
      this.$reset()
    },
  },
})

export const useUserStore = () => {
  return UserStore(store)
}
