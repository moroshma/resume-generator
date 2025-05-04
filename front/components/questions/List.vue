<script setup lang="ts">
const props = defineProps<{ draft: IDraft; error: Error | undefined }>();

const hasValidationError = computed(
  () => props.error?.name == "ValidationError"
);
const countAnime = computed(() => (firstNotValidquestion.value <= 5 ? 4 : 2));

const questionsRef = ref<HTMLElement[]>();

const firstNotValidquestion = computed(() => {
  if (!questions.value) return 0;
  for (let i = 0; i < questions.value.length; i++) {
    const question = questions.value[i];
    if (!filled(question)) return i;
  }

  return 0;
});

const questions = computed(() => {
  const stepId = props.draft.step.id;
  if (stepId === 1) {
    return props.draft.baseQuestions;
  } else if (stepId === 2) {
    return props.draft.generatedQuestions;
  }
});

const answers = computed(() => {
  const stepId = props.draft.step.id;
  if (stepId === 1) {
    return props.draft.answersToBasicQuestions;
  } else if (stepId === 2) {
    return props.draft.answersToGeneratedQuestions;
  } else {
    return {};
  }
});

function filled(question: IQuestion) {
  const answer = answers.value[question];
  return answer && String(answer).trim();
}

watch(hasValidationError, () => {
  if (!isNaN(firstNotValidquestion.value) && questionsRef.value)
    questionsRef.value[firstNotValidquestion.value].scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
});
</script>

<template>
  <div class="questions-container">
    <div
      ref="questionsRef"
      v-for="question in questions"
      :key="question"
      class="question-card"
      :class="!filled(question) && hasValidationError ? 'not-valid' : ''"
    >
      <h3 class="question-title">{{ question }}</h3>
      <QuestionsAnswerField v-model="answers[question]" placeholder="|" />
    </div>
  </div>
</template>

<style scoped>
@keyframes shake {
  0% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(3deg);
  }
  50% {
    transform: rotate(-3deg);
  }
  75% {
    transform: rotate(3deg);
  }
  100% {
    transform: rotate(0deg);
  }
}

.question-card.not-valid {
  animation: shake 0.4s ease-in-out v-bind(countAnime);

  transform-origin: center center;
}

.question-card.not-valid h3 {
  color: var(--main-red);
}

.questions-container {
  display: flex;
  flex-direction: column;
  gap: 50px;
}

.question-card {
  background: rgb(245, 251, 245);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.question-title {
  color: #2d3748;
  font-size: 1.5rem;
  margin-bottom: 2rem;
}
</style>
