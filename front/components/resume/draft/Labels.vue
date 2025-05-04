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

    <div v-else class="labels-container">
      <div class="labels_editor">
        <div class="labels-list" v-if="!loading.isLoadingLabels">
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
        <div v-else>
          <div class="labels-list">
            <div
              style="height: 120px"
              v-for="index in 5"
              :key="index"
              class="label-card loading"
            ></div>
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
          :isLoading="Boolean(loading.isLoadingLabels)"
          :error="null"
          :isSaving="false"
          :pdfFile="props.draft.pdf"
          @save="openSaveModal"
        />
      </div>
    </div>
    <div v-if="isModalVisible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3 class="modal-title">Сохранить резюме</h3>
        <p class="modal-prompt">Введите название для вашего резюме:</p>
        <input
          v-model="resumeName"
          type="text"
          class="modal-input"
          placeholder="Например, Резюме Frontend Developer"
          ref="resumeNameInput"
        />
        <div class="modal-actions">
          <button @click="closeModal" class="modal-button cancel">
            Отмена
          </button>
          <button
            @click="confirmSave"
            class="modal-button save"
            :disabled="!resumeName.trim()"
          >
            Сохранить
          </button>
        </div>
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

const isModalVisible = ref(false);
const resumeName = ref("");
const resumeNameInput = ref<HTMLInputElement | null>(null);

const { saveResume } = useResume();

async function openSaveModal() {
  if (!props.draft.pdf) {
    console.error("Резюме еще не сгенерировалось");
    // Optionally show a user-friendly error message here
    return;
  }
  resumeName.value = ""; // Clear previous name
  isModalVisible.value = true;
  // Focus the input field when the modal opens
  await nextTick(); // Wait for the DOM to update
  resumeNameInput.value?.focus();
}

function closeModal() {
  isModalVisible.value = false;
}

async function confirmSave() {
  if (!props.draft.pdf) {
    console.error("PDF data missing during confirmSave");
    closeModal();
    return; // Should not happen if openSaveModal checks, but good practice
  }
  const nameToSave = resumeName.value.trim();
  if (!nameToSave) {
    // Maybe add visual feedback to the input field
    console.warn("Resume name cannot be empty");
    resumeNameInput.value?.focus(); // Keep focus on input
    return; // Don't close modal, don't save
  }

  try {
    // Call the updated saveResume function with the name
    await saveResume(props.draft.pdf, nameToSave);
    // Optionally: Show a success message
    console.log(`Resume "${nameToSave}" saved successfully.`);
  } catch (error) {
    console.error("Failed to save resume:", error);
    // Optionally: Show an error message to the user within the modal or after closing
  } finally {
    closeModal(); // Close modal after attempting to save
  }
}

const feedback = ref("");
const isRegenerating = ref(false);
const handleRegenerate = async () => {
  emit("regenerate", feedback.value);
  feedback.value = "";
};

const restartProcess = async () => {
  navigateTo("/resume", { external: true });
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6); /* Semi-transparent background */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Ensure it's on top */
  padding: 1rem;
}

.modal-content {
  background-color: #ffffff; /* Or your desired background color */
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 450px; /* Adjust max-width as needed */
  display: flex;
  flex-direction: column;
  gap: 1rem; /* Spacing between elements */
}

.modal-title {
  color: #0f172a; /* Match your theme */
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-align: center;
}

.modal-prompt {
  color: #334155; /* Match your theme */
  font-size: 1rem;
  margin-bottom: 1rem;
  text-align: center;
}

.modal-input {
  max-width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #e2e8f0; /* Match your theme's border color */
  border-radius: 8px;
  font-size: 1rem;
  color: #334155; /* Match your theme */
}

.modal-input:focus {
  outline: none;
  border-color: var(--main-green, #17837b); /* Use your theme color */
  box-shadow: 0 0 0 3px rgba(23, 131, 123, 0.2); /* Adjust color/opacity */
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-button {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, opacity 0.2s ease;
  font-size: 0.95rem;
}

.modal-button.save {
  background-color: var(--main-green, #17837b); /* Use your theme color */
  color: white;
}

.modal-button.save:hover {
  background-color: var(
    --main-green-dark,
    #11665f
  ); /* Darker shade for hover */
}

.modal-button.save:disabled {
  background-color: #e2e8f0; /* Disabled style */
  color: #a0aec0;
  cursor: not-allowed;
  opacity: 0.7;
}

.modal-button.cancel {
  background-color: transparent;
  color: #718096; /* Match your theme's secondary text color */
  border: 2px solid #e2e8f0; /* Match your theme's border color */
}

.modal-button.cancel:hover {
  background-color: #f8fafc; /* Slight background on hover */
  border-color: #cbd5e1;
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
