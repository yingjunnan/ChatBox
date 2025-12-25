<script setup>
import { RouterView } from 'vue-router'
import { useUserStore } from './stores/user'
import { onMounted } from 'vue'

const userStore = useUserStore()

onMounted(() => {
  userStore.loadUsername()
})
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <RouterView />
  </div>
</template>
