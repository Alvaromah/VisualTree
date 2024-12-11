<template>
    <div class="p-4">
        <!-- Show Selected Content Button -->
        <div class="mb-4">
            <button @click="showSelectedContent" :disabled="isLoading || selectedPaths.length === 0"
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center">
                <span v-if="isLoading" class="mr-2">Loading...</span>
                <span>Show Selected Content ({{ selectedPaths.length }} files)</span>
            </button>
        </div>

        <!-- Tree View -->
        <div class="border rounded-md">
            <TreeView :items="items" :filter="filterPattern" @selection-change="handleSelectionChange" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, inject, watch } from 'vue';
import TreeView from './components/TreeView.vue';

// Inject the vscode API
const vscode = inject('vscode');

// Reactive state
const items = ref([]);
const selectedPaths = ref([]);
const filterPattern = ref('*.gitignore');
const isLoading = ref(false);

// Handle selection changes emitted from TreeView
const handleSelectionChange = (paths) => {
    selectedPaths.value = paths;
    vscode?.postMessage({
        command: 'ppSelected',
        paths: paths
    });
    console.log('Selection changed:', paths);
};

// Show selected content
const showSelectedContent = async () => {
    if (selectedPaths.value.length === 0) return;

    isLoading.value = true;
    try {
        const serializedPaths = JSON.stringify(selectedPaths.value);
        await vscode.postMessage({
            command: 'showSelected',
            paths: serializedPaths
        });
    } catch (error) {
        console.error('Error showing content:', error);
    } finally {
        isLoading.value = false;
    }
};

// Fetch initial file tree and set up message listener
onMounted(() => {
    // Request initial file tree
    vscode?.postMessage({
        command: 'getFiles'
    });

    // Listen for messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        console.log('Received message:', message);

        switch (message.command) {
            case 'setFiles':
                items.value = message.files;
                break;
            case 'error':
                console.error('Error from extension:', message.error);
                break;
            default:
                console.warn('Unknown command:', message.command);
        }
    });
});
</script>

<style scoped>
/* Optional: Add some basic styling */
textarea {
    resize: vertical;
}
</style>
