<template>
  <div class="container">
    <ProgressBar
      :totalSteps="3"
      :answered-questions="answeredCount"
      :total-questions="totalQuestions"
      :current-step="stepNumber"
      alignment="left"
    />
    <component
      :draft="{
        questions,
        answers,
        labels,
      }"
      :is="step.component.value"
    ></component>

    <ButtonsPrimaryButton
      text="Продолжить"
      @click="nextStep"
      style="align-self: center; margin-top: 20px"
    />
  </div>
</template>
<script setup>
import { useDraft } from "~/composables/resume/useDraft";

const {
  initQuestions,
  generateLabels,
  questions,
  getNextQuestions,
  isLoading,
  answers,
  answeredCount,
  totalQuestions,
  labels,
  step,
  nextStep,
  stepNumber,
} = useDraft();

onMounted(async () => {
  await initQuestions();
});

watch(stepNumber, async (newVal, oldVal) => {
  if (newVal !== oldVal) {
    await nextTick();
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }
});

definePageMeta({
  layout: "resume-generator-layout",
  private: true,
});
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  position: relative;
  max-width: 60%;
  margin: 2rem auto;
  padding: 2rem;
}

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 3rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7ed775, #17837b);
  transition: width 0.5s ease;
}

.navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 3rem;
}

.nav-button {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.next {
  background: #17837b;
  color: white;
}

.next:disabled {
  background: #e2e8f0;
  color: #a0aec0;
  cursor: not-allowed;
}

.prev {
  background: none;
  color: #718096;
  border: 2px solid #e2e8f0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.loader {
  text-align: center;
  font-size: 1.2rem;
  color: #718096;
  padding: 4rem;
}
</style>
