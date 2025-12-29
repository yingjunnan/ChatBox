<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const messages = ref([])
const messageInput = ref('')
const ws = ref(null)
const messagesContainer = ref(null)
const fileInput = ref(null)
const showEmojiPicker = ref(false)
const roomName = ref(route.query.name || route.params.roomId)
const notificationSound = ref(null)
const enlargedImage = ref(null)
const onlineUsers = ref([])
const accessDenied = ref(false)

const currentDisplayName = computed(() => {
  return userStore.isAuthenticated ? (userStore.displayName || userStore.username) : userStore.username
})

const API_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : 'http://localhost:8000'
const WS_URL = import.meta.env.VITE_WS_URL !== undefined ? import.meta.env.VITE_WS_URL : 'ws://localhost:8000'

const emojis = ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚',
           '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥',
         '😌', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '😎', '🤓', '🧐', '😕', '😟', '🙁', '☹️',
          '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫', '🥱',
          // 手势
          '👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎',
          '✊', '👊', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻', '👃', '🧠', '🦷',]

onMounted(async () => {
  await loadHistoricalMessages()
  connectWebSocket()
  notificationSound.value = new Audio('/new-notification.mp3')
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})

async function loadHistoricalMessages() {
  try {
    const roomToken = sessionStorage.getItem(`room_token_${route.params.roomId}`)
    const headers = {}
    if (roomToken) {
      headers['X-Room-Access-Token'] = roomToken
    }

    const response = await fetch(`${API_URL}/api/rooms/${route.params.roomId}/messages`, { headers })
    if (response.ok) {
      const historicalMessages = await response.json()
      messages.value = historicalMessages
      nextTick(() => {
        scrollToBottom()
      })
    } else if (response.status === 403) {
      if (!accessDenied.value) {
        accessDenied.value = true
        alert('无权访问此房间，请先验证密码')
        router.push('/')
      }
    }
  } catch (error) {
    console.error('Failed to load historical messages:', error)
  }
}

function connectWebSocket() {
  // 如果 WS_URL 为空，根据当前页面协议动态构建 WebSocket URL
  const wsBaseUrl = WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`

  const roomToken = sessionStorage.getItem(`room_token_${route.params.roomId}`)
  let wsUrl

  if (userStore.isAuthenticated) {
    // Authenticated user: send token and room access token
    wsUrl = `${wsBaseUrl}/ws/${route.params.roomId}?token=${encodeURIComponent(userStore.accessToken)}`
    if (roomToken) {
      wsUrl += `&room_access_token=${encodeURIComponent(roomToken)}`
    }
  } else {
    // Guest user: send username and room access token
    wsUrl = `${wsBaseUrl}/ws/${route.params.roomId}?username=${encodeURIComponent(userStore.username)}`
    if (roomToken) {
      wsUrl += `&room_access_token=${encodeURIComponent(roomToken)}`
    }
  }

  ws.value = new WebSocket(wsUrl)

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'system') {
      // Handle system messages (join/leave)
      onlineUsers.value = data.online_users
      messages.value.push({
        type: 'system',
        content: data.action === 'join' ? `${data.username} 加入了聊天室` : `${data.username} 离开了聊天室`,
        username: 'System',
        timestamp: new Date().toISOString()
      })
    } else if (data.type === 'recall') {
      // Handle message recall
      const msgIndex = messages.value.findIndex(m => m.id === data.message_id)
      if (msgIndex !== -1) {
        messages.value[msgIndex].is_recalled = true
      }
    } else {
      if (!data.timestamp) {
        data.timestamp = new Date().toISOString()
      }
      messages.value.push(data)
    }

    if (data.username !== currentDisplayName.value && data.type !== 'system') {
      notificationSound.value?.play().catch(() => {})
    }

    nextTick(() => {
      scrollToBottom()
    })
  }

  ws.value.onclose = (event) => {
    if (event.code === 1008 && !accessDenied.value) {
      accessDenied.value = true
      alert('无权访问此房间，请先验证密码')
      router.push('/')
    }
  }
}

function sendMessage() {
  if (!messageInput.value.trim()) return

  const message = {
    username: currentDisplayName.value,
    content: messageInput.value,
    type: 'text'
  }

  ws.value.send(JSON.stringify(message))
  messageInput.value = ''
}

function insertEmoji(emoji) {
  messageInput.value += emoji
  showEmojiPicker.value = false
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  await uploadFile(file)
}

async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_URL}/api/upload`, {
      method: 'POST',
      body: formData
    })
    const data = await response.json()

    const fileType = file.type.startsWith('image/') ? 'image' : 'video'
    const message = {
      username: currentDisplayName.value,
      content: `${API_URL}${data.url}`,
      type: fileType
    }

    ws.value.send(JSON.stringify(message))
  } catch (error) {
    alert('文件上传失败')
  }
}

