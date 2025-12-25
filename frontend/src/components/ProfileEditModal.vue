<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="close">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">编辑资料</h2>
        <button @click="close" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
      </div>

      <div class="space-y-6">
        <!-- Profile Section -->
        <div>
          <h3 class="text-lg font-semibold text-gray-700 mb-4">基本信息</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">用户名（不可修改）</label>
              <input
                :value="userStore.username"
                disabled
                class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">显示名称</label>
              <input
                v-model="profileForm.displayName"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="聊天时显示的名称"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your@email.com"
              />
            </div>

            <div v-if="profileError" class="text-red-600 text-sm">
              {{ profileError }}
            </div>

            <div v-if="profileSuccess" class="text-green-600 text-sm">
              {{ profileSuccess }}
            </div>

            <button
              @click="updateProfile"
              :disabled="profileLoading"
              class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              {{ profileLoading ? '保存中...' : '保存资料' }}
            </button>
          </div>
        </div>

        <!-- Password Section -->
        <div class="border-t pt-6">
          <h3 class="text-lg font-semibold text-gray-700 mb-4">修改密码</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">旧密码</label>
              <input
                v-model="passwordForm.oldPassword"
                type="password"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="请输入旧密码"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">新密码</label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                minlength="6"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="至少6个字符"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">确认新密码</label>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="再次输入新密码"
              />
            </div>

            <div v-if="passwordError" class="text-red-600 text-sm">
              {{ passwordError }}
            </div>

            <div v-if="passwordSuccess" class="text-green-600 text-sm">
              {{ passwordSuccess }}
            </div>

            <button
              @click="changePassword"
              :disabled="passwordLoading"
              class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
            >
              {{ passwordLoading ? '修改中...' : '修改密码' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useUserStore } from '../stores/user'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close', 'success'])

const userStore = useUserStore()
const API_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : 'http://localhost:8000'

const profileForm = ref({
  displayName: '',
  email: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileLoading = ref(false)
const profileError = ref('')
const profileSuccess = ref('')
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

watch(() => props.show, (newVal) => {
  if (newVal) {
    resetForms()
    loadCurrentProfile()
  }
})

function loadCurrentProfile() {
  profileForm.value.displayName = userStore.displayName || ''
  profileForm.value.email = userStore.email || ''
}

function resetForms() {
  profileError.value = ''
  profileSuccess.value = ''
  passwordError.value = ''
  passwordSuccess.value = ''
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}

async function updateProfile() {
  profileLoading.value = true
  profileError.value = ''
  profileSuccess.value = ''

  try {
    const result = await userStore.updateProfile({
      display_name: profileForm.value.displayName || null,
      email: profileForm.value.email || null
    })

    if (result.success) {
      profileSuccess.value = '资料保存成功'
      emit('success')
    } else {
      profileError.value = result.error
    }
  } catch (error) {
    profileError.value = '更新失败，请重试'
  } finally {
    profileLoading.value = false
  }
}

async function changePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
    passwordError.value = '请填写所有密码字段'
    return
  }

  if (passwordForm.value.newPassword.length < 6) {
    passwordError.value = '新密码至少需要6个字符'
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }

  passwordLoading.value = true

  try {
    const response = await fetch(`${API_URL}/api/users/me/password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.accessToken}`
      },
      body: JSON.stringify({
        old_password: passwordForm.value.oldPassword,
        new_password: passwordForm.value.newPassword
      })
    })

    if (response.ok) {
      passwordSuccess.value = '密码修改成功'
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    } else {
      const error = await response.json()
      passwordError.value = error.detail || '密码修改失败'
    }
  } catch (error) {
    passwordError.value = '密码修改失败，请重试'
  } finally {
    passwordLoading.value = false
  }
}

function close() {
  emit('close')
}
</script>
