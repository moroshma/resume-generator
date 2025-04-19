<template>
  <div class="date-range">
    <EditableField
      v-model="model.from"
      placeholder="Начало"
      type="month"
      class="date-input"
    />
    <span class="separator">—</span>
    <EditableField
      v-model="model.to"
      placeholder="Окончание"
      type="month"
      class="date-input"
    />
  </div>
</template>

<script setup>
defineProps({
  model: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped>
.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-input {
  flex: 1;
}

.separator {
  color: #94a3b8;
  padding: 0 0.5rem;
}
</style>
