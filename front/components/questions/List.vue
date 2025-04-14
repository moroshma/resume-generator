<script setup>
defineProps({
  draft: Object,
});
</script>

<template>
  <div class="questions-container">
    <div
      v-for="question in draft.questions"
      :key="question.id"
      class="question-card"
    >
      <h3 class="question-title">{{ question.text }}</h3>
      <QuestionsAnswerField
        v-model="draft.answers[question.id]"
        :placeholder="question.placeholder"
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
