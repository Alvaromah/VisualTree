<template>
    <div>
        <div :class="[
            'tree-item group flex items-center px-2 py-1.5 rounded-md transition-colors duration-150',
            level > 0 ? 'ml-4' : '',
            'hover:bg-gray-50 cursor-pointer'
        ]">
            <!-- Expand/Collapse Button for Folders -->
            <template v-if="item.type === 'folder'">
                <button @click="handleToggleFolder"
                    class="mr-2 p-0.5 rounded-md hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <svg :class="[
                        'w-4 h-4 transition-transform duration-200',
                        isExpanded ? 'transform rotate-90' : ''
                    ]" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M7 5l5 5-5 5z" />
                    </svg>
                </button>
                <svg class="w-5 h-5 text-yellow-500 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2 6a2 2 0 012-2h5l2 2h7a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                </svg>
            </template>
            <template v-else>
                <div class="w-6 mr-2"></div>
                <svg class="w-5 h-5 text-gray-400 mr-2 flex-shrink-0 group-hover:text-gray-500" viewBox="0 0 20 20"
                    fill="currentColor">
                    <path d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                </svg>
            </template>

            <!-- Checkbox -->
            <div @click.stop="handleToggleSelection" class="mr-2 relative flex items-center justify-center">
                <template v-if="item.type === 'folder'">
                    <div :class="[
                        'w-4 h-4 border-2 rounded transition-colors duration-200 flex items-center justify-center',
                        selectionState === 'all' || selectionState === 'some'
                            ? 'border-blue-500 bg-blue-500'
                            : 'border-gray-300 group-hover:border-gray-400'
                    ]">
                        <svg v-if="selectionState === 'all'" class="w-3 h-3 text-white" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                        </svg>
                        <div v-else-if="selectionState === 'some'" class="w-2 h-2 bg-white rounded-sm"></div>
                    </div>
                </template>
                <template v-else>
                    <div :class="[
                        'w-4 h-4 border-2 rounded transition-colors duration-200 flex items-center justify-center',
                        selectedItems.has(item.path)
                            ? 'border-blue-500 bg-blue-500'
                            : 'border-gray-300 group-hover:border-gray-400'
                    ]">
                        <svg v-if="selectedItems.has(item.path)" class="w-3 h-3 text-white" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                        </svg>
                    </div>
                </template>
            </div>

            <!-- Item Name -->
            <span :class="[
                'flex-1 truncate',
                item.type === 'folder' ? 'font-medium' : 'text-gray-600 group-hover:text-gray-900'
            ]" @click="item.type === 'folder' ? handleToggleFolder : handleToggleSelection">
                {{ item.name }}
            </span>
        </div>

        <!-- Render children if folder is expanded -->
        <div v-if="item.type === 'folder' && isExpanded" class="ml-4 mt-0.5 space-y-0.5">
            <TreeItem v-for="child in item.children" :key="child.path" :item="child" :level="level + 1" />
        </div>
    </div>
</template>

<script setup>
import { inject, computed } from 'vue';

defineOptions({
    name: 'TreeItem'
});

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

const selectedItems = inject('selectedItems');
const expandedFolders = inject('expandedFolders');
const toggleSelection = inject('toggleSelection');
const toggleFolder = inject('toggleFolder');
const getSelectionState = inject('getSelectionState');

const isExpanded = computed(() => {
    if (props.item.type === 'folder') {
        return expandedFolders.value.has(props.item.path);
    }
    return false;
});

const selectionState = computed(() => {
    if (props.item.type === 'folder') {
        return getSelectionState(props.item);
    }
    return null;
});

const handleToggleSelection = () => {
    toggleSelection(props.item);
};

const handleToggleFolder = () => {
    toggleFolder(props.item);
};
</script>

<style scoped>
.tree-item {
    user-select: none;
}
</style>