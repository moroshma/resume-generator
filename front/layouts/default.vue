<template>
  <div>
    <HeaderLayout>
      <template #button>
        <ButtonsPrimaryButton @click="goHome" text="Начать работу" />
      </template>
    </HeaderLayout>
    <slot></slot>
  </div>
</template>

<script setup>
import HeaderLayout from "./header/HeaderLayout.vue";

const goHome = () => {
  navigateTo("/home");
};
</script>
