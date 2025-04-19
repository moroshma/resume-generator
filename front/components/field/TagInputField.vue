<template>
  <div class="tag-input">
    <div v-for="(tag, index) in modelValue" :key="index" class="tag">
      {{ tag }}
      <button @click="removeTag(index)" class="remove-btn">×</button>
    </div>
    <input
      v-model="newTag"
      type="text"
      placeholder="Добавить язык"
      @keydown.enter="addTag"
      class="input"
    />
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);

const newTag = ref("");

const addTag = () => {
  if (newTag.value.trim()) {
    emit("update:modelValue", [...props.modelValue, newTag.value.trim()]);
    newTag.value = "";
  }
};

const removeTag = (index) => {
  const newTags = props.modelValue.filter((_, i) => i !== index);
  emit("update:modelValue", newTags);
};
</script>

<style scoped>
.tag-input {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.tag {
  background: #e2e8f0;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remove-btn {
  border: none;
  background: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
}

.input {
  border: none;
  padding: 0.5rem;
  background: transparent;
  outline: none;
}
</style>
