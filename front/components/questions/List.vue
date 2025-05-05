<script setup lang="ts">
const props = defineProps<{
  draft: IDraft;
  error: Error | undefined | any;
  loading: ILoading;
}>();

const isLoadingQuestions = computed(() => props.loading.isLoadingQuestions);

const loadingCardCount = 5;

const hasValidationError = computed(
  () => props.error?.name == "ValidationError"
);
const serverError = computed(
  () => !!props.error?.response?.status && props.error.response.status >= 500
);
console.log(serverError, "serverError");

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
    <div v-if="serverError" class="server-error-card" role="alert">
      <h3 class="error-title">Ошибка сервера</h3>
      <p>
        Не удалось загрузить вопросы. Пожалуйста, попробуйте обновить страницу
        позже или свяжитесь с поддержкой.
      </p>
    </div>
    <div class="questions-container" v-else-if="isLoadingQuestions">
      <div
        style="height: 250px"
        class="question-card loading"
        v-for="index in loadingCardCount"
      ></div>
    </div>
    <div
      v-else
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

.server-error-card {
  background-color: rgba(209, 36, 45, 0.05);
  border: 1px solid var(--main-red);
  border-radius: 16px;
  padding: 2rem 2.5rem;
  color: var(--main-red);
  box-shadow: var(--shadow-xl);
  text-align: center;
}

.server-error-card .error-title {
  color: var(--main-red);
  font-size: 1.6rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.server-error-card p {
  font-size: 1rem;
  line-height: 1.5;
  color: #c81e26;
}

.question-card.loading,
.label-card.loading {
  background-image: linear-gradient(
    -74deg,
    transparent 25%,
    var(--main-green) 50%,
    transparent 75%
  );

  background-size: 200% 100%;

  animation: loading-smooth 2s linear infinite;

  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  height: 250px;
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
  gap: 2rem;
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
}
</style>
