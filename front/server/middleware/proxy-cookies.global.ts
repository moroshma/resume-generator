export default defineEventHandler(async (event) => {
  const incomingCookies = getHeader(event, "cookie");

  event.context.cookies = incomingCookies;
});
