<template>
  <button class="profile-btn" @click="navigateToAuth">
    <svg class="profile-icon" viewBox="0 0 24 24">
      <path
        d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"
      />
    </svg>
  </button>
</template>

<script setup>
const navigateToAuth = () => {
  navigateTo("/home/profile");
};
</script>

<style scoped>
.profile-btn {
  cursor: pointer;
  padding: 0.3rem;
  background: none;
  border: 2px solid var(--main-green);
  transition: all 0.3s ease;
  border-radius: 5px;
}

.profile-btn:hover {
  border-color: var(--main-green);
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(148, 163, 184, 0.2);
}

.profile-btn:hover .profile-icon {
  fill: var(--main-red);
}

.profile-icon {
  width: 1.5rem;
  height: 1.5rem;
  fill: #475569;
}
</style>
