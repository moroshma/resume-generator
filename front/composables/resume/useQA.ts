export const useQA = () => {
  const questions = ref<IQuestion[]>([]);
  const answers = ref<Record<string, string>>({});
  const labels = ref<ILabel[]>([]);

  const isLoading = ref(false);

  const areAllQuestionsAnswered = (): boolean => {
    for (let i = 0; i < questions.value.length; i++) {
      const question = questions.value[i];
      const answer = answers.value[question];

      if (!answer || !String(answer).trim()) {
        return false;
      }
    }

    return true;
  };

  const initBasicQuestions = async () => {
    const data: { questions: IQuestion[] } = await $fetch("/api/qa/basic");
    questions.value = data.questions;
  };

  const getNextQuestions = async () => {
    const data: { questions: IQuestion[] } = await $fetch(
      "/api/qa/additional",
      {
        method: "POST",
        body: { answers: answers.value },
      }
    );

    questions.value = data.questions;
    answers.value = {};
  };

  const generateLabels = async () => {
    const data: ILabel[] = await $fetch("api/labels/generate", {
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
    areAllQuestionsAnswered,
  };
};
