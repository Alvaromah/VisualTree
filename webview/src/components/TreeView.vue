<template>
    <div class="tree-view">
        <TreeItem v-for="item in filteredItems" :key="item.path" :item="item" />
    </div>
</template>

<script setup>
import { ref, computed, provide } from 'vue';
import TreeItem from './TreeItem.vue'; // Ensure the correct path

// Define props
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

// Define emits
const emit = defineEmits(['selection-change']);

// Reactive sets for selection and expansion
const selectedItems = ref(new Set());
const expandedFolders = ref(new Set());

// Function to emit selection changes
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
            // Deselect all
            folderFiles.forEach(file => selectedItems.value.delete(file.path));
        } else {
            // Select all
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

// Function to get all files under a folder recursively
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

// Convert .gitignore style pattern to regex
const patternToRegex = (pattern) => {
    // Escape regex special characters except for * and ?
    const escaped = pattern.replace(/[-\/\\^$+?.()|[\]{}]/g, '\\$&');
    return new RegExp(
        '^' + escaped
            .replace(/\*/g, '.*')
            .replace(/\?/g, '.') + '$'
    );
};

// Functional filter to filter the tree
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

// Compute the filtered items
const filteredItems = computed(() => {
    if (!props.filter.trim()) return props.items;

    const patterns = props.filter
        .split('\n')
        .map(p => p.trim())
        .filter(p => p && !p.startsWith('#'))
        .map(patternToRegex);

    return filterTree(props.items, patterns);
});
</script>

<style scoped>
.tree-view {
    max-height: 80vh;
    overflow-y: auto;
}
</style>