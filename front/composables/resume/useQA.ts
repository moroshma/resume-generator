export const useQA = () => {
  const questions = ref<IQuestion[]>([]);
  const answers = ref<Record<string, string>>({});
  const labels = ref<ILabel[]>([]);

  const isLoading = ref(false);

  const initBasicQuestions = async () => {
    const data: any = await $fetch("/api/qa/basic");
    questions.value = data.questions;
  };

  const getNextQuestions = async () => {
    console.log(answers.value, "answers.value");

    const data: any = await $fetch("/api/qa/additional", {
      method: "POST",
      body: { answers: answers.value },
    });

    questions.value = data.questions;
  };

  const generateLabels = async () => {
    const data: any = await $fetch("api/labels/generate", {
      method: "POST",
      body: { answers: answers.value },
    });

    labels.value = data;
  };

  return {
    questions,
    answers,
    labels,
    initBasicQuestions,
    getNextQuestions,
    generateLabels,
  };
};
