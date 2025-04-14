<script setup>
defineProps({
  text: String,
});
</script>

<template>
  <button class="primary-btn">
    <span v-if="$slots.icon" class="btn-icon" style="margin-right: 0px">
      <slot name="icon"></slot>
    </span>
    {{ text }}
  </button>
</template>

<style>
.primary-btn {
  background: #17837b;
  color: white;
  padding: 0.75rem 1.4rem;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.primary-btn:hover {
  background: #12665f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(23, 131, 123, 0.2);
}

.primary-btn:hover .icon {
  stroke: var(--main-red);
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  stroke: currentColor;
}

@media (max-width: 768px) {
  .primary-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
}
</style>
