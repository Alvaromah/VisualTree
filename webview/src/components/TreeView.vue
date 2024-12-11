<template>
    <div class="tree-view bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="p-3 border-b border-gray-200">
            <input type="text" placeholder="Filter files..." v-model="filterText"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
        </div>
        <div class="tree-content p-2 max-h-[calc(80vh-4rem)] overflow-y-auto">
            <TreeItem v-for="item in filteredItems" :key="item.path" :item="item" class="first:mt-0" />
        </div>
    </div>
</template>

<script setup>
import { ref, computed, provide } from 'vue';
import TreeItem from './TreeItem.vue';

const props = defineProps({
    items: {
        type: Array,
        required: true
    },
    filter: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['selection-change']);
const filterText = ref('');
const selectedItems = ref(new Set());
const expandedFolders = ref(new Set());

const emitSelection = () => {
    emit('selection-change', Array.from(selectedItems.value));
};

// Provide the state and functions to child components
provide('selectedItems', selectedItems);
provide('expandedFolders', expandedFolders);
provide('toggleSelection', (item) => {
    if (item.type === 'folder') {
        const folderFiles = getAllFiles(item);
        const allSelected = folderFiles.every(file => selectedItems.value.has(file.path));

        if (allSelected) {
            folderFiles.forEach(file => selectedItems.value.delete(file.path));
        } else {
            folderFiles.forEach(file => selectedItems.value.add(file.path));
        }
    } else {
        if (selectedItems.value.has(item.path)) {
            selectedItems.value.delete(item.path);
        } else {
            selectedItems.value.add(item.path);
        }
    }
    emitSelection();
});

provide('toggleFolder', (folder) => {
    if (expandedFolders.value.has(folder.path)) {
        expandedFolders.value.delete(folder.path);
    } else {
        expandedFolders.value.add(folder.path);
    }
});

provide('getSelectionState', (folder) => {
    const files = getAllFiles(folder);
    const selectedCount = files.filter(file => selectedItems.value.has(file.path)).length;

    if (selectedCount === 0) return 'none';
    if (selectedCount === files.length) return 'all';
    return 'some';
});

const getAllFiles = (folder) => {
    const files = [];
    const traverse = (item) => {
        if (item.type === 'file') {
            files.push(item);
        } else if (item.children) {
            item.children.forEach(traverse);
        }
    };
    traverse(folder);
    return files;
};

const patternToRegex = (pattern) => {
    const escaped = pattern.replace(/[-\/\\^$+?.()|[\]{}]/g, '\\$&');
    return new RegExp(
        '^' + escaped
            .replace(/\*/g, '.*')
            .replace(/\?/g, '.') + '$'
    );
};

const filterTree = (items, patterns) => {
    return items
        .map(item => {
            const isExcluded = patterns.some(pattern => pattern.test(item.path));
            if (isExcluded) return null;
            if (item.type === 'folder' && item.children) {
                const filteredChildren = filterTree(item.children, patterns);
                return filteredChildren.length ? { ...item, children: filteredChildren } : null;
            }
            return item;
        })
        .filter(Boolean);
};

const filteredItems = computed(() => {
    if (!filterText.value.trim()) return props.items;

    const patterns = filterText.value
        .split('\n')
        .map(p => p.trim())
        .filter(p => p && !p.startsWith('#'))
        .map(patternToRegex);

    return filterTree(props.items, patterns);
});
</script>

<style scoped>
.tree-content::-webkit-scrollbar {
    width: 8px;
}

.tree-content::-webkit-scrollbar-track {
    @apply bg-gray-100 rounded-lg;
}

.tree-content::-webkit-scrollbar-thumb {
    @apply bg-gray-300 rounded-lg hover:bg-gray-400 transition-colors;
}
</style>