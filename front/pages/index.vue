<template>
  <div class="unauth-container">
    <main class="content">
      <div class="hero-card">
        <h1 class="title">Добро пожаловать!</h1>
        <p class="subtitle">
          Создавайте профессиональные резюме и управляйте ими в одном месте
        </p>

        <div class="features">
          <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <h3>AI-оптимизация содержания</h3>
            <p>Автоматический анализ и улучшение текста резюме</p>
          </div>

          <div class="feature-item">
            <div class="feature-icon">💼</div>
            <h3>Экспорт в PDF</h3>
            <p>Сохраняйте готовые резюме в удобном формате</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🔒</div>
            <h3>Безопасное хранение</h3>
            <p>Ваши данные защищены современными технологиями</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.profile-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  color: #0f172a;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.profile-btn:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.profile-icon {
  width: 1.25rem;
  height: 1.25rem;
  fill: #0f172a;
}

.content {
  max-width: 1200px;
  margin: 3rem auto;
  padding: 0 1.5rem;
}

.hero-card {
  background: white;
  padding: 4rem 2rem;
  border-radius: 1.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.title {
  font-size: 2.5rem;
  color: #0f172a;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.125rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto 3rem;
}

.auth-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 4rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 2rem;
}

.feature-item {
  padding: 2rem;
  background: #f8fafc;
  border-radius: 1rem;
  transition: transform 0.2s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.feature-item h3 {
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.feature-item p {
  color: #64748b;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .auth-actions {
    flex-direction: column;
  }

  .title {
    font-size: 2rem;
  }

  .features {
    grid-template-columns: 1fr;
  }
}
</style>
