export default defineEventHandler(async (event) => {
  const { BASE_HOST } = useRuntimeConfig();

  try {
    const response = await fetch(
      `${BASE_HOST}/user_service/api/v001/auth/logout`,
      {
        method: "DELETE",
        headers: {
          ...(event.context.cookies && { cookie: event.context.cookies }),
          "Content-Type": "application/json",
        },
      }
    );

    return response;
  } catch (error) {
    setResponseStatus(event, 500);
    return {
      error: "Internal Server Error",
      details: error instanceof Error ? error.message : String(error),
    };
  }
});
