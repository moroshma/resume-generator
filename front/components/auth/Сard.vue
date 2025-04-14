<template>
  <div class="auth-card">
    <div class="forms-container" :class="formType">
      <div class="form login-form">
        <h2>Вход</h2>
        <input type="login" v-model="userAuth.login" placeholder="Email" />
        <input
          type="password"
          v-model="userAuth.password"
          placeholder="Пароль"
        />
        <button
          class="primary-btn"
          @click="emit('submit', { ...userAuth, type: 'login' })"
        >
          Войти
        </button>
        <transition name="scroll">
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </transition>

        <button class="switch-btn" @click="switchForm('register')">
          Нет аккаунта? Зарегистрироваться →
        </button>
      </div>

      <div class="form register-form">
        <h2>Регистрация</h2>
        <input type="login" v-model="userAuth.login" placeholder="Логин" />
        <input
          type="password"
          v-model="userAuth.password"
          placeholder="Пароль"
        />
        <button
          class="primary-btn"
          @click="emit('submit', { ...userAuth, type: 'register' })"
        >
          Создать аккаунт
        </button>
        <transition name="scroll">
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </transition>

        <button class="switch-btn" @click="switchForm('login')">
          Уже есть аккаунт? Войти →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  formType: {
    type: String,
    default: "login",
  },
  error: String,
});

const userAuth = ref({
  login: "",
  password: "",
});

const emit = defineEmits(["switch-form", "submit"]);

const switchForm = (type) => {
  emit("switch-form", type);
};
</script>

<style scoped>
.scroll-enter-active,
.scroll-leave-active {
  transition: max-height 0.5s ease-in-out, opacity 0.3s ease 0.2s;
  max-height: 100px;
  overflow: hidden;
}

.scroll-enter-from,
.scroll-leave-to {
  max-height: 0;
  opacity: 0;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px 20px;
  border-radius: 8px;
  margin: 15px 0;
  border: 1px solid #fecaca;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-message::before {
  content: "!";
  background: #dc2626;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}
.auth-card {
  position: relative;
  width: 400px;
  height: 500px;
  perspective: 1000px;
  transform: translateZ(50px);
}

.forms-container {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.8s;
  transform-style: preserve-3d;
}

.form {
  will-change: transform;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.login-form {
  transform: rotateY(0deg);
}

.register-form {
  transform: rotateY(180deg);
}

.forms-container.register {
  transform: rotateY(180deg);
}

.forms-container.login {
  transform: rotateY(0deg);
}

h2 {
  color: #2c3e50;
  font-size: 24px;
  margin-bottom: 10px;
}

input {
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  border-color: #3498db;
  outline: none;
}

.primary-btn {
  justify-content: center;
  background: #3498db;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.primary-btn:hover {
  background: #2980b9;
}

.switch-btn {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  padding: 10px 0;
  margin-top: auto;
  transition: color 0.3s;
}

.switch-btn:hover {
  color: #2980b9;
  text-decoration: underline;
}
</style>
