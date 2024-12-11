<template>
    <div class="tree-view bg-white rounded-lg shadow-sm border border-gray-200 h-full">
        <div class="p-3 space-y-3 border-b border-gray-200">
            <!-- Include Filter -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Include patterns</label>
                <input type="text" placeholder="e.g. *.js; *.vue; src/*" v-model="includeFilter"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" />
            </div>

            <!-- Exclude Filter -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Exclude patterns</label>
                <input type="text" placeholder="e.g. node_modules/*; *.test.js" v-model="excludeFilter"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm" />
            </div>
        </div>

        <div class="tree-content p-2 overflow-y-auto">
            <TreeItem v-for="item in filteredAndSortedItems" :key="item.path" :item="item" class="first:mt-0" />
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
    }
});

const emit = defineEmits(['selection-change']);
const includeFilter = ref('');
const excludeFilter = ref('');
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

// Convert glob pattern to regex
const globToRegex = (pattern) => {
    const escaped = pattern
        .trim()
        .replace(/[.+^${}()|[\]\\]/g, '\\$&') // Escape special regex chars
        .replace(/\*/g, '.*') // Convert * to .*
        .replace(/\?/g, '.'); // Convert ? to .
    return new RegExp(`^${escaped}$`);
};

// Sort function for items
const sortItems = (items) => {
    return [...items].sort((a, b) => {
        // Sort folders first
        if (a.type === 'folder' && b.type !== 'folder') return -1;
        if (a.type !== 'folder' && b.type === 'folder') return 1;

        // Then sort alphabetically
        return a.name.localeCompare(b.name);
    });
};

// Recursive sort function that handles nested folders
const sortTreeItems = (items) => {
    return sortItems(items).map(item => {
        if (item.type === 'folder' && item.children) {
            return {
                ...item,
                children: sortTreeItems(item.children)
            };
        }
        return item;
    });
};

const filterTree = (items, includePatterns, excludePatterns) => {
    return items
        .map(item => {
            // Check if item should be excluded
            const isExcluded = excludePatterns.length > 0 &&
                excludePatterns.some(pattern => pattern.test(item.path));

            if (isExcluded) return null;

            // Check if item should be included
            const shouldInclude = includePatterns.length === 0 ||
                includePatterns.some(pattern => pattern.test(item.path));

            if (item.type === 'folder' && item.children) {
                const filteredChildren = filterTree(item.children, includePatterns, excludePatterns);
                // Keep folder if it has matching children or if it matches include patterns
                return filteredChildren.length > 0 || shouldInclude
                    ? { ...item, children: filteredChildren }
                    : null;
            }

            return shouldInclude ? item : null;
        })
        .filter(Boolean);
};

const filteredAndSortedItems = computed(() => {
    // Convert include patterns to regex
    const includePatterns = includeFilter.value
        ? includeFilter.value
            .split(';')
            .map(p => p.trim())
            .filter(Boolean)
            .map(globToRegex)
        : [];

    // Convert exclude patterns to regex
    const excludePatterns = excludeFilter.value
        ? excludeFilter.value
            .split(';')
            .map(p => p.trim())
            .filter(Boolean)
            .map(globToRegex)
        : [];

    // First filter, then sort
    const filteredItems = filterTree(props.items, includePatterns, excludePatterns);
    return sortTreeItems(filteredItems);
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