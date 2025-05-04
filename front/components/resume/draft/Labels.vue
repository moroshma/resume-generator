<template>
  <div>
    <div v-if="incorrectlyError" class="error-state">
      <h2 class="error-title">Не удалось создать резюме</h2>
      <p class="error-message">"{{ incorrectlyError.message }}"</p>
      <p class="error-explanation">
        Вероятно, ответы, которые вы дали на предыдущих шагах, были недостаточно
        подробными или некорректными для генерации данных. Пожалуйста,
        попробуйте пройти процесс создания резюме еще раз, предоставив более
        полные ответы.
      </p>
      <ButtonsPrimaryButton text="Начать заново" @click="restartProcess" />
    </div>
    <div v-else-if="loading.isLoadingLabels">
      <div class="labels-list">
        <div
          style="height: 120px"
          v-for="index in 5"
          :key="index"
          class="label-card loading"
        ></div>
      </div>
    </div>

    <div v-else class="labels-container">
      <div class="labels_editor">
        <div
          class="labels-list"
          v-if="props.draft.labels && props.draft.labels.length > 0"
        >
          <div
            v-for="label in props.draft.labels"
            :key="label.label"
            class="label-card"
          >
            <h3 class="label-title">{{ label.label }}</h3>
            <EditableField
              v-model="label.value"
              class="label-answer"
              placeholder="Введите ваш ответ"
            />
          </div>
        </div>
        <div class="feedback-section">
          <textarea
            v-model="feedback"
            class="feedback-input"
            placeholder="Опишите, что нужно изменить или улучшить в сгенерированных лейблах..."
          />
        </div>

        <div class="actions" v-if="feedback.trim()">
          <ButtonsPrimaryButton
            text="Перегенерировать лейблы"
            @click="handleRegenerate"
          />
        </div>
      </div>
      <div class="pdf">
        <ResumeDraftPdfPreview
          :isLoading="false"
          :error="null"
          :isSaving="false"
          :pdfFile="props.draft.pdf"
          @save="save"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useResume } from "~/composables/resume/useResume";
import { IncorrectlyInputError } from "~/utils/errors/IncorrectlyInputError";

const props = defineProps<{
  draft: IDraft;
  error: Error | undefined;
  loading: ILoading;
}>();

const emit = defineEmits<{ regenerate: [string] }>();

const incorrectlyError = computed(() =>
  props.error instanceof IncorrectlyInputError ? props.error : undefined
);

const { saveResume } = useResume();

async function save() {
  if (!props.draft.pdf) throw new Error("Резюме еще не сгенерировалось");
  saveResume(props.draft.pdf);
}

const feedback = ref("");
const isRegenerating = ref(false);
const handleRegenerate = async () => {
  emit("regenerate", feedback.value);
};

const restartProcess = async () => {
  navigateTo("/resume", { external: true });
};
</script>

<style scoped>
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
.labels-container {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.labels-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 3rem;
}

.label-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  width: 100%;
}

.label-title {
  color: #0f172a;
  font-size: 1.1rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.label-answer {
  font-size: 1rem;
  color: #334155;
}

.feedback-section {
  margin: 3rem 0;
}

.feedback-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  min-height: 100px;
  resize: vertical;
  font-family: inherit;
  color: #334155;
}

.feedback-input:focus {
  outline: none;
  border-color: #94a3b8;
  box-shadow: 0 0 0 3px rgba(148, 163, 184, 0.2);
}

.actions {
  display: flex;
  justify-content: flex-end;
}
</style>
