<template>
  <div class="editable-field" @dblclick="enableEdit">
    <div v-if="!isEditing" class="view-mode">
      <span v-if="icon" class="icon">{{ icon }}</span>
      {{ model || placeholder }}
    </div>
    <component
      v-else
      :is="inputComponent"
      ref="inputRef"
      v-model="localValue"
      :value="localValue"
      :type="type"
      :placeholder="placeholder"
      @blur="saveChanges"
      @keyup.enter="saveChanges"
      class="edit-mode"
      @input="handleInput"
    />
  </div>
</template>

<script setup>
const props = defineProps({
  label: String,
  type: {
    type: String,
    default: "text",
  },
  icon: String,
  placeholder: String,
});

const model = defineModel();

const isEditing = ref(false);
const inputRef = ref(null);
const localValue = ref(model.value);

const inputComponent = computed(() =>
  props.type === "textarea" ? "textarea" : "input"
);

const handleInput = (e) => {
  localValue.value = e.target.value;
};

const enableEdit = async () => {
  isEditing.value = true;
  await nextTick();
  if (inputRef.value?.select) {
    inputRef.value.select();
  }
};

const saveChanges = () => {
  isEditing.value = false;

  if (localValue.value !== model.value) {
    model.value = localValue.value;
  }
};
</script>

<style scoped>
.editable-field {
  position: relative;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.view-mode {
  cursor: text;
  padding: 0.3rem 0.5rem;
  border: 1px solid transparent;
}

.view-mode:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.edit-mode {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-family: inherit;
  font-size: inherit;
}

.edit-mode:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.icon {
  margin-right: 0.5rem;
  opacity: 0.6;
}
</style>
