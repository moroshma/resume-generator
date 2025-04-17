<template>
  <div>
    <HeaderLayout>
      <template #button>
        <ButtonsPrimaryButton text="Новое резюме" @click="startNewResume">
          <template #icon>
            <PlusIcon />
          </template>
        </ButtonsPrimaryButton>
        <ButtonsPrimaryButton @click="out">
          <template #icon>
            <Logout hoverRed="1" />
          </template>
        </ButtonsPrimaryButton>
        <ButtonsProfile />
      </template>
    </HeaderLayout>
    <slot></slot>
  </div>
</template>

<script setup>
import PlusIcon from "~/assets/icons/PlusIcon.vue";
import HeaderLayout from "./header/HeaderLayout.vue";
import Logout from "~/assets/icons/Logout.vue";
import { useAuth } from "../composables/auth/useAuth";

const emit = defineEmits(["create"]);
const { logout } = useAuth();
const startNewResume = () => {
  navigateTo("/resume");
};

async function out() {
  await logout();
  await navigateTo("/", {
    redirectCode: 302,
    external: true,
  });
}
</script>
