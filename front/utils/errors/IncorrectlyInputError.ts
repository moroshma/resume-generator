export class IncorrectlyInputError extends Error {
  constructor(
    message = "Некорректно заполнены ответы на вопросы",
    ...params: any
  ) {
    super(message, ...params);

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, IncorrectlyInputError);
    }

    this.name = "IncorrectlyInputError";
  }
}
