export class ValidationError extends Error {
  constructor(message = "bar", ...params: any) {
    super(message, ...params);

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ValidationError);
    }

    this.name = "ValidationError";
  }
}
