export default defineEventHandler(async (event) => {
  const { BASE_HOST } = useRuntimeConfig();

  try {
    const response = await fetch(
      `${BASE_HOST}/user_service/api/v001/auth/refresh`,
      {
        headers: {
          ...(event.context.cookies && { cookie: event.context.cookies }),
        },
      }
    );

    return response;
  } catch (error: any) {
    const statusCode = error.statusCode || 500;

    throw createError({
      statusCode,
      data: {
        code: error.code || "API_ERROR",
        message: error.message,
      },
    });
  }
});
