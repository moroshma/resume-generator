<template>
  <div class="container">
    <div class="background"></div>
    <h1 class="title">Мои резюме</h1>
    <div v-if="error">По техническим причинам возникла ошибка</div>

    <div v-else-if="resumes?.length === 0 || !resumes" class="empty-state">
      <div class="empty-state-icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m9.75 9.75h-4.5M19.5 14.25v5.25a2.25 2.25 0 0 1-2.25 2.25H6.75a2.25 2.25 0 0 1-2.25-2.25V6.75a2.25 2.25 0 0 1 2.25-2.25h3"
          />
        </svg>
      </div>
      <h2 class="empty-state-title">Пока здесь пусто</h2>
      <p class="empty-state-text">
        У вас еще нет созданных резюме. Начните создавать свое первое прямо
        сейчас!
      </p>
      <ButtonsPrimaryButton
        text="Создать резюме"
        @click="navigateToCreateResume"
      />
    </div>

    <div v-else class="card-grid">
      <ResumeCard
        v-for="(resume, index) in resumes"
        :key="index"
        :resume="resume"
        @export-resume="handleExport"
        @delete-resume="handleDelete"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useResume } from "~/composables/resume/useResume";

definePageMeta({
  layout: "home-layout",
  private: true,
});

const {
  data: resumes,
  error,
  refresh,
} = useFetch<IResumePreview[]>("/api/resume/list");

const { exportResume, deleteResume } = useResume();

function navigateToCreateResume() {
  navigateTo("/resume");
}

function handleExport(id: number) {
  exportResume(id);
}

async function handleDelete(id: number) {
  await deleteResume(id);
  refresh();
}
</script>

<style>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 4rem 2rem; /* Отступы сверху/снизу и по бокам */
  margin-top: 2rem; /* Отступ от заголовка "Мои резюме" */
  background-color: rgba(255, 255, 255, 0.6); /* Полупрозрачный белый фон */
  border-radius: 20px; /* Скругление углов как у карточек */
  max-width: 600px; /* Ограничиваем ширину блока */
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05); /* Легкая тень */
  border: 1px solid rgba(0, 0, 0, 0.05); /* Тонкая граница */
}

.empty-state-icon {
  margin-bottom: 1.5rem;
}

.empty-state-icon svg {
  width: 80px; /* Размер иконки */
  height: 80px;
  stroke: var(--accent); /* Цвет иконки - ваш акцентный */
  opacity: 0.5; /* Делаем иконку немного бледнее */
}

.empty-state-title {
  font-size: 1.8rem; /* Размер заголовка */
  color: #333; /* Темно-серый цвет */
  margin-bottom: 0.8rem;
  font-weight: 600;
}

.empty-state-text {
  font-size: 1rem;
  color: #666; /* Серый цвет */
  max-width: 400px; /* Ограничиваем ширину текста */
  margin-bottom: 2rem; /* Отступ перед кнопкой */
  line-height: 1.6;
}
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
