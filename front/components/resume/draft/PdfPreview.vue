<template>
  <div class="pdf-preview-container">
    <h2>Предпросмотр и сохранение</h2>
    <div v-if="isLoading" class="loading-state">Генерация PDF...</div>
    <div v-else-if="error" class="error-state">
      Ошибка генерации PDF: {{ error.message }}
      <ButtonsPrimaryButton
        @click="emit('regeneratePdf')"
        text="Попробовать снова"
      />
    </div>
    <div v-else-if="pdfUrl" class="preview-area">
      <iframe :src="pdfUrl" type="application/pdf" width="100%" height="1000px">
        <p>
          Ваш браузер не поддерживает отображение PDF.
          <a :href="pdfUrl" target="_blank" download="resume_preview.pdf"
            >Скачать PDF</a
          >
        </p>
      </iframe>
      <div class="preview-actions">
        <ButtonsPrimaryButton
          text="Сохранить резюме"
          :loading="isSaving"
          @click="emit('save')"
        />
      </div>
    </div>
    <div v-else class="loading-state">PDF еще не сгенерирован.</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  pdfFile: File | undefined;
  isLoading: boolean;
  isSaving: boolean;
  error: Error | null;
}>();

const pdfUrl = computed(() => {
  if (props.pdfFile) {
    return URL.createObjectURL(props.pdfFile);
  }
});

const emit = defineEmits<{
  (e: "save"): void;
  (e: "regeneratePdf"): void;
  (e: "backToLabels"): void; // Event to trigger step change
}>();
</script>

<style scoped>
.pdf-preview-container {
  width: 100%;
}
.preview-area {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden; /* Hide iframe borders */
  margin-top: 1.5rem;
}
iframe {
  display: block; /* Remove potential bottom space */
  border: none;
}
.preview-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
}
.loading-state,
.error-state {
  text-align: center;
  padding: 4rem;
  color: #64748b;
}
.secondary-btn {
  padding: 0.75rem 1.4rem;
  border-radius: 8px;
  background-color: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: background-color 0.2s;
}
.secondary-btn:hover:not(:disabled) {
  background-color: #e2e8f0;
}
</style>