async function handlePaste(event) {
  const items = event.clipboardData?.items
  if (!items) return

  for (const item of items) {
    if (item.type.startsWith('image/')) {
      event.preventDefault()
      const file = item.getAsFile()
      if (file) await uploadFile(file)
      break
    }
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function openImage(imageUrl) {
  enlargedImage.value = imageUrl
}

function closeImage() {
  enlargedImage.value = null
}

function leaveRoom() {
  router.push('/')
}

function formatMessageTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function canRecallMessage(msg) {
  if (msg.username !== currentDisplayName.value) return false
  if (msg.is_recalled) return false
  if (!msg.timestamp) return false
  const messageTime = new Date(msg.timestamp)
  const now = new Date()
  const diffMinutes = (now - messageTime) / 1000 / 60
  return diffMinutes < 2
}

async function recallMessage(msg) {
  if (!confirm('确定要撤回这条消息吗？')) return

  try {
    const params = new URLSearchParams()
    if (!userStore.isAuthenticated) {
      params.append('username', userStore.username)
    }

    const headers = {}
    if (userStore.isAuthenticated) {
      headers['Authorization'] = `Bearer ${userStore.accessToken}`
    }

    const response = await fetch(`${API_URL}/api/messages/${msg.id}?${params}`, {
      method: 'DELETE',
      headers
    })

    if (!response.ok) {
      const error = await response.json()
      alert(error.detail || '撤回失败')
    }
  } catch (error) {
    console.error('Failed to recall message:', error)
    alert('撤回失败')
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 p-4 md:p-8">
    <div class="max-w-6xl mx-auto h-[calc(100vh-4rem)] md:h-[calc(100vh-8rem)] flex gap-4">
      <!-- Main Chat Area -->
      <div class="flex-1 flex flex-col bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div class="bg-white shadow-md p-4 flex justify-between items-center border-b">
          <div>
            <h1 class="text-xl font-bold text-gray-800">{{ roomName }}</h1>
            <p class="text-sm text-gray-600">用户: {{ userStore.username }} | 房间ID: {{ route.params.roomId }}</p>
          </div>
          <button @click="leaveRoom" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            离开房间
          </button>
        </div>

        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
          <div v-for="(msg, index) in messages" :key="index">
            <!-- System Messages -->
            <div v-if="msg.type === 'system'" class="flex justify-center">
              <div class="bg-gray-200 text-gray-600 text-xs px-3 py-1 rounded-full">
                {{ msg.content }}
              </div>
            </div>
            <!-- User Messages -->
            <div v-else class="flex" :class="msg.username === currentDisplayName ? 'justify-end' : 'justify-start'">
              <div class="max-w-xs lg:max-w-md">
                <div class="text-xs text-gray-500 mb-1 flex items-center gap-2" :class="msg.username === currentDisplayName ? 'justify-end' : 'justify-start'">
                  <span>{{ msg.username }}</span>
                  <span class="text-gray-400">{{ formatMessageTime(msg.timestamp) }}</span>
                </div>
                <div class="rounded-lg p-3 shadow-sm" :class="msg.username === currentDisplayName ? 'bg-blue-500 text-white' : 'bg-white text-gray-800 border border-gray-200'">
                  <div v-if="msg.is_recalled" class="text-gray-400 italic">消息已撤回</div>
                  <div v-else>
                    <div v-if="msg.type === 'text'">{{ msg.content }}</div>
                    <img v-else-if="msg.type === 'image'" :src="msg.content" @click="openImage(msg.content)" class="max-w-full rounded cursor-pointer hover:opacity-90 transition" />
                    <video v-else-if="msg.type === 'video'" :src="msg.content" controls class="max-w-full rounded" />
                  </div>
                </div>
                <div v-if="canRecallMessage(msg)" class="text-xs mt-1 flex justify-end">
                  <button @click="recallMessage(msg)" class="text-gray-500 hover:text-red-500">撤回</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white border-t p-4">
          <div v-if="showEmojiPicker" class="mb-2 p-2 bg-gray-50 rounded-lg">
            <div class="flex flex-wrap gap-2">
              <button v-for="emoji in emojis" :key="emoji" @click="insertEmoji(emoji)" class="text-2xl hover:bg-gray-200 rounded p-1">
                {{ emoji }}
              </button>
            </div>
          </div>

          <div class="flex gap-2">
            <button @click="showEmojiPicker = !showEmojiPicker" class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">
              😀
            </button>
            <button @click="fileInput.click()" class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300">
              📎
            </button>
            <input ref="fileInput" type="file" accept="image/*,video/*" @change="handleFileUpload" class="hidden" />
            <input v-model="messageInput" @keyup.enter="sendMessage" @paste="handlePaste" placeholder="输入消息..." class="flex-1 px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <button @click="sendMessage" class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600">
              发送
            </button>
          </div>
        </div>
      </div>

      <!-- Online Users Sidebar -->
      <div class="w-64 bg-white rounded-2xl shadow-2xl p-4 hidden md:block">
        <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span class="w-2 h-2 bg-green-500 rounded-full"></span>
          在线用户 ({{ onlineUsers.length }})
        </h2>
        <div class="space-y-2">
          <div v-for="user in onlineUsers" :key="user" class="flex items-center gap-2 p-2 rounded hover:bg-gray-50">
            <span class="w-2 h-2 bg-green-500 rounded-full"></span>
            <span class="text-sm text-gray-700" :class="user === userStore.username ? 'font-bold' : ''">
              {{ user }}{{ user === userStore.username ? ' (你)' : '' }}
            </span>
          </div>
          <div v-if="onlineUsers.length === 0" class="text-sm text-gray-500 text-center py-4">
            暂无在线用户
          </div>
        </div>
      </div>
    </div>

    <div v-if="enlargedImage" @click="closeImage" class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
      <div class="relative max-w-7xl max-h-full">
        <button @click="closeImage" class="absolute -top-12 right-0 text-white text-4xl hover:text-gray-300">
          ×
        </button>
        <img :src="enlargedImage" @click.stop class="max-w-full max-h-[90vh] object-contain rounded-lg" />
      </div>
    </div>
  </div>
</template>
