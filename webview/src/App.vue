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

const handleSelectionChange = (paths) => {
    selectedPaths.value = paths;
};

const showSelectedContent = () => {
    props.vscode.postMessage({
        command: 'showSelected',
        paths: selectedPaths.value
    });
};

onMounted(() => {
    // Listen for messages from extension
    window.addEventListener('message', event => {
        const message = event.data;
        switch (message.command) {
            case 'setFiles':
                items.value = message.files;
                break;
        }
    });

    // Request initial file tree
    props.vscode.postMessage({
        command: 'getFiles'
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
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                :disabled="selectedPaths.length === 0">
                Show Selected Content
            </button>
        </div>

        <div class="border rounded-md">
            <TreeView :items="items" :filter="filterPattern" @selection-change="handleSelectionChange" />
        </div>
    </div>
</template>
