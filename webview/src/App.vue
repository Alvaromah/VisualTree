<script setup>
import { ref, onMounted } from 'vue';
import TreeView from './components/TreeView.vue';

const props = defineProps({
    vscode: {
        type: Object,
        required: true
    }
});

const items = ref([]);
const selectedPaths = ref([]);
const filterPattern = ref('');

// Ensure we're getting the full paths array
const handleSelectionChange = (paths) => {
    console.log('Selection changed:', paths); // Debug log
    selectedPaths.value = paths;
};

const showSelectedContent = () => {
    console.log('Showing content for paths:', selectedPaths.value); // Debug log
    if (selectedPaths.value.length > 0) {
        props.vscode?.postMessage({
            command: 'showSelected',
            paths: selectedPaths.value
        });
    }
};

// Modified to explicitly declare vscode from acquireVsCodeApi
const vscode = typeof acquireVsCodeApi !== 'undefined' ? acquireVsCodeApi() : undefined;

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