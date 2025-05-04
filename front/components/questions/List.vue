<script setup lang="ts">
const props = defineProps<{ draft: IDraft }>();

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

console.log(props.draft);
</script>

<template>
  <div class="questions-container">
    <div v-for="question in questions" :key="question" class="question-card">
      <h3 class="question-title">{{ question }}</h3>
      <QuestionsAnswerField
        v-model="answers[question]"
        :placeholder="question"
      />
    </div>
  </div>
</template>

<style scoped>
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
