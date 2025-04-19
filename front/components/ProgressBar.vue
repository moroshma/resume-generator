<template>
  <div class="circular-progress-container" :class="[alignment]">
    <div class="progress-wrapper">
      <svg class="progress-circle" :width="size" :height="size">
        <circle
          class="progress-background"
          :cx="center"
          :cy="center"
          :r="radius"
        />
        <circle
          class="progress-step"
          :cx="center"
          :cy="center"
          :r="radius"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="stepProgressOffset"
        />

        <circle
          v-if="showQuestionsLevel"
          class="progress-questions"
          :cx="center"
          :cy="center"
          :r="radius - 9"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="questionsProgressOffset"
        />
      </svg>

      <div class="progress-info">
        <div class="step-info">
          Шаг {{ currentStep
          }}<span class="total-steps">/{{ totalSteps }}</span>
        </div>
        <div v-if="showQuestionsLevel" class="questions-info">
          {{ answeredQuestions }}/{{ totalQuestions }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps({
  currentStep: { type: Number, default: 1 },
  totalSteps: { type: Number, default: 1 },
  answeredQuestions: { type: Number, default: 0 },
  totalQuestions: { type: Number, default: 0 },
  size: { type: Number, default: 120 },
  alignment: { type: String, default: "right" },
});

const showQuestionsLevel = computed(() => props.totalQuestions > 0);

const center = computed(() => props.size / 2);
const radius = computed(() => props.size / 2 - 8);
const circumference = computed(() => 2 * Math.PI * radius.value);

const stepProgress = computed(
  () => (props.currentStep - 1) / (props.totalSteps - 1)
);
const stepProgressOffset = computed(
  () => circumference.value * (1 - stepProgress.value)
);

const questionsProgress = computed(
  () => props.answeredQuestions / props.totalQuestions
);
const questionsProgressOffset = computed(
  () => circumference.value * (1 - questionsProgress.value)
);
</script>

<style scoped>
.circular-progress-container {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  padding: 20px;

  &.left {
    left: 20px;
  }

  &.right {
    right: 20px;
  }
}

.progress-wrapper {
  position: relative;
  display: inline-block;
}

.progress-circle {
  transform: rotate(-90deg);
}

circle {
  fill: none;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease;
}

.progress-background {
  stroke: #f0f0f0;
  stroke-width: 8;
}

.progress-step {
  stroke: var(--main-red);
  stroke-width: 8;
}

.progress-questions {
  stroke: #10b981;
  stroke-width: 4;
}

.progress-info {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.step-info {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;

  .total-steps {
    font-size: 0.8em;
    color: #718096;
  }
}

.questions-info {
  font-size: 0.9rem;
  color: #4a5568;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .circular-progress-container {
    position: static;
    transform: none;
    display: flex;
    justify-content: center;
    padding: 15px 0;

    &.left,
    &.right {
      left: auto;
      right: auto;
    }
  }

  .progress-wrapper {
    transform: scale(0.8);
  }
}
</style>
