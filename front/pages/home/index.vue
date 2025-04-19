<template>
  <div class="container">
    <div class="background"></div>
    <h1 class="title">Мои резюме</h1>
    <div class="card-grid">
      <ResumeCard
        v-for="(resume, index) in resumes"
        :key="index"
        :resume="resume"
      />
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: "home-layout",
  private: true,
});

const resumes = ref([
  {
    id: 1,
    title: "Senior Frontend Developer",
    date: "Создано 15.07.2023",
    template: "Modern",
    progress: 92,
    color: "#17837b",
  },
  {
    id: 2,
    title: "UX Team Lead",
    date: "Создано 10.08.2023",
    template: "Creative",
    progress: 60,
    color: "#d1242d",
  },
  // ... больше моковых данных
]);
</script>

<style>
/* Глобальные стили */
:root {
  --primary: #d1242d;
  --secondary: #7ed775;
  --accent: #17837b;
}

.container {
  position: relative;
  min-height: 100vh;
  padding: 4rem 2rem;
  overflow: hidden;
}

.background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #f8f9fa 0%, #e9ecef 100%),
    repeating-radial-gradient(
      circle at 50% 50%,
      rgba(23, 131, 123, 0.05) 0%,
      rgba(23, 131, 123, 0.05) 15%,
      transparent 15%,
      transparent 25%
    );
  background-blend-mode: multiply;
  z-index: -1;
}

.title {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 4rem;
  color: var(--accent);
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2.5rem;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
