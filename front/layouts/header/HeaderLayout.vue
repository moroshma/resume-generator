<template>
  <header class="header">
    <div class="header-content">
      <NuxtLink to="/home" class="logo">
        <span class="logo-accent">C</span>Vibe
      </NuxtLink>

      <div class="buttons">
        <slot name="button"></slot>
      </div>
    </div>
  </header>
</template>

<style scoped>
.buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}
.header {
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.logo {
  font-size: 2.5rem;
  font-weight: 700;
  text-decoration: none;
  color: #2d3748;
  transition: color 0.3s ease;
}

.logo-accent {
  color: #d1242d;
}

.create-btn {
  background: #17837b;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.create-btn:hover {
  background: #12665f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(23, 131, 123, 0.2);
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  stroke: currentColor;
}

@media (max-width: 768px) {
  .header-content {
    padding: 1rem;
  }

  .create-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }

  .logo {
    font-size: 1.25rem;
  }
}
</style>
