<template>
  <div class="text-question">
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      @input="$emit('update:modelValue', $event.target.value)"
      class="answer-input"
      rows="3"
    />
  </div>
</template>

<script setup>
defineProps({
  placeholder: {
    type: String,
    default: "Введите ваш ответ...",
  },
  modelValue: String,
});

defineEmits(["update:modelValue"]);
</script>

<style scoped>
.answer-input {
  max-width: 100%;
  min-width: 100%;
  min-height: 85px;
  padding: 1rem 0rem 1rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.answer-input:focus {
  border-color: #17837b;
  outline: none;
  box-shadow: 0 0 0 3px rgba(23, 131, 123, 0.1);
}
</style>
