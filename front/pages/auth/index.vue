<template>
  <div class="auth-page">
    <div class="auth-container">
      <AuthСard
        :form-type="activeForm"
        @switch-form="handleFormSwitch"
        @submit="auth"
      />
    </div>
  </div>
</template>

<script setup>
import { useAuth } from "~/composables/auth/useAuth";

definePageMeta({
  layout: "auth",
});

const activeForm = ref("login");

const auth = async (userAuthData) => {
  const { register, login } = useAuth();
  const { login: loginData, password, type } = userAuthData;
  let response;

  if (type === "login") {
    response = await login(loginData, password);
  } else if (type === "register") {
    response = await register(loginData, password);
  }
  let status = response.status;
  if (status === 200 || status === 201) {
    navigateTo("/home");
  }
};

const handleFormSwitch = (type) => {
  activeForm.value = type;
};
</script>

<style>
.auth-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(-45deg, #ee7752, #d1242d, #7ed775, #17837b);
  background-size: 400% 400%;
  animation: gradient 45s ease infinite;
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
