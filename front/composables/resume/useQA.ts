export const useQA = () => {
  const questions = ref<any>([]);
  const answers = ref<Record<string, string>>({});
  const labels = ref<any>([]);
  const pdfUrl = ref("");

  const totalQuestions = computed(() => questions.value.length);

  const isLoading = ref(false);

  const initBasicQuestions = async () => {
    const data: any = await $fetch("/api/qa/basic");
    questions.value = data.questions;
  };

  const getNextQuestions = async () => {
    const data: any = await $fetch("/api/qa/additional", {
      method: "POST",
      body: { answers: answers.value },
    });

    questions.value = data.questions;
  };

  const generateLabels = async () => {
    const data: any = await $fetch("/api/qa/labels", {
      method: "POST",
      body: { answers: answers.value },
    });

    labels.value = data;
  };

  return {
    questions,
    answers,
    labels,
    pdfUrl,
    initBasicQuestions,
    getNextQuestions,
    generateLabels,
    isLoading,
    totalQuestions,
  };
};
