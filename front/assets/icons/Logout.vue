<template>
  <svg
    :width="size"
    :height="size"
    viewBox="4 2 24 24"
    class="icon logout-icon"
  >
    <path
      d="M15 3H19C20.1 3 21 3.9 21 5V19C21 20.1 20.1 21 19 21H15M10 17L15 12M15 12L10 7M15 12H3"
    />
  </svg>
</template>

<script setup>
defineProps({
  size: {
    type: [Number, String],
    default: 26,
  },
});
</script>

<style>
.logout-icon {
  fill: none;
  stroke: #fff;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: stroke 0.2s ease;
}
</style>
