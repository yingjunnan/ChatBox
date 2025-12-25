<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="close">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">{{ isLogin ? '登录' : '注册' }}</h2>
        <button @click="close" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
      </div>

      <div class="flex mb-6 border-b">
        <button
          @click="isLogin = true"
          class="flex-1 py-2 text-center font-medium transition-colors"
          :class="isLogin ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'"
        >
          登录
        </button>
        <button
          @click="isLogin = false"
          class="flex-1 py-2 text-center font-medium transition-colors"
          :class="!isLogin ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'"
        >
          注册
        </button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              v-model="formData.username"
              type="text"
              required
              minlength="3"
              maxlength="20"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="formData.password"
              type="password"
              required
              minlength="6"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="请输入密码（至少6位）"
            />
          </div>

          <div v-if="!isLogin">
            <label class="block text-sm font-medium text-gray-700 mb-1">显示名称（可选）</label>
            <input
              v-model="formData.displayName"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="聊天时显示的名称"
            />
          </div>

          <div v-if="!isLogin">
            <label class="block text-sm font-medium text-gray-700 mb-1">邮箱（可选）</label>
            <input
              v-model="formData.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="your@email.com"
            />
          </div>

          <div v-if="errorMessage" class="text-red-600 text-sm">
            {{ errorMessage }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          >
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </div>
      </form>

      <div class="mt-4 text-center">
        <button @click="continueAsGuest" class="text-sm text-gray-600 hover:text-gray-800">
          继续作为游客
        </button>
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
const isLogin = ref(true)
const loading = ref(false)
const errorMessage = ref('')

const formData = ref({
  username: '',
  password: '',
  displayName: '',
  email: ''
})

watch(() => props.show, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

function resetForm() {
  formData.value = {
    username: '',
    password: '',
    displayName: '',
    email: ''
  }
  errorMessage.value = ''
  loading.value = false
}

async function handleSubmit() {
  loading.value = true
  errorMessage.value = ''

  try {
    let result
    if (isLogin.value) {
      result = await userStore.login(formData.value.username, formData.value.password)
    } else {
      result = await userStore.register(
        formData.value.username,
        formData.value.password,
        formData.value.displayName || null,
        formData.value.email || null
      )
    }

    if (result.success) {
      emit('success')
      close()
    } else {
      errorMessage.value = result.error
    }
  } catch (error) {
    errorMessage.value = '操作失败，请重试'
  } finally {
    loading.value = false
  }
}

function close() {
  emit('close')
}

function continueAsGuest() {
  close()
}
</script>
