<script setup>
import { ref, onMounted, inject } from 'vue';
import TreeView from './components/TreeView.vue';

// Inject vscode API instead of using props
const vscode = inject('vscode');

const items = ref([]);
const selectedPaths = ref([]);
const filterPattern = ref('');

const handleSelectionChange = (paths) => {
    selectedPaths.value = paths;
};

const showSelectedContent = () => {
    if (selectedPaths.value.length > 0) {
        vscode?.postMessage({
            command: 'showSelected',
            paths: selectedPaths.value
        });
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
        switch (message.command) {
            case 'setFiles':
                console.log('Received files:', message.files);
                items.value = message.files;
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
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="selectedPaths.length === 0">
                Show Selected Content ({{ selectedPaths.length }} files)
            </button>
        </div>

        <div class="border rounded-md">
            <TreeView :items="items" :filter="filterPattern" @selection-change="handleSelectionChange" />
        </div>
    </div>
</template>
