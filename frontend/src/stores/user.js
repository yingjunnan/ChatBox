import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    username: ''
  }),
  actions: {
    generateUsername() {
      const adjectives = ['快乐', '聪明', '勇敢', '友好', '活泼', '可爱', '神秘', '酷炫']
      const nouns = ['熊猫', '狐狸', '兔子', '猫咪', '小鸟', '海豚', '企鹅', '考拉']
      const adj = adjectives[Math.floor(Math.random() * adjectives.length)]
      const noun = nouns[Math.floor(Math.random() * nouns.length)]
      const num = Math.floor(Math.random() * 1000)
      this.username = `${adj}的${noun}${num}`
      localStorage.setItem('username', this.username)
    },
    loadUsername() {
      const saved = localStorage.getItem('username')
      if (saved) {
        this.username = saved
      } else {
        this.generateUsername()
      }
    }
  }
})
