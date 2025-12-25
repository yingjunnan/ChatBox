<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const rooms = ref([])
const showCreateModal = ref(false)
const showJoinModal = ref(false)
const newRoomName = ref('')
const newRoomPassword = ref('')
const joinRoomId = ref('')
const joinRoomName = ref('')
const joinRoomPassword = ref('')
const editingUsername = ref(false)
const tempUsername = ref('')

const API_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : 'http://localhost:8000'

onMounted(async () => {
  await loadRooms()
})

async function loadRooms() {
  const response = await fetch(`${API_URL}/api/rooms`)
  rooms.value = await response.json()
}

async function createRoom() {
  const response = await fetch(`${API_URL}/api/rooms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: newRoomName.value,
      password: newRoomPassword.value || null
    })
  })
  const room = await response.json()
  showCreateModal.value = false
  newRoomName.value = ''
  newRoomPassword.value = ''
  router.push(`/chat/${room.id}?name=${encodeURIComponent(room.name)}`)
}

async function joinRoom(roomId, roomName = null, needPassword = false) {
  if (needPassword && !joinRoomPassword.value) {
    joinRoomId.value = roomId
    joinRoomName.value = roomName || roomId
    showJoinModal.value = true
    return
  }

  try {
    const response = await fetch(`${API_URL}/api/rooms/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        room_id: roomId,
        password: joinRoomPassword.value || null
      })
    })

    if (response.ok) {
      const data = await response.json()
      showJoinModal.value = false
      joinRoomPassword.value = ''
      joinRoomId.value = ''
      joinRoomName.value = ''
      const name = roomName || data.room?.name || roomId
      router.push(`/chat/${roomId}?name=${encodeURIComponent(name)}`)
    } else {
      alert('密码错误或房间不存在')
    }
  } catch (error) {
    alert('加入房间失败')
  }
}

function directJoin() {
  if (joinRoomId.value) {
    joinRoom(joinRoomId.value, joinRoomName.value, false)
  }
}

function resetUsername() {
  userStore.generateUsername()
}

function startEditUsername() {
  tempUsername.value = userStore.username
  editingUsername.value = true
}

function saveUsername() {
  if (tempUsername.value.trim()) {
    userStore.setUsername(tempUsername.value.trim())
  }
  editingUsername.value = false
}

function cancelEditUsername() {
  editingUsername.value = false
  tempUsername.value = ''
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">聊天室</h1>
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2 flex-1">
            <span class="text-gray-600">当前用户:</span>
            <span v-if="!editingUsername" class="font-medium text-gray-800">{{ userStore.username }}</span>
            <input v-else v-model="tempUsername" class="px-3 py-1 border rounded flex-1 max-w-xs" placeholder="输入用户名">
          </div>
          <div class="flex gap-2">
            <button v-if="!editingUsername" @click="startEditUsername" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm">
              编辑
            </button>
            <button v-if="editingUsername" @click="saveUsername" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 text-sm">
              保存
            </button>
            <button v-if="editingUsername" @click="cancelEditUsername" class="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500 text-sm">
              取消
            </button>
            <button @click="resetUsername" class="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 text-sm">
              随机生成
            </button>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div class="flex gap-4 mb-4">
          <button @click="showCreateModal = true" class="flex-1 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600">
            创建聊天室
          </button>
          <button @click="showJoinModal = true" class="flex-1 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600">
            输入房间ID加入
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">活跃的聊天室</h2>
        <div class="space-y-3">
          <div v-for="room in rooms" :key="room.id" class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
            <div class="flex items-center gap-2">
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-gray-800">{{ room.name }}</h3>
                  <span v-if="room.has_password" class="text-yellow-600" title="需要密码">🔒</span>
                  <span v-if="room.online_count > 0" class="flex items-center gap-1 text-green-600 text-sm">
                    <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                    {{ room.online_count }} 在线
                  </span>
                </div>
                <p class="text-sm text-gray-500">房间ID: {{ room.id }}</p>
              </div>
            </div>
            <button @click="joinRoom(room.id, room.name, room.has_password)" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              加入
            </button>
          </div>
          <div v-if="rooms.length === 0" class="text-center text-gray-500 py-8">
            暂无活跃的聊天室
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-96">
        <h2 class="text-xl font-bold mb-4">创建聊天室</h2>
        <input v-model="newRoomName" placeholder="房间名称" class="w-full px-4 py-2 border rounded mb-3">
        <input v-model="newRoomPassword" type="password" placeholder="密码 (可选)" class="w-full px-4 py-2 border rounded mb-4">
        <div class="flex gap-3">
          <button @click="createRoom" class="flex-1 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            创建
          </button>
          <button @click="showCreateModal = false" class="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400">
            取消
          </button>
        </div>
      </div>
    </div>

    <div v-if="showJoinModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h2 class="text-xl font-bold mb-4">加入聊天室</h2>
        <div class="mb-3">
          <label class="block text-sm text-gray-600 mb-1">房间名称</label>
          <input v-model="joinRoomName" readonly class="w-full px-4 py-2 border rounded bg-gray-50">
        </div>
        <div class="mb-3">
          <label class="block text-sm text-gray-600 mb-1">房间ID</label>
          <input v-model="joinRoomId" :readonly="joinRoomId !== ''" :placeholder="joinRoomId ? '' : '房间ID'" class="w-full px-4 py-2 border rounded" :class="joinRoomId ? 'bg-gray-50' : ''">
        </div>
        <input v-model="joinRoomPassword" type="password" placeholder="密码" class="w-full px-4 py-2 border rounded mb-4">
        <div class="flex gap-3">
          <button @click="directJoin" class="flex-1 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            加入
          </button>
          <button @click="showJoinModal = false; joinRoomId = ''; joinRoomName = ''; joinRoomPassword = ''" class="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400">
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
