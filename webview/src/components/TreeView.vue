<script setup>
import { ref, computed, watch } from 'vue';

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

const emit = defineEmits(['selectionChange']);

const selectedItems = ref(new Set());
const expandedFolders = ref(new Set());

// Watch selectedItems and emit changes
watch(selectedItems, (newVal) => {
    emit('selectionChange', Array.from(newVal));
}, { deep: true });

// Convert .gitignore style pattern to regex
const patternToRegex = (pattern) => {
    return new RegExp(
        pattern
            .replace(/\./g, '\\.')
            .replace(/\*/g, '.*')
            .replace(/\?/g, '.')
    );
};

// Filter items based on .gitignore style patterns
const filteredItems = computed(() => {
    if (!props.filter.trim()) return props.items;

    const patterns = props.filter
        .split('\n')
        .map(p => p.trim())
        .filter(p => p && !p.startsWith('#'))
        .map(patternToRegex);

    const filterItem = (item) => {
        const isExcluded = patterns.some(pattern => pattern.test(item.path));
        if (isExcluded) return false;

        if (item.type === 'folder') {
            item.children = item.children.filter(filterItem);
            return item.children.length > 0;
        }
        return true;
    };

    return JSON.parse(JSON.stringify(props.items)).filter(filterItem);
});

const toggleSelection = (item) => {
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

    // Force emit current selection
    emit('selectionChange', Array.from(selectedItems.value));
};

const toggleFolder = (folder) => {
    if (expandedFolders.value.has(folder.path)) {
        expandedFolders.value.delete(folder.path);
    } else {
        expandedFolders.value.add(folder.path);
    }
};

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

const getSelectionState = (folder) => {
    const files = getAllFiles(folder);
    const selectedCount = files.filter(file => selectedItems.value.has(file.path)).length;

    if (selectedCount === 0) return 'none';
    if (selectedCount === files.length) return 'all';
    return 'some';
};
</script>

<template>
    <div class="tree-view">
        <template v-for="item in filteredItems" :key="item.path">
            <div :class="[
                'tree-item flex items-center p-1 hover:bg-gray-100 cursor-pointer',
                { 'ml-4': item.level > 0 }
            ]">
                <!-- Folder/File Icon -->
                <template v-if="item.type === 'folder'">
                    <button @click="toggleFolder(item)" class="mr-2">
                        <svg v-if="expandedFolders.has(item.path)" class="w-4 h-4" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path d="M5 7l5 5 5-5z" />
                        </svg>
                        <svg v-else class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M7 5l5 5-5 5z" />
                        </svg>
                    </button>
                    <svg class="w-5 h-5 text-yellow-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M2 6a2 2 0 012-2h5l2 2h7a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                    </svg>
                </template>
                <svg v-else class="w-5 h-5 text-gray-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                </svg>

                <!-- Checkbox -->
                <div @click.stop="toggleSelection(item)" class="mr-2">
                    <template v-if="item.type === 'folder'">
                        <div v-if="getSelectionState(item) === 'all'"
                            class="w-4 h-4 border-2 border-blue-500 bg-blue-500">
                            <svg class="w-3 h-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                                <path
                                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                            </svg>
                        </div>
                        <div v-else-if="getSelectionState(item) === 'some'"
                            class="w-4 h-4 border-2 border-blue-500 bg-blue-500">
                            <div class="w-2 h-2 bg-white m-auto"></div>
                        </div>
                        <div v-else class="w-4 h-4 border-2 border-gray-300"></div>
                    </template>
                    <div v-else class="w-4 h-4 border-2"
                        :class="[selectedItems.has(item.path) ? 'border-blue-500 bg-blue-500' : 'border-gray-300']">
                        <svg v-if="selectedItems.has(item.path)" class="w-3 h-3 text-white" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                        </svg>
                    </div>
                </div>

                <!-- Item Name -->
                <span @click="toggleFolder(item)">{{ item.name }}</span>
            </div>

            <!-- Recursively render children if folder is expanded -->
            <template v-if="item.type === 'folder' && expandedFolders.has(item.path)">
                <div v-for="child in item.children" :key="child.path" class="ml-4">
                    <TreeView :items="[child]" :filter="filter" @selection-change="emit('selectionChange', $event)" />
                </div>
            </template>
        </template>
    </div>
</template>
