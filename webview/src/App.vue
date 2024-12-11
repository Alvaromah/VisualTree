<script setup>
import { ref, onMounted, inject } from 'vue';
import TreeView from './components/TreeView.vue';

const vscode = inject('vscode');
const items = ref([]);
const selectedPaths = ref([]);
const filterPattern = ref('');
const isLoading = ref(false);

const handleSelectionChange = async (paths) => {
    await vscode.postMessage({
        command: 'ppSelected',
        paths: paths
    });


    console.log('Selection changed:', paths);
    selectedPaths.value = paths;
};

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

onMounted(() => {
    // Request initial file tree
    vscode?.postMessage({
        command: 'getFiles'
    });

    // Listen for messages from extension
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
        }
    });
});
</script>

<template>
    <div class="p-4">
        <div class="mb-4">
            <textarea v-model="filterPattern" placeholder="Enter .gitignore style patterns..."
                class="w-full p-2 border rounded-md h-20 text-sm font-mono"></textarea>
        </div>

        <div class="mb-4">
            <button @click="showSelectedContent"
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center">
                <span v-if="isLoading" class="mr-2">Loading...</span>
                <span>Show Selected Content ({{ selectedPaths.length }} files)</span>
            </button>
        </div>

        <div class="border rounded-md">
            <TreeView :items="items" :filter="filterPattern" @selection-change="handleSelectionChange" />
        </div>
    </div>
</template>