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
    isLoading.value = true;
    try {
      const data: { questions: IQuestion[] } = await $fetch("/api/qa/basic");
      questions.value = data.questions;
    } catch (error) {
    } finally {
      isLoading.value = false;
    }
  };

  const getNextQuestions = async () => {
    try {
      const data: { questions: IQuestion[] } = await $fetch(
        "/api/qa/additional",
        {
          method: "POST",
          body: { answers: answers.value },
        }
      );

      questions.value = data.questions;
      answers.value = {};
    } catch (error) {
    } finally {
      isLoading.value = false;
    }
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
    isLoading,
    initBasicQuestions,
    getNextQuestions,
    generateLabels,
    areAllQuestionsAnswered,
  };
};
