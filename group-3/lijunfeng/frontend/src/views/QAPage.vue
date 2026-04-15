<template>
  <div class="qa-page">
    <SessionSidebar />
    <div class="qa-main">
      <ChatArea @suggest="handleSuggest" />
      <InputArea ref="inputRef" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SessionSidebar from '../components/SessionSidebar.vue'
import ChatArea from '../components/ChatArea.vue'
import InputArea from '../components/InputArea.vue'

const inputRef = ref(null)

const handleSuggest = (text) => {
  if (inputRef.value) {
    inputRef.value.setSuggestion(text)
  }
}
</script>

<style scoped>
.qa-page {
  display: flex;
  height: 100%;
}
.qa-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
</style>
