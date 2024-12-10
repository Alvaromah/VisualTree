<template>
    <div class="p-4">
        <h1 class="text-2xl font-bold mb-4">{{ message }}</h1>
        <button @click="sendMessage" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Send Message
        </button>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
    vscode: {
        type: Object,
        required: true
    }
})

const message = ref('Hello from Vue + Tailwind!')

// Ejemplo de envío de mensaje a la extensión
const sendMessage = () => {
    props.vscode.postMessage({
        command: 'alert',
        text: message.value
    })
}

onMounted(() => {
    console.log('App mounted')
})
</script>
