import { defineStore } from 'pinia'

const API_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : 'http://localhost:8000'

export const useUserStore = defineStore('user', {
  state: () => ({
    // Guest mode fields
    username: '',
    isGuest: true,

    // Authenticated user fields
    userId: null,
    displayName: '',
    email: '',
    avatarUrl: '',
    accessToken: '',
    refreshToken: '',
    isAuthenticated: false
  }),
  actions: {
    // Guest mode methods
    generateUsername() {
      const adjectives = ['快乐', '聪明', '勇敢', '友好', '活泼', '可爱', '神秘', '酷炫']
      const nouns = ['熊猫', '狐狸', '兔子', '猫咪', '小鸟', '海豚', '企鹅', '考拉']
      const adj = adjectives[Math.floor(Math.random() * adjectives.length)]
      const noun = nouns[Math.floor(Math.random() * nouns.length)]
      const num = Math.floor(Math.random() * 1000)
      this.username = `${adj}的${noun}${num}`
      localStorage.setItem('username', this.username)
    },
    setUsername(name) {
      this.username = name
      localStorage.setItem('username', this.username)
    },
    loadUsername() {
      const saved = localStorage.getItem('username')
      if (saved) {
        this.username = saved
      } else {
        this.generateUsername()
      }
    },

    // Authentication methods
    async register(username, password, displayName = null, email = null) {
      try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password, display_name: displayName, email })
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || '注册失败')
        }

        const data = await response.json()
        this.setAuthData(data)
        await this.loadUserProfile()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async login(username, password) {
      try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || '登录失败')
        }

        const data = await response.json()
        this.setAuthData(data)
        await this.loadUserProfile()
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async logout() {
      try {
        if (this.refreshToken) {
          await fetch(`${API_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${this.accessToken}`
            },
            body: JSON.stringify({ refresh_token: this.refreshToken })
          })
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.clearAuthState()
      }
    },

    async refreshAccessToken() {
      try {
        const response = await fetch(`${API_URL}/api/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: this.refreshToken })
        })

        if (!response.ok) {
          throw new Error('Token refresh failed')
        }

        const data = await response.json()
        this.setAuthData(data)
        return true
      } catch (error) {
        this.clearAuthState()
        return false
      }
    },

    async loadUserProfile() {
      try {
        const response = await fetch(`${API_URL}/api/users/me`, {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        })

        if (response.status === 401) {
          // Token expired, try to refresh
          const refreshed = await this.refreshAccessToken()
          if (refreshed) {
            // Retry with new token
            const retryResponse = await fetch(`${API_URL}/api/users/me`, {
              headers: { 'Authorization': `Bearer ${this.accessToken}` }
            })
            if (!retryResponse.ok) {
              throw new Error('Failed to load profile after refresh')
            }
            const user = await retryResponse.json()
            this.userId = user.id
            this.username = user.username
            this.displayName = user.display_name || user.username
            this.email = user.email
            this.avatarUrl = user.avatar_url
            return
          } else {
            // Refresh failed, clear auth and switch to guest
            throw new Error('Token refresh failed')
          }
        }

        if (!response.ok) {
          throw new Error('Failed to load profile')
        }

        const user = await response.json()
        this.userId = user.id
        this.username = user.username
        this.displayName = user.display_name || user.username
        this.email = user.email
        this.avatarUrl = user.avatar_url
      } catch (error) {
        console.error('Load profile error:', error)
        this.clearAuthState()
      }
    },

    async updateProfile(data) {
      try {
        let response = await fetch(`${API_URL}/api/users/me`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.accessToken}`
          },
          body: JSON.stringify(data)
        })

        if (response.status === 401) {
          // Token expired, try to refresh
          const refreshed = await this.refreshAccessToken()
          if (refreshed) {
            // Retry with new token
            response = await fetch(`${API_URL}/api/users/me`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.accessToken}`
              },
              body: JSON.stringify(data)
            })
          } else {
            return { success: false, error: '登录已过期，请重新登录' }
          }
        }

        if (!response.ok) {
          throw new Error('Failed to update profile')
        }

        const user = await response.json()
        this.displayName = user.display_name || user.username
        this.email = user.email
        this.avatarUrl = user.avatar_url
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    async uploadAvatar(file) {
      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${API_URL}/api/users/me/avatar`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${this.accessToken}` },
          body: formData
        })

        if (!response.ok) {
          throw new Error('Failed to upload avatar')
        }

        const data = await response.json()
        this.avatarUrl = data.avatar_url
        return { success: true, avatarUrl: data.avatar_url }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },

    setAuthData(data) {
      this.accessToken = data.access_token
      this.refreshToken = data.refresh_token
      this.isAuthenticated = true
      this.isGuest = false

      localStorage.setItem('accessToken', this.accessToken)
      localStorage.setItem('refreshToken', this.refreshToken)
    },

    async loadAuthState() {
      const accessToken = localStorage.getItem('accessToken')
      const refreshToken = localStorage.getItem('refreshToken')

      if (accessToken && refreshToken) {
        this.accessToken = accessToken
        this.refreshToken = refreshToken
        this.isAuthenticated = true
        this.isGuest = false
        await this.loadUserProfile()
      } else {
        this.loadUsername()
      }
    },

    clearAuthState() {
      this.userId = null
      this.displayName = ''
      this.email = ''
      this.avatarUrl = ''
      this.accessToken = ''
      this.refreshToken = ''
      this.isAuthenticated = false
      this.isGuest = true

      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')

      this.loadUsername()
    }
  }
})
