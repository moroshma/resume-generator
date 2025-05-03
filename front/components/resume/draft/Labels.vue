<template>
  <div class="labels-container">
    <div class="labels_editor">
      <div class="labels-list">
        <div
          v-for="label in props.draft.labels"
          :key="label.label"
          class="label-item"
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
          :loading="isRegenerating"
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
</template>

<script setup lang="ts">
import { useResume } from "~/composables/resume/useResume";

const props = defineProps<{ draft: IDraft }>();

const { saveResume } = useResume();
console.log(props.draft);

async function save() {
  if (!props.draft.pdf) throw new Error("Резюме еще не сгенерировалось");
  saveResume(props.draft.pdf);
}

const feedback = ref("");
const isRegenerating = ref(false);

const handleRegenerate = async () => {};
</script>

<style scoped>
.labels-container {
  display: flex;
  flex-direction: column;
  align-items: center;
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
