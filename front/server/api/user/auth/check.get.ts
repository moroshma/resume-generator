export default defineEventHandler(async (event) => {
  const { BASE_HOST } = useRuntimeConfig();

  const response = await fetch(
    `${BASE_HOST}/user_service/api/v001/auth/check`,
    {
      headers: {
        ...(event.context.cookies && { cookie: event.context.cookies }),
      },
    }
  );

  return response.status;
});
