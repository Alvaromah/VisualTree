<template>
    <div>
        <div :class="[
            'tree-item flex items-center p-1 hover:bg-gray-100',
            { 'ml-4 cursor-pointer': level > 0 }
        ]">
            <!-- Expand/Collapse Button for Folders -->
            <template v-if="item.type === 'folder'">
                <button @click="handleToggleFolder" class="mr-2 focus:outline-none">
                    <svg v-if="isExpanded" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
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
            <template v-else>
                <svg class="w-5 h-5 text-gray-500 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                </svg>
            </template>

            <!-- Checkbox -->
            <div @click.stop="handleToggleSelection" class="mr-2">
                <template v-if="item.type === 'folder'">
                    <div v-if="selectionState === 'all'"
                        class="w-4 h-4 border-2 border-blue-500 bg-blue-500 flex items-center justify-center">
                        <svg class="w-3 h-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                            <path
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                        </svg>
                    </div>
                    <div v-else-if="selectionState === 'some'"
                        class="w-4 h-4 border-2 border-blue-500 bg-blue-500 flex items-center justify-center">
                        <div class="w-2 h-2 bg-white"></div>
                    </div>
                    <div v-else class="w-4 h-4 border-2 border-gray-300"></div>
                </template>
                <template v-else>
                    <div class="w-4 h-4 border-2 flex items-center justify-center"
                        :class="[selectedItems.has(item.path) ? 'border-blue-500 bg-blue-500' : 'border-gray-300']">
                        <svg v-if="selectedItems.has(item.path)" class="w-3 h-3 text-white" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                        </svg>
                    </div>
                </template>
            </div>

            <!-- Item Name -->
            <span v-if="item.type === 'folder'" @click="handleToggleFolder" class="flex-1">{{ item.name }}</span>
            <span v-else class="flex-1">{{ item.name }}</span>
        </div>

        <!-- Render children if folder is expanded -->
        <div v-if="item.type === 'folder' && isExpanded" class="ml-4">
            <TreeItem v-for="child in item.children" :key="child.path" :item="child" :level="level + 1" />
        </div>
    </div>
</template>

<script setup>
import { inject, computed } from 'vue';

// Define the component name for recursive reference
defineOptions({
    name: 'TreeItem'
});

// Define props
const props = defineProps({
    item: {
        type: Object,
        required: true
    },
    level: {
        type: Number,
        default: 0
    }
});

// Inject the provided state and functions
const selectedItems = inject('selectedItems');
const expandedFolders = inject('expandedFolders');
const toggleSelection = inject('toggleSelection');
const toggleFolder = inject('toggleFolder');
const getSelectionState = inject('getSelectionState');

// Determine if the folder is expanded
const isExpanded = computed(() => {
    if (props.item.type === 'folder') {
        return expandedFolders.value.has(props.item.path);
    }
    return false;
});

// Get the selection state for the folder
const selectionState = computed(() => {
    if (props.item.type === 'folder') {
        return getSelectionState(props.item);
    }
    return null;
});

// Function to handle selection toggle
const handleToggleSelection = () => {
    toggleSelection(props.item);
};

// Function to handle folder toggle
const handleToggleFolder = () => {
    toggleFolder(props.item);
};
</script>

<style scoped>
.tree-item {
    user-select: none;
}
</style>