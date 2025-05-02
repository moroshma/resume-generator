export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { BASE_HOST } = useRuntimeConfig();

  try {
    const response = await fetch(
      `${BASE_HOST}/user_service/api/v001/auth/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          login: body.login,
          password: body.password,
        }),
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
