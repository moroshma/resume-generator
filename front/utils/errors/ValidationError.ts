export class ValidationError extends Error {
  constructor(
    message = "Не заполнены или неправильно заполнены поля",
    ...params: any
  ) {
    super(message, ...params);

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ValidationError);
    }

    this.name = "ValidationError";
  }
}
